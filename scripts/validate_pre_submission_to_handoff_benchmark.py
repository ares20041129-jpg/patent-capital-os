#!/usr/bin/env python3
"""Validate the one-command pre-submission-to-handoff benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_pre_submission_handoff_package
import validate_pre_submission_pipeline_benchmark


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    pre_submission_dir = benchmark_dir / "pre-submission-pipeline"
    handoff_dir = benchmark_dir / "pre-submission-handoff-package"
    result_path = benchmark_dir / "pre-submission-to-handoff-result.json"
    report_path = benchmark_dir / "pre-submission-to-handoff-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    pipeline_result_path = pre_submission_dir / "pre-submission-pipeline-result.json"
    handoff_package_path = handoff_dir / "pre-submission-handoff-package.json"
    lifecycle_trace_path = pre_submission_dir / "case-lifecycle-trace" / "case-lifecycle-trace.json"

    if pre_submission_dir.exists():
        ok, errs, warns = validate_pre_submission_pipeline_benchmark.validate(pre_submission_dir)
        if not ok:
            errors.extend([f"pre_submission_pipeline: {item}" for item in errs])
        warnings.extend([f"pre_submission_pipeline: {item}" for item in warns])
    else:
        errors.append(f"missing_dir: {pre_submission_dir}")

    if handoff_dir.exists():
        ok, errs, warns = validate_pre_submission_handoff_package.validate(handoff_dir)
        if not ok:
            errors.extend([f"pre_submission_handoff_package: {item}" for item in errs])
        warnings.extend([f"pre_submission_handoff_package: {item}" for item in warns])
    else:
        errors.append(f"missing_dir: {handoff_dir}")

    result: dict[str, Any] = {}
    pipeline_result: dict[str, Any] = {}
    handoff_package: dict[str, Any] = {}
    if result_path.exists():
        result = load_json(result_path)
        if result.get("ok") is not True:
            errors.append("pre_submission_to_handoff_result_ok_must_be_true")
        if result.get("pipeline_type") != "pre_submission_to_handoff_ai_self_filing_no_external_lawyer":
            errors.append("pre_submission_to_handoff_pipeline_type_invalid")
        if result.get("status") != "approved_for_adapter_execution":
            errors.append("pre_submission_to_handoff_status_must_remain_approved_for_adapter_execution")
        if result.get("decision") != "handoff_ready_no_auto_submit":
            errors.append("pre_submission_to_handoff_decision_must_be_handoff_ready_no_auto_submit")
        if result.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("pre_submission_to_handoff_legal_gate_mode_invalid")
        if result.get("external_lawyer_involved") is not False:
            errors.append("pre_submission_to_handoff_external_lawyer_must_be_false")
        if result.get("pre_submission_lifecycle_gate") != "passed":
            errors.append("pre_submission_to_handoff_lifecycle_gate_must_pass")
        for field in [
            "official_system_touched",
            "official_submission_performed",
            "adapter_execution_performed",
            "automatic_submission_performed",
        ]:
            if result.get(field) is not False:
                errors.append(f"pre_submission_to_handoff_{field}_must_be_false")
        for field in ["lifecycle_trace_hash", "source_pre_submission_hash", "handoff_package_hash"]:
            if not isinstance(result.get(field), str) or not SHA256_RE.fullmatch(str(result.get(field))):
                errors.append(f"pre_submission_to_handoff_hash_invalid: {field}")
        stages = result.get("stages") if isinstance(result.get("stages"), dict) else {}
        validations = result.get("validations") if isinstance(result.get("validations"), dict) else {}
        for name in ["pre_submission_pipeline", "pre_submission_handoff_package"]:
            stage = stages.get(name) if isinstance(stages.get(name), dict) else {}
            validation = validations.get(name) if isinstance(validations.get(name), dict) else {}
            if stage.get("ok") is not True:
                errors.append(f"pre_submission_to_handoff_stage_must_pass: {name}")
            if validation.get("ok") is not True:
                errors.append(f"pre_submission_to_handoff_validation_must_pass: {name}")
    else:
        errors.append(f"missing_file: {result_path}")

    if pipeline_result_path.exists():
        pipeline_result = load_json(pipeline_result_path)
        if result and result.get("source_pre_submission_hash") != sha256_file(pipeline_result_path):
            errors.append("pre_submission_to_handoff_source_pre_submission_hash_mismatch")
        if result and result.get("lifecycle_trace_hash") != pipeline_result.get("lifecycle_trace_hash"):
            errors.append("pre_submission_to_handoff_lifecycle_hash_must_match_pipeline")
        if result and pipeline_result.get("reference_patent_delta_hash"):
            if result.get("reference_patent_delta_hash") != pipeline_result.get("reference_patent_delta_hash"):
                errors.append("pre_submission_to_handoff_reference_delta_hash_mismatch")
    else:
        errors.append(f"missing_file: {pipeline_result_path}")

    if lifecycle_trace_path.exists() and result:
        if result.get("lifecycle_trace_hash") != sha256_file(lifecycle_trace_path):
            errors.append("pre_submission_to_handoff_lifecycle_trace_hash_mismatch")
    elif not lifecycle_trace_path.exists():
        errors.append(f"missing_file: {lifecycle_trace_path}")

    if handoff_package_path.exists():
        handoff_package = load_json(handoff_package_path)
        if result and result.get("handoff_package_hash") != sha256_file(handoff_package_path):
            errors.append("pre_submission_to_handoff_handoff_package_hash_mismatch")
        if result and handoff_package.get("legal_gate_mode") != result.get("legal_gate_mode"):
            errors.append("pre_submission_to_handoff_legal_gate_must_match_handoff")
        if pipeline_result.get("reference_patent_delta_hash"):
            if handoff_package.get("reference_patent_delta_hash") != pipeline_result.get("reference_patent_delta_hash"):
                errors.append("pre_submission_to_handoff_handoff_reference_delta_hash_mismatch")
            if handoff_package.get("reference_delta_boundary_preserved") is not True:
                errors.append("pre_submission_to_handoff_reference_delta_boundary_must_be_preserved")
            for key in ["reference_delta_rows_count", "reference_delta_claim_elements_count"]:
                if handoff_package.get(key) != result.get(key):
                    errors.append(f"pre_submission_to_handoff_reference_delta_count_mismatch: {key}")
    else:
        errors.append(f"missing_file: {handoff_package_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "pre-submission to handoff report",
            "pipeline status: pass",
            "ai self-filing",
            "official system touched: no",
            "official submission performed: no",
            "adapter execution performed: no",
            "automatic submission performed: no",
            "external lawyer involved: no",
            "read-only handoff package",
            "does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number",
        ]:
            if needle not in text:
                errors.append(f"pre_submission_to_handoff_report_missing_text: {needle}")
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
