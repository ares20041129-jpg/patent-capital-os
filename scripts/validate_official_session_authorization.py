#!/usr/bin/env python3
"""Validate official session authorization before approved adapter execution."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_KEYS = {
    "password",
    "private_key",
    "captcha_bypass",
    "mfa_secret",
    "session_token",
    "cookie",
    "raw_credentials",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED_PATHS = [
    "session_gate",
    "evidence_mode",
    "legal_gate_mode",
    "external_lawyer_involved",
    "official_system",
    "official_account.role",
    "official_account.account_owner_authorization_hash",
    "official_account.self_filing_authority_hash",
    "official_account.authorization_scope_hash",
    "session_broker.name",
    "session_broker.version",
    "session_broker.approval_hash",
    "session_broker.session_reference_hash",
    "session_broker.session_reference_scope",
    "session_broker.expires_at",
    "session_broker.scoped_to_case",
    "session_broker.revocable",
    "session_broker.expiry_enforced",
    "authorization.allowed_actions",
    "authorization.signature_authority_hash",
    "authorization.payment_authority_hash",
    "authorization.fee_payment_allowed",
    "authorization.filing_action_idempotency_key",
    "authorization.human_only_steps_resolved",
    "credential_boundary.credential_source",
    "credential_boundary.credential_material_included",
    "credential_boundary.raw_credentials_in_request",
    "credential_boundary.private_keys_in_request",
    "credential_boundary.session_tokens_in_request",
    "credential_boundary.cookies_in_request",
    "credential_boundary.mfa_secrets_in_request",
    "credential_boundary.passwords_in_request",
    "credential_boundary.stores_credentials",
    "official_controls.respects_mfa",
    "official_controls.respects_captcha",
    "official_controls.access_control_enforced",
    "official_controls.human_only_steps_trigger_handoff",
    "official_controls.signature_ceremony_handoff_if_required",
    "official_controls.bypasses_access_controls",
    "official_controls.bypasses_captcha",
    "official_controls.bypasses_signature_ceremony",
    "official_controls.bypasses_mfa",
    "official_controls.human_only_step_bypassed",
    "execution_controls.requested_action",
    "execution_controls.stop_on_hash_mismatch",
    "execution_controls.stop_on_human_only_step",
    "execution_controls.stop_on_access_control_bypass",
    "execution_controls.receipt_capture_required",
    "execution_controls.audit_logging_required",
    "execution_controls.idempotency_key_required",
    "audit.audit_log_schema_hash",
    "audit.logs_input_hashes",
    "audit.logs_output_hashes",
    "audit.redacts_secrets",
    "audit.retention_policy",
    "decision.status",
    "decision.reason",
]

HASH_PATHS = [
    "official_account.account_owner_authorization_hash",
    "official_account.self_filing_authority_hash",
    "official_account.authorization_scope_hash",
    "session_broker.approval_hash",
    "session_broker.session_reference_hash",
    "authorization.signature_authority_hash",
    "authorization.payment_authority_hash",
    "audit.audit_log_schema_hash",
]

FALSE_PATHS = [
    "credential_boundary.credential_material_included",
    "credential_boundary.raw_credentials_in_request",
    "credential_boundary.private_keys_in_request",
    "credential_boundary.session_tokens_in_request",
    "credential_boundary.cookies_in_request",
    "credential_boundary.mfa_secrets_in_request",
    "credential_boundary.passwords_in_request",
    "credential_boundary.stores_credentials",
    "official_controls.bypasses_access_controls",
    "official_controls.bypasses_captcha",
    "official_controls.bypasses_signature_ceremony",
    "official_controls.bypasses_mfa",
    "official_controls.human_only_step_bypassed",
]

TRUE_PATHS = [
    "session_broker.scoped_to_case",
    "session_broker.revocable",
    "session_broker.expiry_enforced",
    "authorization.human_only_steps_resolved",
    "official_controls.respects_mfa",
    "official_controls.respects_captcha",
    "official_controls.access_control_enforced",
    "official_controls.human_only_steps_trigger_handoff",
    "official_controls.signature_ceremony_handoff_if_required",
    "execution_controls.stop_on_hash_mismatch",
    "execution_controls.stop_on_human_only_step",
    "execution_controls.stop_on_access_control_bypass",
    "execution_controls.receipt_capture_required",
    "execution_controls.audit_logging_required",
    "execution_controls.idempotency_key_required",
    "audit.logs_input_hashes",
    "audit.logs_output_hashes",
    "audit.redacts_secrets",
]

ALLOWED_ACCOUNT_ROLES = {
    "applicant_self_filing_account_owner",
    "enterprise_self_filing_operator",
    "authorized_applicant_representative",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def has_forbidden_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                return key
            found = has_forbidden_key(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = has_forbidden_key(child)
            if found:
                return found
    return None


def mock_or_test_marker(value: Any, allow_production_shape_test: bool) -> str | None:
    if isinstance(value, dict):
        if value.get("benchmark_mock") is True:
            return "benchmark_mock"
        if value.get("not_real_session_authorization") is True and not allow_production_shape_test:
            return "not_real_session_authorization"
        if value.get("production_shape_test") is True and not allow_production_shape_test:
            return "production_shape_test"
        for key, child in value.items():
            if key == "benchmark_mock" and child is True:
                return key
            found = mock_or_test_marker(child, allow_production_shape_test)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = mock_or_test_marker(child, allow_production_shape_test)
            if found:
                return found
    elif isinstance(value, str) and not allow_production_shape_test:
        lowered = value.lower()
        for marker in ["mock", "benchmark", "placeholder", "shape-test"]:
            if marker in lowered:
                return marker
    return None


def action_scope_has_submit_and_fee(data: dict[str, Any]) -> tuple[bool, bool]:
    actions = get_path(data, "authorization.allowed_actions")
    if isinstance(actions, str):
        joined = actions.lower()
    elif isinstance(actions, list):
        joined = " ".join(str(item).lower() for item in actions)
    else:
        joined = ""
    has_submit = "submit_package" in joined or "submit" in joined or "file" in joined
    has_fee = "pay" in joined or "fee" in joined
    return has_submit, has_fee


def validate_packet(
    data: dict[str, Any],
    allow_production_shape_test: bool = False,
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")
    for path in HASH_PATHS:
        require_hash(get_path(data, path), path, errors)

    forbidden = has_forbidden_key(data)
    if forbidden:
        errors.append(f"forbidden_field_present: {forbidden}")

    if data.get("session_gate") != "official_session_authorization_gate":
        errors.append("session_gate_must_be_official_session_authorization_gate")

    evidence_mode = data.get("evidence_mode")
    if evidence_mode == "production_shape_test":
        if allow_production_shape_test:
            if data.get("not_real_session_authorization") is not True:
                errors.append("production_shape_test_requires_not_real_session_authorization_true")
            warnings.append("production_shape_test_not_real_session_authorization")
        else:
            errors.append("production_shape_test_not_allowed_in_strict_session_authorization")
    elif evidence_mode != "official_session_authorization":
        errors.append("evidence_mode_must_be_official_session_authorization")

    marker = mock_or_test_marker(data, allow_production_shape_test)
    if marker:
        errors.append(f"packet_contains_mock_or_test_marker: {marker}")

    legal_gate_mode = data.get("legal_gate_mode")
    if legal_gate_mode == "ai_self_filing_no_external_lawyer":
        if data.get("external_lawyer_involved") is not False:
            errors.append("ai_self_filing_session_authorization_requires_external_lawyer_false")
    elif legal_gate_mode != "counsel_or_agent_review":
        errors.append("legal_gate_mode_invalid")

    if get_path(data, "official_account.role") not in ALLOWED_ACCOUNT_ROLES:
        errors.append("official_account_role_invalid_for_ai_self_filing_session")

    if get_path(data, "session_broker.session_reference_scope") not in {
        "case_and_action_scoped",
        "case_action_and_account_scoped",
    }:
        errors.append("session_reference_scope_must_be_case_action_scoped")

    if get_path(data, "credential_boundary.credential_source") != "official_session_broker":
        errors.append("credential_source_must_be_official_session_broker")

    for path in FALSE_PATHS:
        if get_path(data, path) is not False:
            errors.append(f"flag_must_be_false: {path}")
    for path in TRUE_PATHS:
        if get_path(data, path) is not True:
            errors.append(f"flag_must_be_true: {path}")

    human_only_steps = get_path(data, "authorization.human_only_steps")
    if human_only_steps:
        errors.append("human_only_steps_require_handoff_not_session_authorized_adapter")

    has_submit, has_fee = action_scope_has_submit_and_fee(data)
    if not has_submit:
        errors.append("authorization_scope_missing_submit_or_file")
    if get_path(data, "authorization.fee_payment_allowed") is True and not has_fee:
        errors.append("fee_payment_allowed_without_fee_action_scope")

    if get_path(data, "execution_controls.requested_action") != "submit_package":
        errors.append("requested_action_must_be_submit_package")

    retention_policy = str(get_path(data, "audit.retention_policy") or "")
    if len(retention_policy.strip()) < 6:
        errors.append("audit_retention_policy_required")

    expected_decision = (
        "official_session_shape_test_verified"
        if evidence_mode == "production_shape_test"
        else "official_session_authorized"
    )
    if get_path(data, "decision.status") != expected_decision:
        errors.append(f"decision_status_must_be_{expected_decision}")

    if errors and get_path(data, "decision.status") == "official_session_authorized":
        warnings.append("decision_status_overstates_session_authorization")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--allow-production-shape-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate_packet(
            load_json(args.packet),
            allow_production_shape_test=args.allow_production_shape_test,
        )
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
