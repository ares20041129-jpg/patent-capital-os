#!/usr/bin/env python3
"""Validate generated receipt-capture benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_receipt_capture
import validate_receipt_capture_benchmark


REFERENCE_DELTA_FIELDS = [
    "application_materials_hash",
    "reference_patent_delta_hash",
    "reference_delta_rows_count",
    "reference_delta_claim_elements_count",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_path(data: dict, dotted: str):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    ok, errs, warns = validate_receipt_capture_benchmark.validate(benchmark_dir)
    if not ok:
        errors.extend(errs)
    warnings.extend(warns)

    source_path = benchmark_dir / "receipt-capture-source.json"
    receipt_path = benchmark_dir / "receipt-capture.yaml"
    status_path = benchmark_dir / "filing-status.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    source = load_json(source_path) if source_path.exists() else {}
    receipt = validate_receipt_capture.load_packet(receipt_path) if receipt_path.exists() else {}
    status = load_json(status_path) if status_path.exists() else {}

    if not source_path.exists():
        errors.append(f"missing_file: {source_path}")
    else:
        if source.get("benchmark_mock") is not True:
            errors.append("generated_receipt_benchmark_source_must_be_marked_mock")
        if get_path(source, "decision.status") != "official_receipt_received":
            errors.append("source_decision_must_be_official_receipt_received")

    if source and status:
        if source.get("case_id") != status.get("case_id"):
            errors.append("source_status_case_id_mismatch")
        if source.get("previous_status") != status.get("previous_status"):
            errors.append("source_status_previous_status_mismatch")
        if get_path(source, "official_receipt.receipt_hash") != status.get("official_receipt_hash"):
            errors.append("source_status_receipt_hash_mismatch")
        if (get_path(source, "application.application_number") or "") != (status.get("application_number") or ""):
            errors.append("source_status_application_number_mismatch")
        if source.get("official_session_authorization_hash") != status.get("official_session_authorization_hash"):
            errors.append("source_status_session_authorization_hash_mismatch")
        if source.get("official_session_reference_hash") != status.get("official_session_reference_hash"):
            errors.append("source_status_session_reference_hash_mismatch")
        if status.get("status") != "official_receipt_received":
            errors.append("status_must_be_official_receipt_received")
        if status.get("benchmark_mock") is not True:
            errors.append("status_benchmark_mock_must_be_true")
        if status.get("generator_official_system_touched") is not False:
            errors.append("status_generator_must_not_touch_official_system")
        if status.get("generator_official_submission_performed") is not False:
            errors.append("status_generator_must_not_perform_official_submission")
        if status.get("evidence_claims_official_receipt_received") is not True:
            errors.append("status_must_record_receipt_as_evidence_claim")
        if status.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer":
            if status.get("external_lawyer_involved") is not False:
                errors.append("ai_self_filing_receipt_status_requires_external_lawyer_false")
            if status.get("ai_self_filing_gate") != "passed":
                errors.append("ai_self_filing_receipt_status_requires_ai_gate_passed")
        if source.get("reference_patent_delta_hash") or status.get("reference_patent_delta_hash"):
            for field in REFERENCE_DELTA_FIELDS:
                if source.get(field) != status.get(field):
                    errors.append(f"source_status_{field}_mismatch")
            if source.get("reference_delta_boundary_preserved") is not True:
                errors.append("source_reference_delta_boundary_must_be_true")
            if status.get("reference_delta_boundary_preserved") is not True:
                errors.append("status_reference_delta_boundary_must_be_true")

    if source and receipt:
        if source.get("official_session_authorization_hash") != receipt.get("official_session_authorization_hash"):
            errors.append("source_receipt_session_authorization_hash_mismatch")
        if source.get("official_session_reference_hash") != receipt.get("official_session_reference_hash"):
            errors.append("source_receipt_session_reference_hash_mismatch")
        if source.get("reference_patent_delta_hash") or receipt.get("reference_patent_delta_hash"):
            for field in REFERENCE_DELTA_FIELDS:
                if source.get(field) != receipt.get(field):
                    errors.append(f"source_receipt_{field}_mismatch")
            if receipt.get("reference_delta_boundary_preserved") is not True:
                errors.append("receipt_reference_delta_boundary_must_be_true")

    if hashes_path.exists():
        ok_hash, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok_hash:
            errors.extend([f"artifact_hashes: {item}" for item in hash_errors])
        warnings.extend([f"artifact_hashes: {item}" for item in hash_warnings])

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
