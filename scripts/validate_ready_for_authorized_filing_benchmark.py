#!/usr/bin/env python3
"""Validate generated official-channel preflight to ready-for-authorized-filing artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_official_channel_preflight
import validate_official_ready_benchmark


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    ok, errs, warns = validate_official_ready_benchmark.validate(benchmark_dir)
    if not ok:
        errors.extend(errs)
    warnings.extend(warns)

    status_path = benchmark_dir / "filing-status.json"
    preflight_path = benchmark_dir / "official-channel-preflight.yaml"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") != "ready_for_authorized_filing":
            errors.append("status_must_be_ready_for_authorized_filing")
        if status.get("official_system_touched") is not False:
            errors.append("official_system_touched_must_be_false")
        if status.get("official_submission_performed") is not False:
            errors.append("official_submission_performed_must_be_false")
        if status.get("official_receipt_hash") or status.get("application_number"):
            errors.append("ready_status_must_not_have_receipt_or_application_number")
        if status.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer":
            if status.get("external_lawyer_involved") is not False:
                errors.append("ai_self_filing_ready_status_requires_external_lawyer_false")
            if status.get("ai_self_filing_gate") != "passed":
                errors.append("ai_self_filing_ready_status_requires_ai_gate_passed")
            if status.get("application_materials_generation") != "passed":
                errors.append("ai_self_filing_ready_status_requires_application_materials_generation_passed")
            if not str(status.get("application_materials_hash") or "").startswith("sha256:"):
                errors.append("ai_self_filing_ready_status_requires_application_materials_hash")

            if preflight_path.exists():
                preflight = validate_official_channel_preflight.load_packet(preflight_path)
                materials = preflight.get("application_materials") if isinstance(preflight.get("application_materials"), dict) else {}
                if not str(materials.get("hash") or "").startswith("sha256:"):
                    errors.append("ai_self_filing_preflight_requires_application_materials_hash")
                if materials.get("hash") != status.get("application_materials_hash"):
                    errors.append("ai_self_filing_preflight_application_materials_hash_mismatch")
                if materials.get("reference_patent_delta_hash"):
                    if status.get("reference_patent_delta_hash") != materials.get("reference_patent_delta_hash"):
                        errors.append("ai_self_filing_ready_reference_delta_hash_mismatch")
                    if materials.get("reference_delta_boundary_preserved") is not True:
                        errors.append("ai_self_filing_preflight_reference_delta_boundary_must_be_true")
                    if status.get("reference_delta_boundary_preserved") is not True:
                        errors.append("ai_self_filing_ready_reference_delta_boundary_must_be_true")

    report_path = benchmark_dir / "readiness-report.md"
    preflight = validate_official_channel_preflight.load_packet(preflight_path) if preflight_path.exists() else {}
    materials = preflight.get("application_materials") if isinstance(preflight.get("application_materials"), dict) else {}
    if report_path.exists() and materials.get("reference_patent_delta_hash"):
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "reference-patent delta hash",
            "reference delta boundary",
            "not applicant claim support",
        ]:
            if needle not in text:
                errors.append(f"ready_reference_delta_report_missing_text: {needle}")

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
