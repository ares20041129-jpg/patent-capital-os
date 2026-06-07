#!/usr/bin/env python3
"""Validate application-number acceptance mock benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_application_number_evidence
import validate_artifact_hash_manifest
import validate_filing_status_transition


REFERENCE_DELTA_FIELDS = [
    "application_materials_hash",
    "reference_patent_delta_hash",
    "reference_delta_rows_count",
    "reference_delta_claim_elements_count",
]


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    evidence_path = benchmark_dir / "application-number-evidence.json"
    status_path = benchmark_dir / "filing-status.json"
    docket_path = benchmark_dir / "docket-entry.yaml"
    portfolio_path = benchmark_dir / "portfolio-update.json"
    report_path = benchmark_dir / "application-number-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if evidence_path.exists():
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_application_number_evidence.validate(evidence, base_dir=evidence_path.parent)
        if not ok:
            errors.extend([f"application_number_evidence: {item}" for item in errs])
        warnings.extend([f"application_number_evidence: {item}" for item in warns])
        if evidence.get("benchmark_mock") is not True:
            errors.append("application_number_benchmark_must_be_marked_mock")
    else:
        errors.append(f"missing_file: {evidence_path}")

    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"status_transition: {item}" for item in errs])
        warnings.extend([f"status_transition: {item}" for item in warns])
        if status.get("benchmark_mock") is not True:
            errors.append("filing_status_benchmark_must_be_marked_mock")
    else:
        errors.append(f"missing_file: {status_path}")

    if evidence_path.exists() and status_path.exists():
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if evidence.get("case_id") != status.get("case_id"):
            errors.append("evidence_status_case_id_mismatch")
        application = evidence.get("application") if isinstance(evidence.get("application"), dict) else {}
        receipt = evidence.get("official_receipt") if isinstance(evidence.get("official_receipt"), dict) else {}
        if application.get("application_number") != status.get("application_number"):
            errors.append("evidence_status_application_number_mismatch")
        if receipt.get("receipt_hash") != status.get("official_receipt_hash"):
            errors.append("evidence_status_receipt_hash_mismatch")
        if evidence.get("official_session_authorization_hash") != status.get("official_session_authorization_hash"):
            errors.append("evidence_status_session_authorization_hash_mismatch")
        if evidence.get("official_session_reference_hash") != status.get("official_session_reference_hash"):
            errors.append("evidence_status_session_reference_hash_mismatch")
        if evidence.get("reference_patent_delta_hash") or status.get("reference_patent_delta_hash"):
            for field in REFERENCE_DELTA_FIELDS:
                if evidence.get(field) != status.get(field):
                    errors.append(f"evidence_status_{field}_mismatch")
            if evidence.get("reference_delta_boundary_preserved") is not True:
                errors.append("evidence_reference_delta_boundary_must_be_true")
            if status.get("reference_delta_boundary_preserved") is not True:
                errors.append("status_reference_delta_boundary_must_be_true")

    if not docket_path.exists():
        errors.append(f"missing_file: {docket_path}")

    if portfolio_path.exists():
        portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
        if portfolio.get("benchmark_mock") is not True:
            errors.append("portfolio_update_benchmark_must_be_marked_mock")
        if not portfolio.get("application_number"):
            errors.append("portfolio_update_missing_application_number")
    else:
        errors.append(f"missing_file: {portfolio_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "benchmark mock: yes",
            "not a real cnipa application number",
            "not a real acceptance notice",
            "required production evidence",
        ]:
            if needle not in text:
                errors.append(f"application_number_report_missing_text: {needle}")
        if evidence_path.exists():
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            if evidence.get("reference_patent_delta_hash"):
                for needle in [
                    "reference-patent delta hash",
                    "reference delta boundary",
                    "not applicant claim support",
                ]:
                    if needle not in text:
                        errors.append(f"application_number_reference_delta_report_missing_text: {needle}")
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
