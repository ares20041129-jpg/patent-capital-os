#!/usr/bin/env python3
"""Validate adapter execution mock-submitted benchmark artifacts."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

import validate_adapter_execution_result
import validate_artifact_hash_manifest
import validate_filing_adapter_contract
import validate_filing_status_transition
import validate_receipt_capture


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    execution_path = benchmark_dir / "adapter-execution-result.json"
    response_path = benchmark_dir / "filing-adapter-response.json"
    receipt_path = benchmark_dir / "receipt-capture-pending.yaml"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "adapter-execution-report.md"
    audit_path = benchmark_dir / "audit-log-entry.yaml"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if execution_path.exists():
        result = json.loads(execution_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_adapter_execution_result.validate(result, base_dir=benchmark_dir)
        if not ok:
            errors.extend([f"adapter_execution_result: {item}" for item in errs])
        warnings.extend([f"adapter_execution_result: {item}" for item in warns])
        if result.get("benchmark_mock") is not True:
            errors.append("adapter_execution_benchmark_must_be_marked_mock")
        missing_readiness = copy.deepcopy(result)
        missing_readiness.pop("adapter_production_readiness_hash", None)
        missing_ok, missing_errors, _ = validate_adapter_execution_result.validate(missing_readiness, base_dir=benchmark_dir)
        if missing_ok:
            errors.append("adapter_execution_missing_readiness_hash_must_fail")
        if not any("adapter_production_readiness_hash" in item for item in missing_errors):
            errors.append("adapter_execution_missing_readiness_hash_failure_missing_expected_reason")
        missing_session = copy.deepcopy(result)
        missing_session.pop("official_session_authorization_hash", None)
        missing_ok, missing_errors, _ = validate_adapter_execution_result.validate(missing_session, base_dir=benchmark_dir)
        if missing_ok:
            errors.append("adapter_execution_missing_session_hash_must_fail")
        if not any("official_session_authorization_hash" in item for item in missing_errors):
            errors.append("adapter_execution_missing_session_hash_failure_missing_expected_reason")
        missing_session_reference = copy.deepcopy(result)
        missing_session_reference.pop("official_session_reference_hash", None)
        missing_ok, missing_errors, _ = validate_adapter_execution_result.validate(missing_session_reference, base_dir=benchmark_dir)
        if missing_ok:
            errors.append("adapter_execution_missing_session_reference_hash_must_fail")
        if not any("official_session_reference_hash" in item for item in missing_errors):
            errors.append("adapter_execution_missing_session_reference_hash_failure_missing_expected_reason")
        for key, expected_reason in [
            ("adapter_request_hash", "adapter_request_hash_mismatch"),
            ("approved_adapter_preflight_hash", "approved_adapter_preflight_hash_mismatch"),
            ("receipt_capture_plan_hash", "receipt_capture_plan_hash_mismatch"),
            ("audit_log_entry_hash", "audit_log_entry_hash_mismatch"),
            ("docket_entry_hash", "docket_entry_hash_mismatch"),
        ]:
            mutated = copy.deepcopy(result)
            mutated[key] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            bad_ok, bad_errors, _ = validate_adapter_execution_result.validate(mutated, base_dir=benchmark_dir)
            if bad_ok:
                errors.append(f"adapter_execution_{key}_mutation_must_fail")
            if not any(expected_reason in item for item in bad_errors):
                errors.append(f"adapter_execution_{key}_mutation_missing_expected_reason")
        for key, expected_reason in [
            ("official_status_snapshot_hash", "official_status_snapshot_hash_mismatch"),
            ("submitted_file_list_hash", "submitted_file_list_hash_mismatch"),
        ]:
            mutated = copy.deepcopy(result)
            mutated["official_submission_evidence"][key] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            bad_ok, bad_errors, _ = validate_adapter_execution_result.validate(mutated, base_dir=benchmark_dir)
            if bad_ok:
                errors.append(f"adapter_execution_{key}_mutation_must_fail")
            if not any(expected_reason in item for item in bad_errors):
                errors.append(f"adapter_execution_{key}_mutation_missing_expected_reason")
    else:
        errors.append(f"missing_file: {execution_path}")

    if response_path.exists():
        response = json.loads(response_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_adapter_contract.validate_response(response, base_dir=benchmark_dir)
        if not ok:
            errors.extend([f"adapter_response: {item}" for item in errs])
        warnings.extend([f"adapter_response: {item}" for item in warns])
        missing_readiness = copy.deepcopy(response)
        missing_readiness.pop("adapter_production_readiness_hash", None)
        missing_ok, missing_errors, _ = validate_filing_adapter_contract.validate_response(missing_readiness, base_dir=benchmark_dir)
        if missing_ok:
            errors.append("adapter_response_missing_readiness_hash_must_fail")
        if not any("adapter_production_readiness_hash" in item for item in missing_errors):
            errors.append("adapter_response_missing_readiness_hash_failure_missing_expected_reason")
        missing_session = copy.deepcopy(response)
        missing_session.pop("official_session_authorization_hash", None)
        missing_ok, missing_errors, _ = validate_filing_adapter_contract.validate_response(missing_session, base_dir=benchmark_dir)
        if missing_ok:
            errors.append("adapter_response_missing_session_hash_must_fail")
        if not any("official_session_authorization_hash" in item for item in missing_errors):
            errors.append("adapter_response_missing_session_hash_failure_missing_expected_reason")
        missing_session_reference = copy.deepcopy(response)
        missing_session_reference.pop("official_session_reference_hash", None)
        missing_ok, missing_errors, _ = validate_filing_adapter_contract.validate_response(missing_session_reference, base_dir=benchmark_dir)
        if missing_ok:
            errors.append("adapter_response_missing_session_reference_hash_must_fail")
        if not any("official_session_reference_hash" in item for item in missing_errors):
            errors.append("adapter_response_missing_session_reference_hash_failure_missing_expected_reason")
        mutated = copy.deepcopy(response)
        mutated["adapter_execution_result_hash"] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        bad_ok, bad_errors, _ = validate_filing_adapter_contract.validate_response(mutated, base_dir=benchmark_dir)
        if bad_ok:
            errors.append("adapter_response_result_hash_mutation_must_fail")
        if not any("adapter_execution_result_hash_mismatch" in item for item in bad_errors):
            errors.append("adapter_response_result_hash_mutation_missing_expected_reason")
    else:
        errors.append(f"missing_file: {response_path}")

    if execution_path.exists() and response_path.exists():
        result = json.loads(execution_path.read_text(encoding="utf-8"))
        response = json.loads(response_path.read_text(encoding="utf-8"))
        if result.get("case_id") != response.get("case_id"):
            errors.append("adapter_result_response_case_id_mismatch")
        if result.get("final_package_hash") != response.get("final_package_hash"):
            errors.append("adapter_result_response_final_package_hash_mismatch")
        if result.get("reviewed_package_hash") != response.get("reviewed_package_hash"):
            errors.append("adapter_result_response_reviewed_package_hash_mismatch")
        if result.get("adapter_production_readiness_hash") != response.get("adapter_production_readiness_hash"):
            errors.append("adapter_result_response_production_readiness_hash_mismatch")
        if result.get("official_session_authorization_hash") != response.get("official_session_authorization_hash"):
            errors.append("adapter_result_response_session_authorization_hash_mismatch")
        if result.get("official_session_reference_hash") != response.get("official_session_reference_hash"):
            errors.append("adapter_result_response_session_reference_hash_mismatch")
        if response.get("adapter_execution_result") != "adapter-execution-result.json":
            errors.append("adapter_response_result_reference_invalid")
        if result.get("reference_patent_delta_hash"):
            for key in [
                "application_materials_hash",
                "reference_patent_delta_hash",
                "reference_delta_rows_count",
                "reference_delta_claim_elements_count",
            ]:
                if response.get(key) != result.get(key):
                    errors.append(f"adapter_result_response_{key}_mismatch")
            if response.get("reference_delta_boundary_preserved") is not True:
                errors.append("adapter_response_reference_delta_boundary_must_be_true")
            if result.get("reference_delta_boundary_preserved") is not True:
                errors.append("adapter_result_reference_delta_boundary_must_be_true")

    if receipt_path.exists():
        ok, errs, warns = validate_receipt_capture.validate(
            validate_receipt_capture.load_packet(receipt_path),
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"receipt_pending: {item}" for item in errs])
        warnings.extend([f"receipt_pending: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {receipt_path}")

    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"status_transition: {item}" for item in errs])
        warnings.extend([f"status_transition: {item}" for item in warns])
        if status.get("benchmark_mock") is not True:
            errors.append("filing_status_benchmark_must_be_marked_mock")
        if status.get("official_receipt_hash"):
            errors.append("submitted_pending_receipt_must_not_have_receipt_hash")
        if status.get("application_number"):
            errors.append("submitted_pending_receipt_must_not_have_application_number")
        if status.get("production_adapter_readiness") != "passed":
            errors.append("filing_status_requires_production_adapter_readiness_passed")
        if not SHA256_RE.fullmatch(str(status.get("production_adapter_readiness_hash") or "")):
            errors.append("filing_status_requires_production_adapter_readiness_hash")
        if status.get("official_session_authorization") != "passed":
            errors.append("filing_status_requires_official_session_authorization_passed")
        if not SHA256_RE.fullmatch(str(status.get("official_session_authorization_hash") or "")):
            errors.append("filing_status_requires_official_session_authorization_hash")
        if not SHA256_RE.fullmatch(str(status.get("official_session_reference_hash") or "")):
            errors.append("filing_status_requires_official_session_reference_hash")
        if execution_path.exists():
            result = json.loads(execution_path.read_text(encoding="utf-8"))
            if status.get("official_session_reference_hash") != result.get("official_session_reference_hash"):
                errors.append("filing_status_result_session_reference_hash_mismatch")
            if result.get("reference_patent_delta_hash"):
                for key in [
                    "application_materials_hash",
                    "reference_patent_delta_hash",
                    "reference_delta_rows_count",
                    "reference_delta_claim_elements_count",
                ]:
                    if status.get(key) != result.get(key):
                        errors.append(f"filing_status_result_{key}_mismatch")
                if status.get("reference_delta_boundary_preserved") is not True:
                    errors.append("filing_status_reference_delta_boundary_must_be_true")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "benchmark mock: yes",
            "not a real cnipa submission",
            "not a real filing",
            "not a real receipt",
            "next allowed step is receipt capture",
        ]:
            if needle not in text:
                errors.append(f"adapter_execution_report_missing_text: {needle}")
        if execution_path.exists():
            result = json.loads(execution_path.read_text(encoding="utf-8"))
            if result.get("reference_patent_delta_hash"):
                for needle in [
                    "reference-patent delta hash",
                    "reference delta boundary",
                    "not applicant claim support",
                ]:
                    if needle not in text:
                        errors.append(f"adapter_execution_reference_delta_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if audit_path.exists() and execution_path.exists():
        result = json.loads(execution_path.read_text(encoding="utf-8"))
        if result.get("reference_patent_delta_hash"):
            audit = validate_receipt_capture.load_packet(audit_path)
            input_hashes = audit.get("input_hashes")
            for expected, label in [
                (result.get("application_materials_hash"), "application_materials_hash"),
                (result.get("reference_patent_delta_hash"), "reference_patent_delta_hash"),
            ]:
                if not isinstance(input_hashes, list) or expected not in input_hashes:
                    errors.append(f"adapter_execution_audit_missing_input_hash: {label}")

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
