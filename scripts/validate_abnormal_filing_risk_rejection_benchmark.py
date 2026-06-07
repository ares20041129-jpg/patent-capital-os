#!/usr/bin/env python3
"""Validate abnormal filing risk rejection cases."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import prepare_abnormal_filing_risk_assessment
import validate_abnormal_filing_risk_benchmark
import validate_artifact_hash_manifest


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if not isinstance(cur, dict):
            raise RuntimeError(f"mutation_path_not_object: {dotted}")
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    if not isinstance(cur, dict):
        raise RuntimeError(f"mutation_path_not_object: {dotted}")
    cur[parts[-1]] = value


def apply_mutations(case_dir: Path, mutations: list[dict[str, Any]]) -> None:
    cache: dict[Path, dict[str, Any]] = {}
    for mutation in mutations:
        rel_file = str(mutation.get("file") or "")
        dotted = str(mutation.get("path") or "")
        if not rel_file or not dotted:
            raise RuntimeError("mutation_missing_file_or_path")
        path = case_dir / rel_file
        if path not in cache:
            cache[path] = load_json(path)
        set_path(cache[path], dotted, mutation.get("value"))
    for path, data in cache.items():
        write_json(path, data)


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    cases_path = benchmark_dir / "rejection-cases.json"
    base_dir = benchmark_dir.parent / "abnormal-filing-risk-gate"
    hash_path = benchmark_dir / "artifact-hashes.json"

    if not cases_path.exists():
        return False, [f"missing_file: {cases_path}"], warnings
    if not base_dir.exists():
        return False, [f"missing_base_benchmark: {base_dir}"], warnings

    base_ok, base_errors, base_warnings = validate_abnormal_filing_risk_benchmark.validate(base_dir)
    if not base_ok:
        errors.extend([f"base_abnormal_filing_risk_gate: {item}" for item in base_errors])
    warnings.extend([f"base_abnormal_filing_risk_gate: {item}" for item in base_warnings])

    payload = load_json(cases_path)
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases_must_be_nonempty_list")
        cases = []

    with tempfile.TemporaryDirectory(prefix="abnormal-risk-rejection-") as tmp:
        tmp_root = Path(tmp)
        for case in cases:
            if not isinstance(case, dict):
                errors.append("case_must_be_object")
                continue
            case_id = str(case.get("id") or "")
            expected = case.get("expected_failed_checks")
            mutations = case.get("mutations")
            if not case_id:
                errors.append("case_id_missing")
                continue
            if not isinstance(expected, list) or not expected:
                errors.append(f"{case_id}: expected_failed_checks_missing")
                continue
            if not isinstance(mutations, list) or not mutations:
                errors.append(f"{case_id}: mutations_missing")
                continue

            input_dir = tmp_root / case_id / "input"
            output_dir = tmp_root / case_id / "output"
            shutil.copytree(base_dir, input_dir)
            apply_mutations(input_dir, mutations)
            response, exit_code = prepare_abnormal_filing_risk_assessment.prepare(input_dir, output_dir)
            assessment_path = output_dir / "abnormal-filing-risk-assessment.json"
            assessment = load_json(assessment_path) if assessment_path.exists() else {}
            failed_checks = set(assessment.get("errors") or [])

            if exit_code == 0 or response.get("ok") is True:
                errors.append(f"{case_id}: unsafe_case_unexpectedly_passed")
            if assessment.get("risk_level") == "low":
                errors.append(f"{case_id}: risk_level_must_not_be_low")
            for check_id in expected:
                if str(check_id) not in failed_checks:
                    errors.append(f"{case_id}: missing_expected_failed_check: {check_id}")
            if assessment.get("official_system_touched") is not False:
                errors.append(f"{case_id}: official_system_touched_must_be_false")
            if assessment.get("official_submission_performed") is not False:
                errors.append(f"{case_id}: official_submission_performed_must_be_false")
            if assessment.get("external_lawyer_involved") is not False:
                errors.append(f"{case_id}: external_lawyer_involved_must_be_false")

    if hash_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hash_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {hash_path}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.benchmark_dir)
    result = {"ok": ok, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if ok else "FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
