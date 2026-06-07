#!/usr/bin/env python3
"""Validate case lifecycle trace benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_case_lifecycle_trace


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    trace_path = benchmark_dir / "case-lifecycle-trace.json"
    report_path = benchmark_dir / "lifecycle-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if trace_path.exists():
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_case_lifecycle_trace.validate(trace, base_dir=benchmark_dir)
        if not ok:
            errors.extend([f"lifecycle_trace: {item}" for item in errs])
        warnings.extend([f"lifecycle_trace: {item}" for item in warns])
        if trace.get("trace_type") == "benchmark_mock":
            stages = trace.get("stages") if isinstance(trace.get("stages"), list) else []
            for index, stage in enumerate(stages, start=1):
                if isinstance(stage, dict) and stage.get("benchmark_mock") is not True:
                    errors.append(f"benchmark_stage_{index}_must_be_marked_mock")
                if trace.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer" and isinstance(stage, dict):
                    if stage.get("generator_official_system_touched") is not False:
                        errors.append(f"ai_self_filing_stage_{index}_generator_must_not_touch_official_system")
                    if stage.get("generator_official_submission_performed") is not False:
                        errors.append(f"ai_self_filing_stage_{index}_generator_must_not_perform_official_submission")
                    if stage.get("official_system_touched") is True and stage.get("evidence_claims_official_system_touched") is not True:
                        errors.append(f"ai_self_filing_stage_{index}_official_touch_must_be_marked_as_evidence_claim")
                    if stage.get("official_submission_performed") is True and stage.get("evidence_claims_official_submission_performed") is not True:
                        errors.append(f"ai_self_filing_stage_{index}_official_submission_must_be_marked_as_evidence_claim")
        expected_final_statuses = (
            {"approved_for_adapter_execution", "submitted_pending_receipt", "official_receipt_received", "accepted_or_application_number_received"}
            if trace.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer"
            else {"accepted_or_application_number_received"}
        )
        if trace.get("final_status") not in expected_final_statuses:
            errors.append("lifecycle_benchmark_final_status_invalid")
    else:
        errors.append(f"missing_file: {trace_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        trace_for_report = json.loads(trace_path.read_text(encoding="utf-8")) if trace_path.exists() else {}
        final_status_needle = f"final status: {trace_for_report.get('final_status') or 'accepted_or_application_number_received'}"
        for needle in [
            "trace type: benchmark_mock",
            final_status_needle,
            "legal gate never skipped: yes",
            "no receipt before submission: yes",
            "no application number before receipt: yes",
            "official session hash consistent: yes",
            "mock evidence marked: yes",
        ]:
            if needle not in text:
                errors.append(f"lifecycle_report_missing_text: {needle}")
        if trace_for_report.get("reference_patent_delta_hash"):
            for needle in [
                "reference patent delta hash:",
                "reference delta boundary preserved: yes",
            ]:
                if needle not in text:
                    errors.append(f"lifecycle_report_missing_text: {needle}")
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
