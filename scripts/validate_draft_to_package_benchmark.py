#!/usr/bin/env python3
"""Validate draft-to-filing-package bridge benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_filing_package_manifest
import validate_submission_packet


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    packet_path = benchmark_dir / "submission-authorization-packet.json"
    manifest_path = benchmark_dir / "filing-package-manifest.yaml"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "package-validation-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if packet_path.exists():
        ok, errs, warns = validate_submission_packet.validate(
            validate_submission_packet.load_packet(packet_path),
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"submission_packet: {item}" for item in errs])
        warnings.extend([f"submission_packet: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {packet_path}")

    if manifest_path.exists():
        ok, errs, warns = validate_filing_package_manifest.validate(
            validate_filing_package_manifest.load_packet(manifest_path),
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"filing_package_manifest: {item}" for item in errs])
        warnings.extend([f"filing_package_manifest: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {manifest_path}")

    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") != "package_valid_official_preflight_pending":
            errors.append("status_must_be_package_valid_official_preflight_pending")
        if status.get("legal_gate") != "passed":
            errors.append("legal_gate_must_be_passed")
        if status.get("package_validation") != "passed":
            errors.append("package_validation_must_be_passed")
        if status.get("official_channel_preflight") != "pending":
            errors.append("official_channel_preflight_must_be_pending")
        if status.get("decision") != "do_not_file_until_official_preflight":
            errors.append("decision_must_be_do_not_file_until_official_preflight")
        if status.get("official_submission_performed") is not False:
            errors.append("official_submission_performed_must_be_false")
        if status.get("official_receipt_hash"):
            errors.append("official_receipt_hash_must_be_empty")
        if status.get("application_number"):
            errors.append("application_number_must_be_empty")
        if status.get("final_package_hash") != status.get("reviewed_package_hash"):
            errors.append("status_hash_mismatch_final_vs_reviewed")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        required = [
            "package_valid_official_preflight_pending",
            "official submission performed: no",
            "do not file yet",
            "official-channel preflight",
        ]
        for item in required:
            if item not in text:
                errors.append(f"report_missing_text: {item}")
        forbidden = [
            "official_receipt_received",
            "accepted_or_application_number_received",
        ]
        for item in forbidden:
            if item in text:
                # The report is allowed to list forbidden statuses only as boundary text.
                if "must not use" not in text:
                    errors.append(f"report_contains_forbidden_status_without_boundary: {item}")
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
