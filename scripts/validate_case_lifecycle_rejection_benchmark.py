#!/usr/bin/env python3
"""Validate lifecycle trace rejection cases."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_case_lifecycle_trace


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    last = parts[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    spec_path = benchmark_dir / "rejection-cases.json"
    report_path = benchmark_dir / "lifecycle-rejection-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if not spec_path.exists():
        return False, [f"missing_file: {spec_path}"], warnings
    spec = load_json(spec_path)

    source_trace_ref = spec.get("source_trace")
    if is_blank(source_trace_ref):
        errors.append("missing_required_field: source_trace")
        source_trace_path = None
    else:
        source_trace_path = (benchmark_dir / str(source_trace_ref)).resolve()
        if not source_trace_path.exists():
            errors.append(f"missing_source_trace: {source_trace_ref}")

    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases_must_be_nonempty_list")

    if errors:
        return False, errors, warnings

    assert source_trace_path is not None
    source_trace = load_json(source_trace_path)
    source_ok, source_errors, source_warnings = validate_case_lifecycle_trace.validate(
        source_trace,
        base_dir=source_trace_path.parent,
    )
    if not source_ok:
        errors.extend([f"source_trace_invalid: {item}" for item in source_errors])
    warnings.extend([f"source_trace: {item}" for item in source_warnings])

    seen_ids: set[str] = set()
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            errors.append(f"case_{index}_must_be_object")
            continue
        case_id = str(case.get("id") or "")
        if is_blank(case_id):
            errors.append(f"case_{index}_missing_required_field: id")
        elif case_id in seen_ids:
            errors.append(f"duplicate_case_id: {case_id}")
        seen_ids.add(case_id)

        mutations = case.get("mutations")
        expected = case.get("expected_error_fragments")
        if not isinstance(mutations, list) or not mutations:
            errors.append(f"{case_id or f'case_{index}'}_mutations_must_be_nonempty_list")
            continue
        if not isinstance(expected, list) or not expected:
            errors.append(f"{case_id or f'case_{index}'}_expected_errors_must_be_nonempty_list")
            continue

        mutated = copy.deepcopy(source_trace)
        for mutation in mutations:
            if not isinstance(mutation, dict) or is_blank(mutation.get("path")):
                errors.append(f"{case_id}_mutation_missing_path")
                continue
            set_path(mutated, str(mutation["path"]), mutation.get("value"))

        ok, rejection_errors, rejection_warnings = validate_case_lifecycle_trace.validate(
            mutated,
            base_dir=source_trace_path.parent,
        )
        warnings.extend([f"{case_id}: {item}" for item in rejection_warnings])
        if ok:
            errors.append(f"{case_id}_must_fail_validation")
            continue
        for fragment in expected:
            if not any(str(fragment) in item for item in rejection_errors):
                errors.append(f"{case_id}_missing_expected_error: {fragment}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "lifecycle rejection gate",
            "session-reference mismatch must fail",
            "artifact hash mismatch must fail",
            "receipt-before-submission must fail",
            "submitted package hash mismatch must fail",
        ]:
            if needle not in text:
                errors.append(f"report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in hash_errors])
        warnings.extend([f"artifact_hashes: {item}" for item in hash_warnings])
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
