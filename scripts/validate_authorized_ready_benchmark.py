#!/usr/bin/env python3
"""Validate the positive ready-for-authorized-filing benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_official_channel_preflight
import validate_submission_packet
import validate_filing_status_transition


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    packet_path = benchmark_dir / "submission-packet.json"
    preflight_path = benchmark_dir / "official-channel-preflight.yaml"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "readiness-report.md"

    if not packet_path.exists():
        errors.append(f"missing_file: {packet_path}")
    else:
        ok, packet_errors, packet_warnings = validate_submission_packet.validate(
            validate_submission_packet.load_packet(packet_path),
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"submission_packet: {item}" for item in packet_errors])
        warnings.extend([f"submission_packet: {item}" for item in packet_warnings])

    if not preflight_path.exists():
        errors.append(f"missing_file: {preflight_path}")
    else:
        ok, preflight_errors, preflight_warnings = validate_official_channel_preflight.validate(
            validate_official_channel_preflight.load_packet(preflight_path)
        )
        if not ok:
            errors.extend([f"official_channel_preflight: {item}" for item in preflight_errors])
        warnings.extend([f"official_channel_preflight: {item}" for item in preflight_warnings])

    if not status_path.exists():
        errors.append(f"missing_file: {status_path}")
    else:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status_transition: {item}" for item in status_errors])
        warnings.extend([f"filing_status_transition: {item}" for item in status_warnings])
        if status.get("status") != "ready_for_authorized_filing":
            errors.append("status_must_be_ready_for_authorized_filing")
        if status.get("legal_gate") != "passed":
            errors.append("legal_gate_must_be_passed")
        if status.get("official_system_touched") is not False:
            errors.append("official_system_touched_must_be_false")
        if status.get("official_submission_performed") is not False:
            errors.append("official_submission_performed_must_be_false")
        if status.get("not_filed_yet") is not True:
            errors.append("not_filed_yet_must_be_true")
        if status.get("official_receipt_hash"):
            errors.append("official_receipt_hash_must_be_empty_before_submission")
        if status.get("application_number"):
            errors.append("application_number_must_be_empty_before_submission")

    if not report_path.exists():
        errors.append(f"missing_file: {report_path}")
    else:
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in ["ready_for_authorized_filing", "official submission performed: no", "no official system action"]:
            if needle not in text:
                errors.append(f"readiness_report_missing_text: {needle}")

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
