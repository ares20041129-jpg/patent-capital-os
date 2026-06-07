#!/usr/bin/env python3
"""Validate generated approved-adapter preflight benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_approved_adapter_benchmark
import validate_artifact_hash_manifest


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    ok, errs, warns = validate_approved_adapter_benchmark.validate(benchmark_dir)
    if not ok:
        errors.extend(errs)
    warnings.extend(warns)

    status_path = benchmark_dir / "filing-status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") != "approved_for_adapter_execution":
            errors.append("status_must_be_approved_for_adapter_execution")
        if status.get("official_system_touched") is not False:
            errors.append("official_system_touched_must_be_false")
        if status.get("official_submission_performed") is not False:
            errors.append("official_submission_performed_must_be_false")
        if status.get("adapter_execution_performed") is not False:
            errors.append("adapter_execution_performed_must_be_false")
        if status.get("official_receipt_hash") or status.get("application_number"):
            errors.append("approved_adapter_preflight_must_not_have_receipt_or_application_number")
        if status.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer":
            if status.get("external_lawyer_involved") is not False:
                errors.append("ai_self_filing_adapter_status_requires_external_lawyer_false")
            if status.get("ai_self_filing_gate") != "passed":
                errors.append("ai_self_filing_adapter_status_requires_ai_gate_passed")
            if status.get("reference_patent_delta_hash") and status.get("reference_delta_boundary_preserved") is not True:
                errors.append("ai_self_filing_adapter_reference_delta_boundary_must_be_true")

    hashes_path = benchmark_dir / "artifact-hashes.json"
    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])

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
