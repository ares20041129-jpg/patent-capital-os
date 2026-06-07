#!/usr/bin/env python3
"""Validate the production adapter readiness benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_production_adapter_readiness


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    shape_packet = benchmark_dir / "production-shape" / "production-adapter-readiness-packet.json"
    production_ready_dir = benchmark_dir / "production-ready"
    unsafe_packet = benchmark_dir / "unsafe-rejection" / "production-adapter-readiness-packet.json"
    report_path = benchmark_dir / "production-adapter-readiness-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if shape_packet.exists():
        shape = json.loads(shape_packet.read_text(encoding="utf-8"))
        ok, errs, warns = validate_production_adapter_readiness.validate_packet(
            shape,
            allow_production_shape_test=True,
        )
        if not ok:
            errors.extend([f"production_shape: {item}" for item in errs])
        warnings.extend([f"production_shape: {item}" for item in warns])

        strict_ok, strict_errors, _ = validate_production_adapter_readiness.validate_packet(shape)
        if strict_ok:
            errors.append("production_shape_packet_must_fail_strict_adapter_readiness")
        if not any("production_shape_test_not_allowed" in item for item in strict_errors):
            errors.append("production_shape_strict_failure_missing_expected_reason")
    else:
        errors.append(f"missing_file: {shape_packet}")

    production_packets = sorted(production_ready_dir.glob("*.json")) if production_ready_dir.exists() else []
    if not production_packets:
        errors.append(f"missing_production_ready_packets: {production_ready_dir}")
    for packet_path in production_packets:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_production_adapter_readiness.validate_packet(packet)
        if not ok:
            errors.extend([f"production_ready:{packet_path.name}: {item}" for item in errs])
        warnings.extend([f"production_ready:{packet_path.name}: {item}" for item in warns])
        if packet.get("evidence_mode") != "production_adapter_readiness":
            errors.append(f"production_ready:{packet_path.name}: evidence_mode_must_be_production_adapter_readiness")
        if packet.get("decision", {}).get("status") != "production_adapter_ready":
            errors.append(f"production_ready:{packet_path.name}: decision_status_must_be_production_adapter_ready")

    if unsafe_packet.exists():
        unsafe = json.loads(unsafe_packet.read_text(encoding="utf-8"))
        unsafe_ok, unsafe_errors, _ = validate_production_adapter_readiness.validate_packet(unsafe)
        if unsafe_ok:
            errors.append("unsafe_adapter_packet_must_fail_strict_readiness")
        if not any("forbidden_field_present" in item or "bypasses" in item or "flag_must_be_false" in item for item in unsafe_errors):
            errors.append("unsafe_rejection_missing_security_or_bypass_error")
    else:
        errors.append(f"missing_file: {unsafe_packet}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "adapter readiness",
            "strict adapter readiness",
            "strict production packet passes",
            "unsafe adapter must fail",
            "no external lawyer",
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
