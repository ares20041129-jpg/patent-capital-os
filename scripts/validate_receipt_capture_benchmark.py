#!/usr/bin/env python3
"""Validate receipt-capture mock benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_filing_status_transition
import validate_receipt_capture


REFERENCE_DELTA_FIELDS = [
    "application_materials_hash",
    "reference_patent_delta_hash",
    "reference_delta_rows_count",
    "reference_delta_claim_elements_count",
]


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    receipt_path = benchmark_dir / "receipt-capture.yaml"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "receipt-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if receipt_path.exists():
        ok, errs, warns = validate_receipt_capture.validate(
            validate_receipt_capture.load_packet(receipt_path),
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"receipt_capture: {item}" for item in errs])
        warnings.extend([f"receipt_capture: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {receipt_path}")

    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"status_transition: {item}" for item in errs])
        warnings.extend([f"status_transition: {item}" for item in warns])
        if status.get("benchmark_mock") is not True:
            errors.append("receipt_capture_benchmark_must_be_marked_mock")
    else:
        errors.append(f"missing_file: {status_path}")

    if receipt_path.exists() and status_path.exists():
        receipt = validate_receipt_capture.load_packet(receipt_path)
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if receipt.get("official_session_authorization_hash") != status.get("official_session_authorization_hash"):
            errors.append("receipt_status_session_authorization_hash_mismatch")
        if receipt.get("official_session_reference_hash") != status.get("official_session_reference_hash"):
            errors.append("receipt_status_session_reference_hash_mismatch")
        if receipt.get("reference_patent_delta_hash") or status.get("reference_patent_delta_hash"):
            for field in REFERENCE_DELTA_FIELDS:
                if receipt.get(field) != status.get(field):
                    errors.append(f"receipt_status_{field}_mismatch")
            if receipt.get("reference_delta_boundary_preserved") is not True:
                errors.append("receipt_reference_delta_boundary_must_be_true")
            if status.get("reference_delta_boundary_preserved") is not True:
                errors.append("status_reference_delta_boundary_must_be_true")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "benchmark mock: yes",
            "not a real cnipa receipt",
            "not a real filing",
            "evidence required in production",
        ]:
            if needle not in text:
                errors.append(f"report_missing_text: {needle}")
        if status_path.exists():
            status = json.loads(status_path.read_text(encoding="utf-8"))
            if status.get("reference_patent_delta_hash"):
                for needle in [
                    "reference-patent delta hash",
                    "reference delta boundary",
                    "not applicant claim support",
                ]:
                    if needle not in text:
                        errors.append(f"receipt_reference_delta_report_missing_text: {needle}")
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
