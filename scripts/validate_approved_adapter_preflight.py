#!/usr/bin/env python3
"""Validate approved-adapter preflight evidence before real filing execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_official_session_authorization
import validate_production_adapter_readiness


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED_PATHS = [
    "case_id",
    "execution_mode",
    "adapter.name",
    "adapter.version",
    "adapter.registry_entry_hash",
    "adapter.dry_run_result_hash",
    "adapter.production_readiness.readiness_gate",
    "adapter.production_readiness.evidence_mode",
    "adapter.production_readiness.packet",
    "adapter.production_readiness.packet_hash",
    "adapter.production_readiness.validation_result",
    "adapter.production_readiness.adapter_name",
    "adapter.production_readiness.adapter_version",
    "adapter.production_readiness.registry_entry_hash",
    "adapter.security_review.reviewed_by",
    "adapter.security_review.reviewed_at",
    "adapter.security_review.result",
    "adapter.security_review.review_artifact_hash",
    "adapter.security_review.scope",
    "authorization.submission_authorization_packet",
    "authorization.submission_authorization_packet_hash",
    "authorization.account_owner_authorization",
    "authorization.signature_authority_evidence",
    "authorization.payment_authority_evidence",
    "authorization.allowed_actions",
    "authorization.two_person_approval.legal_approver",
    "authorization.two_person_approval.ops_approver",
    "authorization.two_person_approval.approved_at",
    "authorization.two_person_approval.evidence_hash",
    "official_channel.preflight_file",
    "official_channel.preflight_hash",
    "official_channel.official_system",
    "official_channel.session_authorization.session_gate",
    "official_channel.session_authorization.evidence_mode",
    "official_channel.session_authorization.packet",
    "official_channel.session_authorization.packet_hash",
    "official_channel.session_authorization.validation_result",
    "official_channel.session_authorization.approved_for_real_execution",
    "official_channel.session_authorization.official_account_role",
    "official_channel.session_authorization.session_reference_hash",
    "official_channel.session_authorization.authorization_scope_hash",
    "package.manifest_file",
    "package.manifest_hash",
    "package.final_package_hash",
    "package.reviewed_package_hash",
    "package.xml_validation_result",
    "package.attachment_list_hash",
    "evidence.receipt_capture_plan",
    "evidence.receipt_capture_plan_hash",
    "evidence.audit_log_entry_plan",
    "evidence.audit_log_entry_plan_hash",
    "evidence.docket_entry_plan",
    "evidence.docket_entry_plan_hash",
    "execution_controls.requested_action",
    "decision.status",
    "decision.reason",
    "decision.next_status_if_success",
]

HASH_PATHS = [
    "adapter.registry_entry_hash",
    "adapter.dry_run_result_hash",
    "adapter.production_readiness.packet_hash",
    "adapter.production_readiness.registry_entry_hash",
    "adapter.security_review.review_artifact_hash",
    "authorization.submission_authorization_packet_hash",
    "authorization.two_person_approval.evidence_hash",
    "official_channel.preflight_hash",
    "official_channel.session_authorization.packet_hash",
    "official_channel.session_authorization.session_reference_hash",
    "official_channel.session_authorization.authorization_scope_hash",
    "package.manifest_hash",
    "package.final_package_hash",
    "package.reviewed_package_hash",
    "package.attachment_list_hash",
    "evidence.receipt_capture_plan_hash",
    "evidence.audit_log_entry_plan_hash",
    "evidence.docket_entry_plan_hash",
]

FORBIDDEN_CREDENTIAL_FLAGS = [
    "credential_handling.raw_credentials_in_request",
    "credential_handling.private_keys_in_request",
    "credential_handling.captcha_bypass",
    "credential_handling.mfa_secret_in_request",
    "credential_handling.session_token_in_request",
    "credential_handling.stores_credentials",
]


def load_packet(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("YAML input requires PyYAML. Use JSON or install PyYAML.") from exc
        loaded = yaml.safe_load(text)
        return loaded or {}
    raise RuntimeError("Unsupported input format. Use .json, .yaml, or .yml")


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_reference(reference: Any, base_dir: Path) -> Path:
    path = Path(str(reference))
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def require_hash(data: dict[str, Any], dotted: str, errors: list[str]) -> None:
    value = get_path(data, dotted)
    if is_blank(value):
        errors.append(f"missing_required_field: {dotted}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{dotted}_must_be_sha256_64_hex")


def require_positive_int(value: Any, label: str, errors: list[str]) -> None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        errors.append(f"{label}_must_be_positive_integer")
        return
    if parsed <= 0:
        errors.append(f"{label}_must_be_positive_integer")


def validate_file_hash_reference(
    data: dict[str, Any],
    path_key: str,
    hash_key: str,
    label: str,
    base_dir: Path | None,
    errors: list[str],
) -> None:
    if base_dir is None or is_blank(get_path(data, path_key)):
        return
    path = resolve_reference(get_path(data, path_key), base_dir)
    if not path.exists():
        errors.append(f"{label}_file_not_found")
        return
    if get_path(data, hash_key) and sha256_file(path) != get_path(data, hash_key):
        errors.append(f"{label}_hash_mismatch")


def action_scope_has_submit_and_fee(data: dict[str, Any]) -> tuple[bool, bool]:
    actions = get_path(data, "authorization.allowed_actions")
    if isinstance(actions, str):
        joined = actions.lower()
    elif isinstance(actions, list):
        joined = " ".join(str(item).lower() for item in actions)
    else:
        joined = ""
    has_submit = "submit" in joined or "file" in joined or "提交" in joined
    has_fee = "pay" in joined or "fee" in joined or "缴费" in joined or "费用" in joined
    return has_submit, has_fee


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")

    for path in HASH_PATHS:
        require_hash(data, path, errors)

    for path_key, hash_key, label in [
        ("authorization.submission_authorization_packet", "authorization.submission_authorization_packet_hash", "submission_authorization_packet"),
        ("official_channel.preflight_file", "official_channel.preflight_hash", "official_channel_preflight"),
        ("package.manifest_file", "package.manifest_hash", "package_manifest"),
        ("evidence.receipt_capture_plan", "evidence.receipt_capture_plan_hash", "receipt_capture_plan"),
        ("evidence.audit_log_entry_plan", "evidence.audit_log_entry_plan_hash", "audit_log_entry_plan"),
        ("evidence.docket_entry_plan", "evidence.docket_entry_plan_hash", "docket_entry_plan"),
    ]:
        validate_file_hash_reference(data, path_key, hash_key, label, base_dir, errors)

    if get_path(data, "execution_mode") != "approved_adapter":
        errors.append("execution_mode_must_be_approved_adapter")

    if get_path(data, "adapter.approved_for_production") is not True:
        errors.append("adapter_must_be_approved_for_production")

    if get_path(data, "adapter.production_readiness.readiness_gate") != "production_adapter_readiness_gate":
        errors.append("adapter_production_readiness_gate_must_be_production_adapter_readiness_gate")
    if get_path(data, "adapter.production_readiness.evidence_mode") != "production_adapter_readiness":
        errors.append("adapter_production_readiness_evidence_mode_must_be_production_adapter_readiness")
    if get_path(data, "adapter.production_readiness.validation_result") != "passed":
        errors.append("adapter_production_readiness_validation_must_be_passed")
    if get_path(data, "adapter.production_readiness.approved_for_real_execution") is not True:
        errors.append("adapter_production_readiness_must_approve_real_execution")
    if get_path(data, "adapter.production_readiness.adapter_name") != get_path(data, "adapter.name"):
        errors.append("adapter_production_readiness_name_mismatch")
    if get_path(data, "adapter.production_readiness.adapter_version") != get_path(data, "adapter.version"):
        errors.append("adapter_production_readiness_version_mismatch")
    if get_path(data, "adapter.production_readiness.registry_entry_hash") != get_path(data, "adapter.registry_entry_hash"):
        errors.append("adapter_production_readiness_registry_hash_mismatch")

    if base_dir is not None and not is_blank(get_path(data, "adapter.production_readiness.packet")):
        readiness_path = resolve_reference(get_path(data, "adapter.production_readiness.packet"), base_dir)
        if not readiness_path.exists():
            errors.append("adapter_production_readiness_packet_missing")
        else:
            readiness_hash = sha256_file(readiness_path)
            if readiness_hash != get_path(data, "adapter.production_readiness.packet_hash"):
                errors.append("adapter_production_readiness_packet_hash_mismatch")
            readiness_packet: dict[str, Any] | None = None
            try:
                readiness_packet = validate_production_adapter_readiness.load_json(readiness_path)
                readiness_ok, readiness_errors, readiness_warnings = validate_production_adapter_readiness.validate_packet(readiness_packet)
            except Exception as exc:
                readiness_ok, readiness_errors, readiness_warnings = False, [str(exc)], []
            if not readiness_ok:
                errors.extend([f"adapter_production_readiness_packet: {item}" for item in readiness_errors])
            warnings.extend([f"adapter_production_readiness_packet: {item}" for item in readiness_warnings])
            if readiness_packet is not None:
                if get_path(readiness_packet, "adapter.name") != get_path(data, "adapter.name"):
                    errors.append("adapter_production_readiness_packet_name_mismatch")
                if get_path(readiness_packet, "adapter.version") != get_path(data, "adapter.version"):
                    errors.append("adapter_production_readiness_packet_version_mismatch")
                if get_path(readiness_packet, "adapter.registry_entry_hash") != get_path(data, "adapter.registry_entry_hash"):
                    errors.append("adapter_production_readiness_packet_registry_hash_mismatch")
                if get_path(readiness_packet, "official_system") != get_path(data, "official_channel.official_system"):
                    errors.append("adapter_production_readiness_official_system_mismatch")

    if str(get_path(data, "adapter.security_review.result") or "").lower() != "passed":
        errors.append("adapter_security_review_must_be_passed")

    if get_path(data, "authorization.applicant_authorization_confirmed") is not True:
        errors.append("applicant_authorization_must_be_confirmed")

    counsel_confirmed = get_path(data, "authorization.counsel_review_confirmed") is True
    ai_self_filing_confirmed = get_path(data, "authorization.ai_self_filing_confirmed") is True
    if not counsel_confirmed and not ai_self_filing_confirmed:
        errors.append("legal_gate_requires_counsel_review_or_ai_self_filing_confirmation")
    if ai_self_filing_confirmed:
        if get_path(data, "authorization.external_lawyer_involved") is not False:
            errors.append("ai_self_filing_requires_external_lawyer_involved_false")
        if base_dir is not None:
            try:
                readiness_path = resolve_reference(get_path(data, "adapter.production_readiness.packet"), base_dir)
                readiness_packet = validate_production_adapter_readiness.load_json(readiness_path)
                if get_path(readiness_packet, "legal_gate_mode") != "ai_self_filing_no_external_lawyer":
                    errors.append("ai_self_filing_requires_ai_readiness_legal_gate_mode")
                if get_path(readiness_packet, "external_lawyer_involved") is not False:
                    errors.append("ai_self_filing_requires_readiness_external_lawyer_false")
            except Exception:
                pass
        if get_path(data, "authorization.self_filing_allowed") is not True:
            errors.append("ai_self_filing_requires_self_filing_allowed_true")
        if get_path(data, "authorization.mandatory_agent_required") is not False:
            errors.append("ai_self_filing_requires_mandatory_agent_required_false")
        if get_path(data, "authorization.foreign_or_hmt_applicant") is not False:
            errors.append("ai_self_filing_requires_foreign_or_hmt_applicant_false")
        if get_path(data, "authorization.agency_bypass_requested") is not False:
            errors.append("ai_self_filing_requires_agency_bypass_requested_false")

    legal_approver = get_path(data, "authorization.two_person_approval.legal_approver")
    ops_approver = get_path(data, "authorization.two_person_approval.ops_approver")
    if legal_approver and ops_approver and legal_approver == ops_approver:
        errors.append("two_person_approval_requires_distinct_legal_and_ops_approvers")

    has_submit, has_fee = action_scope_has_submit_and_fee(data)
    if not has_submit:
        errors.append("authorization_scope_missing_submit_or_file")
    if get_path(data, "execution_controls.payment_allowed") is True and not has_fee:
        errors.append("payment_allowed_without_fee_authorization")

    if get_path(data, "official_channel.automation_allowed") is not True:
        errors.append("official_channel_automation_must_be_allowed")

    if get_path(data, "official_channel.bypasses_access_controls") is not False:
        errors.append("official_channel_must_not_bypass_access_controls")

    if get_path(data, "official_channel.session_authorization.session_gate") != "official_session_authorization_gate":
        errors.append("official_session_authorization_gate_must_be_official_session_authorization_gate")
    if get_path(data, "official_channel.session_authorization.evidence_mode") != "official_session_authorization":
        errors.append("official_session_authorization_evidence_mode_must_be_official_session_authorization")
    if get_path(data, "official_channel.session_authorization.validation_result") != "passed":
        errors.append("official_session_authorization_validation_must_be_passed")
    if get_path(data, "official_channel.session_authorization.approved_for_real_execution") is not True:
        errors.append("official_session_authorization_must_approve_real_execution")

    if base_dir is not None and not is_blank(get_path(data, "official_channel.session_authorization.packet")):
        session_path = resolve_reference(get_path(data, "official_channel.session_authorization.packet"), base_dir)
        if not session_path.exists():
            errors.append("official_session_authorization_packet_missing")
        else:
            session_hash = sha256_file(session_path)
            if session_hash != get_path(data, "official_channel.session_authorization.packet_hash"):
                errors.append("official_session_authorization_packet_hash_mismatch")
            session_packet: dict[str, Any] | None = None
            try:
                session_packet = validate_official_session_authorization.load_json(session_path)
                session_ok, session_errors, session_warnings = validate_official_session_authorization.validate_packet(session_packet)
            except Exception as exc:
                session_ok, session_errors, session_warnings = False, [str(exc)], []
            if not session_ok:
                errors.extend([f"official_session_authorization_packet: {item}" for item in session_errors])
            warnings.extend([f"official_session_authorization_packet: {item}" for item in session_warnings])
            if session_packet is not None:
                if get_path(session_packet, "official_system") != get_path(data, "official_channel.official_system"):
                    errors.append("official_session_authorization_official_system_mismatch")
                if get_path(session_packet, "official_account.role") != get_path(data, "official_channel.session_authorization.official_account_role"):
                    errors.append("official_session_authorization_account_role_mismatch")
                if get_path(session_packet, "session_broker.session_reference_hash") != get_path(data, "official_channel.session_authorization.session_reference_hash"):
                    errors.append("official_session_authorization_session_reference_hash_mismatch")
                if get_path(session_packet, "official_account.authorization_scope_hash") != get_path(data, "official_channel.session_authorization.authorization_scope_hash"):
                    errors.append("official_session_authorization_scope_hash_mismatch")
                if ai_self_filing_confirmed:
                    if get_path(session_packet, "legal_gate_mode") != "ai_self_filing_no_external_lawyer":
                        errors.append("ai_self_filing_requires_ai_session_authorization_legal_gate_mode")
                    if get_path(session_packet, "external_lawyer_involved") is not False:
                        errors.append("ai_self_filing_requires_session_authorization_external_lawyer_false")

    human_only_steps = get_path(data, "official_channel.human_only_steps")
    if human_only_steps:
        errors.append("human_only_steps_require_handoff_not_approved_adapter")
    if get_path(data, "official_channel.human_only_steps_resolved") is not True:
        errors.append("human_only_steps_resolved_must_be_true")

    final_hash = get_path(data, "package.final_package_hash")
    reviewed_hash = get_path(data, "package.reviewed_package_hash")
    if final_hash and reviewed_hash and final_hash != reviewed_hash:
        errors.append("hash_mismatch: package.final_package_hash != package.reviewed_package_hash")

    if str(get_path(data, "package.xml_validation_result") or "").lower() != "passed":
        errors.append("package_xml_validation_must_be_passed")

    application_materials = data.get("application_materials") if isinstance(data.get("application_materials"), dict) else {}
    preflight_application_materials: dict[str, Any] = {}
    if base_dir is not None and not is_blank(get_path(data, "official_channel.preflight_file")):
        try:
            preflight_path = resolve_reference(get_path(data, "official_channel.preflight_file"), base_dir)
            preflight_packet = load_packet(preflight_path)
            loaded_materials = preflight_packet.get("application_materials")
            if isinstance(loaded_materials, dict):
                preflight_application_materials = loaded_materials
        except Exception:
            preflight_application_materials = {}
    preflight_reference_hash = preflight_application_materials.get("reference_patent_delta_hash")
    application_reference_hash = application_materials.get("reference_patent_delta_hash")
    reference_delta_binding_required = bool(preflight_reference_hash or application_reference_hash)
    if application_materials:
        application_materials_hash = application_materials.get("hash")
        preflight_materials_hash = preflight_application_materials.get("hash")
        if not is_blank(application_materials_hash) and not SHA256_RE.fullmatch(str(application_materials_hash)):
            errors.append("application_materials.hash_must_be_sha256_64_hex")
        if not is_blank(application_materials_hash) and not is_blank(preflight_materials_hash):
            if application_materials_hash != preflight_materials_hash:
                errors.append("application_materials_hash_mismatch_with_official_preflight")
    if reference_delta_binding_required:
        if not application_materials:
            errors.append("application_materials_must_be_preserved_from_official_preflight")
        if application_materials.get("hash") != preflight_application_materials.get("hash"):
            errors.append("application_materials_hash_mismatch_with_official_preflight")
        if application_reference_hash != preflight_reference_hash:
            errors.append("reference_patent_delta_hash_mismatch_with_official_preflight")
        if is_blank(application_reference_hash):
            errors.append("missing_required_field: application_materials.reference_patent_delta_hash")
        elif not SHA256_RE.fullmatch(str(application_reference_hash)):
            errors.append("application_materials.reference_patent_delta_hash_must_be_sha256_64_hex")
        require_positive_int(application_materials.get("reference_delta_rows_count"), "application_materials.reference_delta_rows_count", errors)
        require_positive_int(
            application_materials.get("reference_delta_claim_elements_count"),
            "application_materials.reference_delta_claim_elements_count",
            errors,
        )
        if application_materials.get("reference_delta_boundary_preserved") is not True:
            errors.append("application_materials_reference_delta_boundary_must_be_true")

    for path in FORBIDDEN_CREDENTIAL_FLAGS:
        if get_path(data, path) is not False:
            errors.append(f"forbidden_credential_handling_flag_must_be_false: {path}")

    for path in [
        "execution_controls.stop_on_hash_mismatch",
        "execution_controls.stop_on_human_only_step",
        "execution_controls.stop_on_access_control_bypass",
        "execution_controls.receipt_capture_required",
        "execution_controls.audit_log_required",
        "execution_controls.docket_update_required",
    ]:
        if get_path(data, path) is not True:
            errors.append(f"execution_control_must_be_true: {path}")

    if get_path(data, "execution_controls.requested_action") != "submit_package":
        errors.append("requested_action_must_be_submit_package")

    decision = str(get_path(data, "decision.status") or "")
    if decision not in {"approved_for_adapter_execution", "handoff_required", "blocked"}:
        errors.append("decision_status_invalid")
    if decision == "approved_for_adapter_execution" and get_path(data, "decision.next_status_if_success") != "submitted_pending_receipt":
        errors.append("approved_adapter_next_status_must_be_submitted_pending_receipt")

    if errors and decision == "approved_for_adapter_execution":
        warnings.append("decision_status_overstates_adapter_readiness")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("preflight", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_packet(args.preflight), base_dir=args.preflight.parent)
    except Exception as exc:
        ok, errors, warnings = False, [str(exc)], []

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
