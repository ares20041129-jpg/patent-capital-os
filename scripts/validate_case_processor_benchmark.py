#!/usr/bin/env python3
"""Validate case-processor dry-run benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_case_record
import validate_filing_adapter_contract
import validate_filing_status_transition


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    case_record_path = benchmark_dir / "case-record.json"
    request_path = benchmark_dir / "filing-adapter-request.json"
    response_path = benchmark_dir / "filing-adapter-response.json"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "processor-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if case_record_path.exists():
        ok, errs, warns = validate_case_record.validate(
            json.loads(case_record_path.read_text(encoding="utf-8"))
        )
        if not ok:
            errors.extend([f"case_record: {item}" for item in errs])
        warnings.extend([f"case_record: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {case_record_path}")

    if request_path.exists():
        ok, errs, warns = validate_filing_adapter_contract.validate_request(
            json.loads(request_path.read_text(encoding="utf-8")),
            base_dir=request_path.parent,
        )
        if not ok:
            errors.extend([f"adapter_request: {item}" for item in errs])
        warnings.extend([f"adapter_request: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {request_path}")

    if response_path.exists():
        ok, errs, warns = validate_filing_adapter_contract.validate_response(
            json.loads(response_path.read_text(encoding="utf-8")),
            base_dir=response_path.parent,
        )
        if not ok:
            errors.extend([f"adapter_response: {item}" for item in errs])
        warnings.extend([f"adapter_response: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {response_path}")

    if status_path.exists():
        ok, errs, warns = validate_filing_status_transition.validate(
            json.loads(status_path.read_text(encoding="utf-8"))
        )
        if not ok:
            errors.extend([f"status_transition: {item}" for item in errs])
        warnings.extend([f"status_transition: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "dry_run",
            "official system touched: no",
            "official submission performed: no",
            "handoff",
        ]:
            if needle not in text:
                errors.append(f"processor_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        warnings.append("artifact_hashes_missing_until_manifest_generated")

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
