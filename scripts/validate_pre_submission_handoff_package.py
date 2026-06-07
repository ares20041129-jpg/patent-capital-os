#!/usr/bin/env python3
"""Validate a read-only pre-submission handoff package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_pre_submission_pipeline_benchmark


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED_ROLES = {
    "pre_submission_result",
    "pre_submission_report",
    "application_materials",
    "request_form_metadata",
    "document_generation_plan",
    "claims_material",
    "specification_material",
    "abstract_material",
    "drawings_materials_plan",
    "xml_readiness_checklist",
    "final_claims_xml",
    "final_specification_xml",
    "final_abstract_xml",
    "final_drawings_pdf",
    "final_request_metadata_xml",
    "filing_package_manifest",
    "ai_self_filing_authorization_packet",
    "official_channel_preflight",
    "receipt_capture_plan",
    "approved_adapter_preflight",
    "filing_adapter_request",
    "audit_log_entry_plan",
    "docket_entry_plan",
    "case_lifecycle_trace",
    "lifecycle_report",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def safe_rel_file(root: Path, rel: str) -> Path | None:
    path = Path(rel)
    if path.is_absolute() or ".." in path.parts:
        return None
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def evidence_by_role(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in package.get("evidence_files", []):
        if isinstance(item, dict) and item.get("role"):
            result[str(item["role"])] = item
    return result


def validate(folder: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    package_path = folder / "pre-submission-handoff-package.json"
    report_path = folder / "pre-submission-handoff-report.md"
    hashes_path = folder / "artifact-hashes.json"
    if not package_path.exists():
        return False, [f"missing_file: {package_path}"], warnings

    try:
        package = load_json(package_path)
    except Exception as exc:
        return False, [f"handoff_package_json_invalid: {exc}"], warnings

    for key in [
        "case_id",
        "handoff_package_type",
        "source_pre_submission_dir",
        "source_pre_submission_hash",
        "status",
        "decision",
        "legal_gate_mode",
        "pre_submission_lifecycle_gate",
        "lifecycle_trace_hash",
        "copied_lifecycle_trace_hash",
        "final_package_hash",
        "application_materials_hash",
        "official_material_inventory",
        "evidence_files",
        "handoff_controls",
        "next_action",
    ]:
        if is_blank(package.get(key)):
            errors.append(f"missing_required_field: {key}")

    if package.get("handoff_package_type") != "pre_submission_approved_adapter_execution_handoff":
        errors.append("handoff_package_type_invalid")
    if package.get("status") != "approved_for_adapter_execution":
        errors.append("handoff_status_must_be_approved_for_adapter_execution")
    if package.get("decision") != "handoff_ready_no_auto_submit":
        errors.append("handoff_decision_must_be_no_auto_submit")
    if package.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("handoff_legal_gate_mode_invalid")
    if package.get("external_lawyer_involved") is not False:
        errors.append("handoff_external_lawyer_must_be_false")
    if package.get("pre_submission_lifecycle_gate") != "passed":
        errors.append("handoff_lifecycle_gate_must_pass")
    for key in [
        "source_pre_submission_hash",
        "lifecycle_trace_hash",
        "copied_lifecycle_trace_hash",
        "final_package_hash",
        "application_materials_hash",
    ]:
        if not isinstance(package.get(key), str) or not SHA256_RE.fullmatch(str(package.get(key))):
            errors.append(f"handoff_hash_invalid: {key}")
    for field in [
        "official_system_touched",
        "official_submission_performed",
        "adapter_execution_performed",
        "automatic_submission_performed",
    ]:
        if package.get(field) is not False:
            errors.append(f"handoff_{field}_must_be_false")

    controls = package.get("handoff_controls") if isinstance(package.get("handoff_controls"), dict) else {}
    for field in [
        "read_only_handoff",
        "does_not_authorize_automatic_submission",
        "requires_separate_adapter_execution_result",
        "requires_receipt_capture_after_submission",
        "no_receipt_claimed",
        "no_application_number_claimed",
    ]:
        if controls.get(field) is not True:
            errors.append(f"handoff_control_must_be_true: {field}")

    source_dir_raw = package.get("source_pre_submission_dir")
    source_dir = None
    if isinstance(source_dir_raw, str) and source_dir_raw:
        source_dir = (folder / source_dir_raw).resolve()
        if not source_dir.exists() or not source_dir.is_dir():
            errors.append("source_pre_submission_dir_missing")
        else:
            ok, errs, warns = validate_pre_submission_pipeline_benchmark.validate(source_dir)
            if not ok:
                errors.extend([f"source_pre_submission: {item}" for item in errs])
            warnings.extend([f"source_pre_submission: {item}" for item in warns])
            source_result = source_dir / "pre-submission-pipeline-result.json"
            if source_result.exists() and package.get("source_pre_submission_hash") != sha256_file(source_result):
                errors.append("source_pre_submission_hash_mismatch")

    entries = package.get("evidence_files")
    if not isinstance(entries, list) or not entries:
        errors.append("evidence_files_must_be_nonempty_list")
        entries = []
    roles = evidence_by_role(package)
    missing_roles = sorted(REQUIRED_ROLES - set(roles))
    for role in missing_roles:
        errors.append(f"missing_evidence_role: {role}")
    if package.get("reference_patent_delta_hash"):
        if "reference_patent_delta" not in roles:
            errors.append("reference_delta_handoff_missing_evidence")
        if package.get("reference_delta_boundary_preserved") is not True:
            errors.append("reference_delta_boundary_must_be_preserved")
        for key in ["reference_delta_rows_count", "reference_delta_claim_elements_count"]:
            if not isinstance(package.get(key), int) or isinstance(package.get(key), bool) or package.get(key) <= 0:
                errors.append(f"reference_delta_count_invalid: {key}")

    seen_paths: set[str] = set()
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            errors.append(f"evidence_{index}_must_be_object")
            continue
        role = item.get("role")
        package_rel = item.get("package_path")
        if not isinstance(role, str) or not role:
            errors.append(f"evidence_{index}_role_missing")
        if not isinstance(package_rel, str) or not package_rel:
            errors.append(f"evidence_{index}_package_path_missing")
            continue
        if package_rel in seen_paths:
            errors.append(f"duplicate_evidence_package_path: {package_rel}")
        seen_paths.add(package_rel)
        copied_path = safe_rel_file(folder, package_rel)
        if copied_path is None:
            errors.append(f"unsafe_evidence_package_path: {package_rel}")
            continue
        if not copied_path.exists() or not copied_path.is_file():
            errors.append(f"missing_evidence_file: {package_rel}")
            continue
        actual_hash = sha256_file(copied_path)
        if item.get("sha256") != actual_hash:
            errors.append(f"evidence_hash_mismatch: {package_rel}")
        if item.get("source_sha256") != actual_hash:
            errors.append(f"evidence_source_hash_mismatch: {package_rel}")
        if item.get("bytes") != copied_path.stat().st_size:
            errors.append(f"evidence_byte_count_mismatch: {package_rel}")
        if source_dir is not None and isinstance(item.get("source_path"), str):
            source_path = (source_dir / str(item["source_path"])).resolve()
            try:
                source_path.relative_to(source_dir.resolve())
            except ValueError:
                errors.append(f"evidence_source_path_outside_source_dir: {item.get('source_path')}")
                continue
            if not source_path.exists() or sha256_file(source_path) != actual_hash:
                errors.append(f"evidence_source_file_mismatch: {item.get('source_path')}")

    lifecycle_item = roles.get("case_lifecycle_trace")
    if lifecycle_item:
        lifecycle_path = safe_rel_file(folder, str(lifecycle_item.get("package_path") or ""))
        if lifecycle_path and lifecycle_path.exists():
            try:
                trace = load_json(lifecycle_path)
            except Exception as exc:
                errors.append(f"handoff_lifecycle_json_invalid: {exc}")
                trace = {}
            if trace:
                if trace.get("final_status") != "approved_for_adapter_execution":
                    errors.append("handoff_lifecycle_final_status_invalid")
                if trace.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
                    errors.append("handoff_lifecycle_legal_gate_invalid")
                if trace.get("external_lawyer_involved") is not False:
                    errors.append("handoff_lifecycle_external_lawyer_must_be_false")
                if package.get("reference_patent_delta_hash"):
                    if trace.get("reference_patent_delta_hash") != package.get("reference_patent_delta_hash"):
                        errors.append("handoff_lifecycle_reference_delta_hash_mismatch")
                    if trace.get("reference_delta_rows_count") != package.get("reference_delta_rows_count"):
                        errors.append("handoff_lifecycle_reference_delta_rows_mismatch")
                    if trace.get("reference_delta_claim_elements_count") != package.get("reference_delta_claim_elements_count"):
                        errors.append("handoff_lifecycle_reference_delta_claim_elements_mismatch")
                    if trace.get("reference_delta_boundary_preserved") is not True:
                        errors.append("handoff_lifecycle_reference_delta_boundary_missing")
            if package.get("lifecycle_trace_hash") != sha256_file(lifecycle_path):
                errors.append("handoff_lifecycle_trace_hash_mismatch")
            if package.get("copied_lifecycle_trace_hash") != sha256_file(lifecycle_path):
                errors.append("handoff_copied_lifecycle_trace_hash_mismatch")

    app_item = roles.get("application_materials")
    if app_item:
        app_path = safe_rel_file(folder, str(app_item.get("package_path") or ""))
        if app_path and app_path.exists():
            try:
                materials = load_json(app_path)
            except Exception as exc:
                errors.append(f"handoff_application_materials_json_invalid: {exc}")
                materials = {}
            if materials:
                if materials.get("case_id") != package.get("case_id"):
                    errors.append("handoff_application_materials_case_id_mismatch")
                if materials.get("final_package_hash") != package.get("final_package_hash"):
                    errors.append("handoff_final_package_hash_mismatch")
            if sha256_file(app_path) != package.get("application_materials_hash"):
                errors.append("handoff_application_materials_hash_mismatch")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "pre-submission handoff package",
            "lifecycle gate: passed",
            "not a filing",
            "not a submission receipt",
            "not an application-number evidence artifact",
            "automatic submission performed: no",
        ]:
            if needle not in text:
                errors.append(f"handoff_report_missing_text: {needle}")
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
    parser.add_argument("folder", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.folder)
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
