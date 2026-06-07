#!/usr/bin/env python3
"""Validate AI self-filing rejection when abnormal-risk evidence binding is invalid."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

import prepare_ai_self_filing_package
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
            raise ValueError(f"mutation_parent_not_object: {dotted}")
        cur = cur.setdefault(part, {})
    if not isinstance(cur, dict):
        raise ValueError(f"mutation_target_parent_not_object: {dotted}")
    cur[parts[-1]] = value


def remove_path(data: dict[str, Any], dotted: str) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if not isinstance(cur, dict) or part not in cur:
            return
        cur = cur[part]
    if isinstance(cur, dict):
        cur.pop(parts[-1], None)


def apply_case(base: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    packet = copy.deepcopy(base)
    for dotted in case.get("remove_paths", []):
        remove_path(packet, str(dotted))
    mutations = case.get("mutations") if isinstance(case.get("mutations"), dict) else {}
    for dotted, value in mutations.items():
        set_path(packet, str(dotted), value)
    return packet


def response_errors(response: dict[str, Any]) -> list[str]:
    found: list[str] = []
    for key in ["errors", "source_errors", "draft_errors", "manifest_errors", "status_errors", "hash_errors"]:
        value = response.get(key)
        if isinstance(value, list):
            found.extend(str(item) for item in value)
    return found


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    spec_path = benchmark_dir / "rejection-cases.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    if not spec_path.exists():
        return False, [f"missing_file: {spec_path}"], warnings

    spec = load_json(spec_path)
    base_source_path = Path(str(spec.get("base_source") or ""))
    draft_package_dir = Path(str(spec.get("draft_package_dir") or ""))
    if not base_source_path.is_absolute():
        base_source_path = (benchmark_dir / base_source_path).resolve()
    if not draft_package_dir.is_absolute():
        draft_package_dir = (benchmark_dir / draft_package_dir).resolve()
    if not base_source_path.exists():
        errors.append(f"missing_base_source: {base_source_path}")
    if not draft_package_dir.exists():
        errors.append(f"missing_draft_package_dir: {draft_package_dir}")
    base_source = load_json(base_source_path) if base_source_path.exists() else {}
    assessment_ref = base_source.get("ai_compliance_review", {}).get("abnormal_filing_risk_assessment", {})
    if isinstance(assessment_ref, dict) and assessment_ref.get("artifact_path"):
        artifact_path = Path(str(assessment_ref["artifact_path"]))
        if not artifact_path.is_absolute():
            assessment_ref["artifact_path"] = str((base_source_path.parent / artifact_path).resolve())

    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("rejection_cases_missing")
        cases = []

    with tempfile.TemporaryDirectory(prefix="ai-self-filing-binding-") as tmp:
        tmp_root = Path(tmp)
        for case in cases:
            if not isinstance(case, dict):
                errors.append("rejection_case_must_be_object")
                continue
            case_id = str(case.get("id") or "unnamed_case")
            expected_error = str(case.get("expected_error") or "")
            source = apply_case(base_source, case)
            source_path = tmp_root / f"{case_id}.json"
            output_dir = tmp_root / f"{case_id}-output"
            write_json(source_path, source)
            response, exit_code = prepare_ai_self_filing_package.prepare(draft_package_dir, source_path, output_dir)
            found_errors = response_errors(response)
            if exit_code == 0 or response.get("ok") is True:
                errors.append(f"{case_id}: rejection_case_unexpectedly_passed")
            if expected_error and not any(expected_error in item for item in found_errors):
                errors.append(f"{case_id}: expected_error_not_found: {expected_error}")
            if not expected_error:
                errors.append(f"{case_id}: expected_error_missing")
            if response.get("official_system_touched") is not False:
                errors.append(f"{case_id}: official_system_touched_must_be_false")
            if response.get("official_submission_performed") is not False:
                errors.append(f"{case_id}: official_submission_performed_must_be_false")
            if response.get("external_lawyer_involved") not in (False, None):
                errors.append(f"{case_id}: external_lawyer_involved_must_be_false")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {hashes_path}")

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
