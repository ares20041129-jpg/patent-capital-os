#!/usr/bin/env python3
"""Validate the production official evidence gate benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_production_official_evidence_gate


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    shape_packet = benchmark_dir / "production-shape" / "production-official-evidence-packet.json"
    mock_packet = benchmark_dir / "mock-rejection" / "production-official-evidence-packet.json"
    report_path = benchmark_dir / "production-official-evidence-gate-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if not shape_packet.exists():
        errors.append(f"missing_file: {shape_packet}")
    else:
        ok, errs, warns = validate_production_official_evidence_gate.validate_packet(
            shape_packet,
            allow_production_shape_test=True,
        )
        if not ok:
            errors.extend([f"production_shape: {item}" for item in errs])
        warnings.extend([f"production_shape: {item}" for item in warns])

        strict_ok, strict_errors, _ = validate_production_official_evidence_gate.validate_packet(shape_packet)
        if strict_ok:
            errors.append("production_shape_packet_must_fail_strict_production_gate")
        if not any("production_shape_test_not_allowed" in item for item in strict_errors):
            errors.append("production_shape_strict_failure_missing_expected_reason")

    if not mock_packet.exists():
        errors.append(f"missing_file: {mock_packet}")
    else:
        mock_ok, mock_errors, _ = validate_production_official_evidence_gate.validate_packet(mock_packet)
        if mock_ok:
            errors.append("mock_evidence_packet_must_fail_strict_production_gate")
        if not any("benchmark_mock" in item or "mock" in item for item in mock_errors):
            errors.append("mock_rejection_missing_benchmark_mock_error")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "strict production gate",
            "mock evidence must fail",
            "shape test is not real official evidence",
            "no external lawyer",
            "reference delta boundary preserved",
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
