#!/usr/bin/env python3
"""Validate generated adapter execution benchmark artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import validate_adapter_execution_benchmark
import validate_artifact_hash_manifest


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_path(data: dict, dotted: str):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_blank(value) -> bool:
    return value is None or value == "" or value == [] or value == {}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_reference(reference, base_dir: Path) -> Path:
    path = Path(str(reference or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def validate_source_file_hash(source: dict, file_key: str, hash_key: str, label: str, base_dir: Path, errors: list[str]) -> None:
    raw_path = get_path(source, file_key)
    expected_hash = get_path(source, hash_key)
    if is_blank(raw_path):
        errors.append(f"source_missing_required_field: {file_key}")
        return
    if is_blank(expected_hash):
        errors.append(f"source_missing_required_field: {hash_key}")
        return
    path = resolve_reference(raw_path, base_dir)
    if not path.exists():
        errors.append(f"source_{label}_file_not_found")
        return
    if sha256_file(path) != expected_hash:
        errors.append(f"source_{label}_hash_mismatch")


def require_generator_boundary(data: dict, label: str, errors: list[str]) -> None:
    if data.get("generator_official_system_touched") is not False:
        errors.append(f"{label}_generator_must_not_touch_official_system")
    if data.get("generator_official_submission_performed") is not False:
        errors.append(f"{label}_generator_must_not_perform_official_submission")
    if "generator_adapter_execution_performed" in data and data.get("generator_adapter_execution_performed") is not False:
        errors.append(f"{label}_generator_must_not_perform_adapter_execution")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    ok, errs, warns = validate_adapter_execution_benchmark.validate(benchmark_dir)
    if not ok:
        errors.extend(errs)
    warnings.extend(warns)

    source_path = benchmark_dir / "adapter-execution-source.json"
    result_path = benchmark_dir / "adapter-execution-result.json"
    response_path = benchmark_dir / "filing-adapter-response.json"
    status_path = benchmark_dir / "filing-status.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if not source_path.exists():
        errors.append(f"missing_file: {source_path}")
        source = {}
    else:
        source = load_json(source_path)
        if get_path(source, "execution.benchmark_mock") is not True:
            errors.append("generated_execution_benchmark_source_must_be_marked_mock")
        if get_path(source, "decision.status") != "submitted_pending_receipt":
            errors.append("generated_execution_source_decision_must_be_submitted_pending_receipt")
        validate_source_file_hash(
            source,
            "execution.official_status_snapshot_file",
            "execution.official_status_snapshot_hash",
            "official_status_snapshot",
            benchmark_dir,
            errors,
        )
        validate_source_file_hash(
            source,
            "execution.submitted_file_list_file",
            "execution.submitted_file_list_hash",
            "submitted_file_list",
            benchmark_dir,
            errors,
        )

    result = load_json(result_path) if result_path.exists() else {}
    response = load_json(response_path) if response_path.exists() else {}
    status = load_json(status_path) if status_path.exists() else {}

    if result:
        require_generator_boundary(result, "result", errors)
    if response:
        require_generator_boundary(response, "response", errors)

    if source and result:
        if source.get("case_id") != result.get("case_id"):
            errors.append("source_result_case_id_mismatch")
        if get_path(source, "adapter.name") != result.get("adapter_name"):
            errors.append("source_result_adapter_name_mismatch")
        if get_path(source, "adapter.version") != result.get("adapter_version"):
            errors.append("source_result_adapter_version_mismatch")
        if get_path(source, "execution.submission_reference") != get_path(result, "official_submission_evidence.submission_reference"):
            errors.append("source_result_submission_reference_mismatch")
        if get_path(source, "execution.official_status_snapshot_hash") != get_path(result, "official_submission_evidence.official_status_snapshot_hash"):
            errors.append("source_result_status_snapshot_hash_mismatch")
        if get_path(source, "execution.official_status_snapshot_file") != get_path(result, "official_submission_evidence.official_status_snapshot_file"):
            errors.append("source_result_status_snapshot_file_mismatch")
        if get_path(source, "execution.submitted_file_list_hash") != get_path(result, "official_submission_evidence.submitted_file_list_hash"):
            errors.append("source_result_file_list_hash_mismatch")
        if get_path(source, "execution.submitted_file_list_file") != get_path(result, "official_submission_evidence.submitted_file_list_file"):
            errors.append("source_result_file_list_file_mismatch")

    if result and response:
        if result.get("approved_adapter_preflight_hash") != response.get("approved_adapter_preflight_hash"):
            errors.append("result_response_approved_preflight_hash_mismatch")
        if result.get("adapter_production_readiness_hash") != response.get("adapter_production_readiness_hash"):
            errors.append("result_response_production_readiness_hash_mismatch")
        if result.get("official_session_authorization_hash") != response.get("official_session_authorization_hash"):
            errors.append("result_response_session_authorization_hash_mismatch")
        if result.get("official_session_reference_hash") != response.get("official_session_reference_hash"):
            errors.append("result_response_session_reference_hash_mismatch")
        if result.get("response_state") != response.get("response_state"):
            errors.append("result_response_state_mismatch")

    if status:
        if status.get("status") != "submitted_pending_receipt":
            errors.append("status_must_be_submitted_pending_receipt")
        if status.get("previous_status") != "approved_for_adapter_execution":
            errors.append("previous_status_must_be_approved_for_adapter_execution")
        if status.get("official_system_touched") is not True:
            errors.append("status_must_record_official_system_touched_from_evidence")
        if status.get("official_submission_performed") is not True:
            errors.append("status_must_record_submission_performed_from_evidence")
        if status.get("adapter_execution_performed") is not True:
            errors.append("status_must_record_adapter_execution_performed_from_evidence")
        if status.get("official_receipt_hash") or status.get("application_number"):
            errors.append("submitted_pending_receipt_must_not_have_receipt_or_application_number")
        if status.get("production_adapter_readiness") != "passed":
            errors.append("status_requires_production_adapter_readiness_passed")
        if result and status.get("production_adapter_readiness_hash") != result.get("adapter_production_readiness_hash"):
            errors.append("status_result_production_readiness_hash_mismatch")
        if status.get("official_session_authorization") != "passed":
            errors.append("status_requires_official_session_authorization_passed")
        if result and status.get("official_session_authorization_hash") != result.get("official_session_authorization_hash"):
            errors.append("status_result_session_authorization_hash_mismatch")
        if result and status.get("official_session_reference_hash") != result.get("official_session_reference_hash"):
            errors.append("status_result_session_reference_hash_mismatch")
        require_generator_boundary(status, "status", errors)
        if status.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer":
            if status.get("external_lawyer_involved") is not False:
                errors.append("ai_self_filing_submitted_status_requires_external_lawyer_false")
            if status.get("ai_self_filing_gate") != "passed":
                errors.append("ai_self_filing_submitted_status_requires_ai_gate_passed")

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
