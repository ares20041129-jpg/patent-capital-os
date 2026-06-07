#!/usr/bin/env python3
"""Validate official-channel-preflight-to-ready benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_filing_status_transition
import validate_official_channel_preflight
import validate_receipt_capture


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    preflight_path = benchmark_dir / "official-channel-preflight.yaml"
    receipt_plan_path = benchmark_dir / "receipt-capture-plan.yaml"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "readiness-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if preflight_path.exists():
        ok, errs, warns = validate_official_channel_preflight.validate(
            validate_official_channel_preflight.load_packet(preflight_path)
        )
        if not ok:
            errors.extend([f"official_channel_preflight: {item}" for item in errs])
        warnings.extend([f"official_channel_preflight: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {preflight_path}")

    if receipt_plan_path.exists():
        ok, errs, warns = validate_receipt_capture.validate(
            validate_receipt_capture.load_packet(receipt_plan_path),
            allow_plan_only=True,
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"receipt_capture_plan: {item}" for item in errs])
        warnings.extend([f"receipt_capture_plan: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {receipt_plan_path}")

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
            "ready_for_authorized_filing",
            "official submission performed: no",
            "no filing, payment, signature",
            "submitted_pending_receipt",
        ]:
            if needle not in text:
                errors.append(f"report_missing_text: {needle}")
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
