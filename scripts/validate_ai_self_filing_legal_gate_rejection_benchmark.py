#!/usr/bin/env python3
"""Validate AI self-filing legal gate rejection cases."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import validate_ai_self_filing_authorization
import validate_artifact_hash_manifest


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    cases_path = benchmark_dir / "rejection-cases.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    if not cases_path.exists():
        return False, [f"missing_file: {cases_path}"], warnings

    spec = load_json(cases_path)
    base_path = Path(str(spec.get("base_packet") or ""))
    if not base_path.is_absolute():
        base_path = (benchmark_dir / base_path).resolve()
    if not base_path.exists():
        errors.append(f"missing_base_packet: {base_path}")
        base_packet: dict[str, Any] = {}
    else:
        base_packet = load_json(base_path)
        base_ok, base_errors, base_warnings = validate_ai_self_filing_authorization.validate(base_packet, base_dir=base_path.parent)
        if not base_ok:
            errors.extend([f"base_packet_should_pass: {item}" for item in base_errors])
        warnings.extend([f"base_packet: {item}" for item in base_warnings])

    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("rejection_cases_missing")
        cases = []

    for case in cases:
        if not isinstance(case, dict):
            errors.append("rejection_case_must_be_object")
            continue
        case_id = str(case.get("id") or "unnamed_case")
        expected_error = str(case.get("expected_error") or "")
        packet = apply_case(base_packet, case)
        ok, case_errors, case_warnings = validate_ai_self_filing_authorization.validate(packet, base_dir=base_path.parent)
        warnings.extend([f"{case_id}: {item}" for item in case_warnings])
        if ok:
            errors.append(f"{case_id}: rejection_case_unexpectedly_passed")
        if expected_error and not any(expected_error in item for item in case_errors):
            errors.append(f"{case_id}: expected_error_not_found: {expected_error}")
        if not expected_error:
            errors.append(f"{case_id}: expected_error_missing")

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
