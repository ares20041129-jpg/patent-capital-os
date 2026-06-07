#!/usr/bin/env python3
"""Validate approved-adapter preflight benchmark artifacts."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import validate_approved_adapter_preflight
import validate_artifact_hash_manifest
import validate_filing_adapter_contract
import validate_filing_status_transition


def collect_bad_sha256_strings(value: Any, path: str, errors: list[str], label: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            collect_bad_sha256_strings(child, f"{path}.{key}" if path else str(key), errors, label)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            collect_bad_sha256_strings(child, f"{path}[{index}]", errors, label)
    elif isinstance(value, str) and value.startswith("sha256:"):
        if not validate_approved_adapter_preflight.SHA256_RE.fullmatch(value):
            errors.append(f"{label}:{path}_must_be_exact_sha256")


def require_hash_in_list(values: Any, expected: Any, label: str, errors: list[str]) -> None:
    if not expected:
        return
    if not isinstance(values, list) or expected not in values:
        errors.append(f"audit_plan_missing_input_hash: {label}")


def validate_audit_and_docket_plans(
    benchmark_dir: Path,
    preflight: dict[str, Any] | None,
    errors: list[str],
    warnings: list[str],
) -> None:
    audit_path = benchmark_dir / "audit-log-entry-plan.yaml"
    docket_path = benchmark_dir / "docket-entry-plan.yaml"

    if not audit_path.exists():
        errors.append(f"missing_file: {audit_path}")
        return
    if not docket_path.exists():
        errors.append(f"missing_file: {docket_path}")
        return

    try:
        audit_plan = validate_approved_adapter_preflight.load_packet(audit_path)
        docket_plan = validate_approved_adapter_preflight.load_packet(docket_path)
    except Exception as exc:
        errors.append(f"audit_docket_plan_load_failed: {exc}")
        return

    collect_bad_sha256_strings(audit_plan, "", errors, "audit_plan")
    collect_bad_sha256_strings(docket_plan, "", errors, "docket_plan")

    if preflight:
        package = preflight.get("package") if isinstance(preflight.get("package"), dict) else {}
        official_channel = preflight.get("official_channel") if isinstance(preflight.get("official_channel"), dict) else {}
        session = official_channel.get("session_authorization") if isinstance(official_channel.get("session_authorization"), dict) else {}
        evidence = preflight.get("evidence") if isinstance(preflight.get("evidence"), dict) else {}
        adapter = preflight.get("adapter") if isinstance(preflight.get("adapter"), dict) else {}
        readiness = adapter.get("production_readiness") if isinstance(adapter.get("production_readiness"), dict) else {}
        audit_input_hashes = audit_plan.get("input_hashes")
        for expected, label in [
            (package.get("final_package_hash"), "final_package_hash"),
            (official_channel.get("preflight_hash"), "official_channel_preflight_hash"),
            (evidence.get("receipt_capture_plan_hash"), "receipt_capture_plan_hash"),
            (readiness.get("packet_hash"), "adapter_production_readiness_hash"),
            (session.get("packet_hash"), "official_session_authorization_hash"),
            (session.get("session_reference_hash"), "official_session_reference_hash"),
        ]:
            require_hash_in_list(audit_input_hashes, expected, label, errors)
        materials = preflight.get("application_materials") if isinstance(preflight.get("application_materials"), dict) else {}
        if materials.get("reference_patent_delta_hash"):
            for expected, label in [
                (materials.get("hash"), "application_materials_hash"),
                (materials.get("reference_patent_delta_hash"), "reference_patent_delta_hash"),
            ]:
                require_hash_in_list(audit_input_hashes, expected, label, errors)

    source_hash = docket_plan.get("source_hash")
    if source_hash not in {"", None, "pending", "pending_until_preflight_hash_materialized"}:
        if not (isinstance(source_hash, str) and validate_approved_adapter_preflight.SHA256_RE.fullmatch(source_hash)):
            errors.append("docket_plan_source_hash_must_be_pending_or_exact_sha256")
    if docket_plan.get("related_application_number"):
        errors.append("docket_plan_must_not_have_application_number_before_execution")
    if docket_plan.get("status") != "open":
        warnings.append("docket_plan_status_should_be_open_before_execution")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    preflight_path = benchmark_dir / "approved-adapter-preflight.json"
    request_path = benchmark_dir / "filing-adapter-request.json"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "adapter-boundary-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    rejection_dir = benchmark_dir / "readiness-bypass-rejection"

    if preflight_path.exists():
        ok, errs, warns = validate_approved_adapter_preflight.validate(
            json.loads(preflight_path.read_text(encoding="utf-8")),
            base_dir=preflight_path.parent,
        )
        if not ok:
            errors.extend([f"approved_adapter_preflight: {item}" for item in errs])
        warnings.extend([f"approved_adapter_preflight: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {preflight_path}")

    if request_path.exists():
        request = json.loads(request_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_adapter_contract.validate_request(
            request,
            base_dir=request_path.parent,
        )
        if not ok:
            errors.extend([f"adapter_request: {item}" for item in errs])
        warnings.extend([f"adapter_request: {item}" for item in warns])
        for key, expected_reason in [
            ("approved_adapter_preflight_hash", "approved_adapter_preflight_hash_mismatch"),
            ("adapter_production_readiness_hash", "adapter_production_readiness_packet_hash_mismatch"),
            ("official_session_authorization_hash", "official_session_authorization_packet_hash_mismatch"),
        ]:
            mutated = copy.deepcopy(request)
            mutated[key] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            bad_ok, bad_errors, _ = validate_filing_adapter_contract.validate_request(
                mutated,
                base_dir=request_path.parent,
            )
            if bad_ok:
                errors.append(f"adapter_request_{key}_mutation_must_fail")
            if not any(expected_reason in item for item in bad_errors):
                errors.append(f"adapter_request_{key}_mutation_missing_expected_reason")
    else:
        errors.append(f"missing_file: {request_path}")

    if preflight_path.exists() and request_path.exists():
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        request = json.loads(request_path.read_text(encoding="utf-8"))
        if preflight.get("case_id") != request.get("case_id"):
            errors.append("preflight_request_case_id_mismatch")
        package = preflight.get("package") if isinstance(preflight.get("package"), dict) else {}
        if package.get("final_package_hash") != request.get("final_package_hash"):
            errors.append("preflight_request_final_package_hash_mismatch")
        if package.get("reviewed_package_hash") != request.get("reviewed_package_hash"):
            errors.append("preflight_request_reviewed_package_hash_mismatch")
        materials = preflight.get("application_materials") if isinstance(preflight.get("application_materials"), dict) else {}
        if request.get("application_materials_hash") and materials.get("hash") and request.get("application_materials_hash") != materials.get("hash"):
            errors.append("preflight_request_application_materials_hash_mismatch")
        if materials.get("reference_patent_delta_hash"):
            if request.get("application_materials_hash") != materials.get("hash"):
                errors.append("preflight_request_application_materials_hash_mismatch")
            if request.get("reference_patent_delta_hash") != materials.get("reference_patent_delta_hash"):
                errors.append("preflight_request_reference_patent_delta_hash_mismatch")
            if request.get("reference_delta_boundary_preserved") is not True:
                errors.append("preflight_request_reference_delta_boundary_must_be_true")
        session = preflight.get("official_channel", {}).get("session_authorization", {})
        if session.get("packet_hash") != request.get("official_session_authorization_hash"):
            errors.append("preflight_request_session_authorization_hash_mismatch")
        if session.get("session_reference_hash") != request.get("official_session_reference_hash"):
            errors.append("preflight_request_session_reference_hash_mismatch")
        if session.get("validation_result") != "passed":
            errors.append("preflight_session_authorization_must_pass")

    validate_audit_and_docket_plans(
        benchmark_dir,
        json.loads(preflight_path.read_text(encoding="utf-8")) if preflight_path.exists() else None,
        errors,
        warnings,
    )

    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        if status.get("official_system_touched") is not False:
            errors.append("status_must_not_touch_official_system")
        if status.get("official_submission_performed") is not False:
            errors.append("status_must_not_perform_official_submission")
        if status.get("adapter_execution_performed") is not False:
            errors.append("status_must_not_perform_adapter_execution")
        if status.get("official_session_authorization") != "passed":
            errors.append("status_requires_official_session_authorization_passed")
        if preflight_path.exists():
            preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
            session_hash = preflight.get("official_channel", {}).get("session_authorization", {}).get("packet_hash")
            if status.get("official_session_authorization_hash") != session_hash:
                errors.append("status_preflight_session_authorization_hash_mismatch")
            session_reference_hash = preflight.get("official_channel", {}).get("session_authorization", {}).get("session_reference_hash")
            if status.get("official_session_reference_hash") != session_reference_hash:
                errors.append("status_preflight_session_reference_hash_mismatch")
            materials = preflight.get("application_materials") if isinstance(preflight.get("application_materials"), dict) else {}
            if status.get("application_materials_hash") and materials.get("hash") and status.get("application_materials_hash") != materials.get("hash"):
                errors.append("status_preflight_application_materials_hash_mismatch")
            if materials.get("reference_patent_delta_hash"):
                if status.get("application_materials_hash") != materials.get("hash"):
                    errors.append("status_preflight_application_materials_hash_mismatch")
                if status.get("reference_patent_delta_hash") != materials.get("reference_patent_delta_hash"):
                    errors.append("status_preflight_reference_patent_delta_hash_mismatch")
                if status.get("reference_delta_boundary_preserved") is not True:
                    errors.append("status_reference_delta_boundary_must_be_true")
        if status.get("official_receipt_hash"):
            errors.append("status_must_not_have_official_receipt_hash")
        if status.get("application_number"):
            errors.append("status_must_not_have_application_number")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "execution mode: approved_adapter_preflight",
            "decision: approved_for_adapter_execution",
            "official system touched: no",
            "official submission performed: no",
            "adapter execution performed: no",
        ]:
            if needle not in text:
                errors.append(f"adapter_report_missing_text: {needle}")
        if preflight_path.exists():
            preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
            materials = preflight.get("application_materials") if isinstance(preflight.get("application_materials"), dict) else {}
            if materials.get("reference_patent_delta_hash"):
                for needle in [
                    "reference-patent delta hash",
                    "reference delta boundary",
                    "not applicant claim support",
                ]:
                    if needle not in text:
                        errors.append(f"adapter_reference_delta_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        warnings.append("artifact_hashes_missing_until_manifest_generated")

    if rejection_dir.exists():
        rejection_files = sorted(rejection_dir.glob("*.json"))
        if not rejection_files:
            errors.append(f"readiness_bypass_rejection_missing_json: {rejection_dir}")
        for rejection_path in rejection_files:
            ok, errs, _ = validate_approved_adapter_preflight.validate(
                json.loads(rejection_path.read_text(encoding="utf-8")),
                base_dir=rejection_path.parent,
            )
            if ok:
                errors.append(f"readiness_bypass_rejection_should_fail: {rejection_path.name}")
            if not any("production_readiness" in item for item in errs):
                errors.append(f"readiness_bypass_rejection_missing_expected_reason: {rejection_path.name}")

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
