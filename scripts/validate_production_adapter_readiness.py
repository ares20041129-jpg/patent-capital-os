#!/usr/bin/env python3
"""Validate production filing-adapter readiness before approved execution."""

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
    "readiness_gate",
    "evidence_mode",
    "official_system",
    "adapter.name",
    "adapter.version",
    "adapter.registry_entry_hash",
    "adapter.release_artifact_hash",
    "adapter.source_review_hash",
    "adapter.supported_actions",
    "adapter.approved_for_production",
    "security_review.reviewed_by",
    "security_review.reviewed_at",
    "security_review.result",
    "security_review.scope",
    "security_review.review_artifact_hash",
    "security_review.threat_model_hash",
    "security_review.dependency_scan_hash",
    "security_review.sandbox_dry_run_hash",
    "credential_policy.credential_source",
    "approval.account_owner_authorization_hash",
    "approval.filing_ops_approval_hash",
    "approval.compliance_approval_hash",
    "execution_controls.requested_action",
    "audit.audit_log_schema_hash",
    "rollback.duplicate_submission_prevention",
    "rollback.idempotency_key_policy",
    "decision.status",
    "decision.reason",
]

HASH_PATHS = [
    "adapter.registry_entry_hash",
    "adapter.release_artifact_hash",
    "adapter.source_review_hash",
    "security_review.review_artifact_hash",
    "security_review.threat_model_hash",
    "security_review.dependency_scan_hash",
    "security_review.sandbox_dry_run_hash",
    "approval.account_owner_authorization_hash",
    "approval.filing_ops_approval_hash",
    "approval.compliance_approval_hash",
    "audit.audit_log_schema_hash",
]

FALSE_PATHS = [
    "credential_policy.raw_credentials_in_request",
    "credential_policy.private_keys_in_request",
    "credential_policy.session_tokens_in_request",
    "credential_policy.cookies_in_request",
    "credential_policy.mfa_secrets_in_request",
    "credential_policy.stores_credentials",
    "official_controls.bypasses_access_controls",
    "official_controls.bypasses_captcha",
    "official_controls.bypasses_signature_ceremony",
    "official_controls.bypasses_mfa",
]

TRUE_PATHS = [
    "official_controls.respects_mfa",
    "official_controls.human_only_steps_trigger_handoff",
    "official_controls.signature_ceremony_handoff_if_required",
    "official_controls.payment_requires_explicit_authority",
    "execution_controls.dry_run_required_before_production",
    "execution_controls.stop_on_hash_mismatch",
    "execution_controls.stop_on_human_only_step",
    "execution_controls.stop_on_access_control_bypass",
    "execution_controls.receipt_capture_required",
    "execution_controls.audit_logging_required",
    "execution_controls.docket_update_required",
    "execution_controls.immutable_package_hash_required",
    "audit.logs_input_hashes",
    "audit.logs_output_hashes",
    "audit.redacts_secrets",
    "rollback.duplicate_submission_prevention",
]


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
        if value.get("not_real_adapter_approval") is True and not allow_production_shape_test:
            return "not_real_adapter_approval"
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

    if data.get("readiness_gate") != "production_adapter_readiness_gate":
        errors.append("readiness_gate_must_be_production_adapter_readiness_gate")

    evidence_mode = data.get("evidence_mode")
    if evidence_mode == "production_shape_test":
        if allow_production_shape_test:
            if data.get("not_real_adapter_approval") is not True:
                errors.append("production_shape_test_requires_not_real_adapter_approval_true")
            warnings.append("production_shape_test_not_real_adapter_approval")
        else:
            errors.append("production_shape_test_not_allowed_in_strict_adapter_readiness")
    elif evidence_mode != "production_adapter_readiness":
        errors.append("evidence_mode_must_be_production_adapter_readiness")

    marker = mock_or_test_marker(data, allow_production_shape_test)
    if marker:
        errors.append(f"packet_contains_mock_or_test_marker: {marker}")

    if data.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer":
        if data.get("external_lawyer_involved") is not False:
            errors.append("ai_self_filing_adapter_readiness_requires_external_lawyer_false")
    elif data.get("legal_gate_mode") not in {"counsel_or_agent_review", "ai_self_filing_no_external_lawyer"}:
        errors.append("legal_gate_mode_invalid")

    if get_path(data, "adapter.approved_for_production") is not True:
        errors.append("adapter_approved_for_production_must_be_true")

    supported_actions = get_path(data, "adapter.supported_actions")
    joined_actions = " ".join(str(item).lower() for item in supported_actions) if isinstance(supported_actions, list) else str(supported_actions or "").lower()
    if "submit_package" not in joined_actions:
        errors.append("adapter_supported_actions_must_include_submit_package")

    if str(get_path(data, "security_review.result") or "").lower() != "passed":
        errors.append("security_review_result_must_be_passed")

    if str(get_path(data, "security_review.credential_handling_result") or "").lower() != "passed":
        errors.append("credential_handling_review_must_be_passed")

    if get_path(data, "credential_policy.credential_source") not in {"official_session_broker", "authorized_human_handoff", "platform_secret_broker"}:
        errors.append("credential_source_invalid")

    for path in FALSE_PATHS:
        if get_path(data, path) is not False:
            errors.append(f"flag_must_be_false: {path}")

    for path in TRUE_PATHS:
        if get_path(data, path) is not True:
            errors.append(f"flag_must_be_true: {path}")

    if get_path(data, "execution_controls.requested_action") != "submit_package":
        errors.append("requested_action_must_be_submit_package")

    failure_modes = get_path(data, "rollback.failure_modes")
    if not isinstance(failure_modes, list) or not failure_modes:
        errors.append("rollback_failure_modes_must_be_nonempty_list")

    retention_policy = str(get_path(data, "audit.retention_policy") or "")
    if len(retention_policy.strip()) < 6:
        errors.append("audit_retention_policy_required")

    expected_decision = "production_shape_test_verified" if evidence_mode == "production_shape_test" else "production_adapter_ready"
    if get_path(data, "decision.status") != expected_decision:
        errors.append(f"decision_status_must_be_{expected_decision}")

    if errors and get_path(data, "decision.status") == "production_adapter_ready":
        warnings.append("decision_status_overstates_adapter_readiness")

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
