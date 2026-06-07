#!/usr/bin/env python3
"""Validate AI-only self-filing authorization evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_PATHS = [
    "case_id",
    "filing_type",
    "jurisdiction",
    "source_draft_hash",
    "final_package_hash",
    "external_lawyer_involved",
    "self_filing_eligibility.applicant_region",
    "self_filing_eligibility.applicant_type",
    "self_filing_eligibility.self_filing_allowed",
    "self_filing_eligibility.mandatory_agent_required",
    "self_filing_eligibility.foreign_or_hmt_applicant",
    "self_filing_eligibility.agency_bypass_requested",
    "self_filing_eligibility.basis",
    "ai_compliance_review.engine_name",
    "ai_compliance_review.engine_version",
    "ai_compliance_review.checked_at",
    "ai_compliance_review.reviewed_artifacts_hash",
    "ai_compliance_review.no_copying_check",
    "ai_compliance_review.claim_support_check",
    "ai_compliance_review.abnormal_filing_risk",
    "ai_compliance_review.abnormal_filing_risk_assessment.case_id",
    "ai_compliance_review.abnormal_filing_risk_assessment.status",
    "ai_compliance_review.abnormal_filing_risk_assessment.gate",
    "ai_compliance_review.abnormal_filing_risk_assessment.risk_level",
    "ai_compliance_review.abnormal_filing_risk_assessment.artifact_hash",
    "ai_compliance_review.abnormal_filing_risk_assessment.artifact_path",
    "ai_compliance_review.official_format_check",
    "ai_compliance_review.limitations",
    "ai_compliance_review.legal_gate_review.review_record_hash",
    "ai_compliance_review.legal_gate_review.authorization_scope_check",
    "ai_compliance_review.legal_gate_review.self_filing_eligibility_check",
    "ai_compliance_review.legal_gate_review.inventor_ownership_check",
    "ai_compliance_review.legal_gate_review.secrecy_check",
    "ai_compliance_review.legal_gate_review.fee_authority_check",
    "ai_compliance_review.legal_gate_review.official_channel_boundary_check",
    "ai_compliance_review.legal_gate_review.stop_conditions_checked",
    "ai_compliance_review.legal_gate_review.legal_advice_claimed",
    "ai_compliance_review.legal_gate_review.lawyer_or_agent_review_claimed",
    "applicant_authorization.applicant_name",
    "applicant_authorization.authorized_person",
    "applicant_authorization.authority_basis",
    "applicant_authorization.allowed_actions",
    "applicant_authorization.timestamp",
    "inventor_confirmation.inventors",
    "inventor_confirmation.contribution_confirmed",
    "ownership.basis",
    "ownership.evidence",
    "ownership.dispute_absent",
    "secrecy_review.china_completed",
    "secrecy_review.foreign_or_pct_planned",
    "secrecy_review.status",
    "filing_channel.official_system",
    "filing_channel.account_owner",
    "filing_channel.official_account_registered",
    "filing_channel.signature_authority",
    "filing_channel.automation_allowed",
    "filing_channel.bypasses_access_controls",
    "fees.payer",
    "fees.fee_reduction",
    "fees.auto_pay_authorized",
    "fees.payment_account_reference",
    "decision.status",
    "decision.reason",
]

HASH_PATHS = [
    "source_draft_hash",
    "final_package_hash",
    "ai_compliance_review.reviewed_artifacts_hash",
    "ai_compliance_review.abnormal_filing_risk_assessment.artifact_hash",
    "ai_compliance_review.legal_gate_review.review_record_hash",
]

LEGAL_GATE_CHECK_PATHS = [
    "ai_compliance_review.legal_gate_review.authorization_scope_check",
    "ai_compliance_review.legal_gate_review.self_filing_eligibility_check",
    "ai_compliance_review.legal_gate_review.inventor_ownership_check",
    "ai_compliance_review.legal_gate_review.secrecy_check",
    "ai_compliance_review.legal_gate_review.fee_authority_check",
    "ai_compliance_review.legal_gate_review.official_channel_boundary_check",
]

REQUIRED_STOP_CONDITIONS = {
    "mandatory_agent_condition",
    "foreign_or_hmt_applicant_condition",
    "agency_bypass_request",
    "access_control_bypass",
    "official_submission_claim_without_evidence",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


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


def require_hash(data: dict[str, Any], dotted: str, errors: list[str]) -> None:
    value = get_path(data, dotted)
    require_hash_value(value, dotted, errors)


def require_hash_value(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def require_positive_int(value: Any, label: str, errors: list[str]) -> None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        errors.append(f"{label}_must_be_positive_integer")
        return
    if parsed <= 0:
        errors.append(f"{label}_must_be_positive_integer")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_reference(reference: Any, base_dir: Path) -> Path:
    path = Path(str(reference or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def validate_artifact_reference(
    data: dict[str, Any],
    base_dir: Path | None,
    errors: list[str],
) -> None:
    if base_dir is None:
        return
    raw_path = get_path(data, "ai_compliance_review.abnormal_filing_risk_assessment.artifact_path")
    expected_hash = get_path(data, "ai_compliance_review.abnormal_filing_risk_assessment.artifact_hash")
    if is_blank(raw_path):
        return
    path = resolve_reference(raw_path, base_dir)
    if not path.exists():
        errors.append("abnormal_filing_risk_assessment_artifact_file_not_found")
        return
    if expected_hash and sha256_file(path) != expected_hash:
        errors.append("abnormal_filing_risk_assessment_artifact_hash_mismatch")


def load_referenced_abnormal_assessment(
    data: dict[str, Any],
    base_dir: Path | None,
    errors: list[str],
) -> dict[str, Any] | None:
    if base_dir is None:
        return None
    raw_path = get_path(data, "ai_compliance_review.abnormal_filing_risk_assessment.artifact_path")
    if is_blank(raw_path):
        return None
    path = resolve_reference(raw_path, base_dir)
    if not path.exists():
        return None
    try:
        loaded = load_json(path)
    except Exception as exc:
        errors.append(f"abnormal_filing_risk_assessment_artifact_read_failed: {exc}")
        return None
    return loaded if isinstance(loaded, dict) else None


def action_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(item).lower() for item in value)
    return str(value or "").lower()


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")

    for path in HASH_PATHS:
        require_hash(data, path, errors)
    validate_artifact_reference(data, base_dir, errors)
    abnormal_artifact = load_referenced_abnormal_assessment(data, base_dir, errors)

    if data.get("external_lawyer_involved") is not False:
        errors.append("external_lawyer_involved_must_be_false_for_ai_self_filing")

    if get_path(data, "self_filing_eligibility.self_filing_allowed") is not True:
        errors.append("self_filing_must_be_allowed")
    if get_path(data, "self_filing_eligibility.mandatory_agent_required") is not False:
        errors.append("mandatory_agent_required_must_be_false")
    if get_path(data, "self_filing_eligibility.foreign_or_hmt_applicant") is not False:
        errors.append("foreign_or_hmt_applicant_must_be_false_for_this_route")
    if get_path(data, "self_filing_eligibility.agency_bypass_requested") is not False:
        errors.append("agency_bypass_requested_must_be_false")

    if get_path(data, "ai_compliance_review.no_copying_check") != "passed":
        errors.append("ai_no_copying_check_must_pass")
    if get_path(data, "ai_compliance_review.claim_support_check") != "passed":
        errors.append("ai_claim_support_check_must_pass")
    if get_path(data, "ai_compliance_review.official_format_check") != "passed":
        errors.append("ai_official_format_check_must_pass")
    if str(get_path(data, "ai_compliance_review.abnormal_filing_risk") or "").lower() not in {"low", "none"}:
        errors.append("ai_abnormal_filing_risk_must_be_low_or_none")
    assessment = get_path(data, "ai_compliance_review.abnormal_filing_risk_assessment")
    if isinstance(assessment, dict):
        if assessment.get("case_id") != data.get("case_id"):
            errors.append("abnormal_filing_risk_assessment_case_id_mismatch")
        if assessment.get("status") != "abnormal_filing_risk_assessed":
            errors.append("abnormal_filing_risk_assessment_status_invalid")
        if assessment.get("gate") != "G8 Non-abnormal filing check":
            errors.append("abnormal_filing_risk_assessment_gate_invalid")
        if str(assessment.get("risk_level") or "").lower() not in {"low", "none"}:
            errors.append("abnormal_filing_risk_assessment_must_be_low_or_none")
        if str(get_path(data, "ai_compliance_review.abnormal_filing_risk") or "").lower() == "low" and str(assessment.get("risk_level") or "").lower() != "low":
            errors.append("abnormal_filing_risk_assessment_must_match_ai_risk_level")
        artifact_ref_hash = abnormal_artifact.get("reference_patent_delta_hash") if isinstance(abnormal_artifact, dict) else None
        packet_ref_hash = assessment.get("reference_patent_delta_hash")
        if packet_ref_hash or artifact_ref_hash:
            require_hash_value(packet_ref_hash, "ai_compliance_review.abnormal_filing_risk_assessment.reference_patent_delta_hash", errors)
            require_positive_int(
                assessment.get("reference_delta_rows_count"),
                "ai_compliance_review.abnormal_filing_risk_assessment.reference_delta_rows_count",
                errors,
            )
            require_positive_int(
                assessment.get("reference_delta_claim_elements_count"),
                "ai_compliance_review.abnormal_filing_risk_assessment.reference_delta_claim_elements_count",
                errors,
            )
            if assessment.get("reference_delta_boundary_preserved") is not True:
                errors.append("reference_delta_boundary_preserved_must_be_true")
            if artifact_ref_hash and packet_ref_hash != artifact_ref_hash:
                errors.append("reference_patent_delta_hash_mismatch_with_abnormal_artifact")
            if isinstance(abnormal_artifact, dict):
                for key in ["reference_delta_rows_count", "reference_delta_claim_elements_count"]:
                    if abnormal_artifact.get(key) is not None and assessment.get(key) != abnormal_artifact.get(key):
                        errors.append(f"{key}_mismatch_with_abnormal_artifact")
    for path in LEGAL_GATE_CHECK_PATHS:
        if get_path(data, path) != "passed":
            errors.append(f"{path}_must_pass")
    stop_conditions = get_path(data, "ai_compliance_review.legal_gate_review.stop_conditions_checked")
    if isinstance(stop_conditions, list):
        missing = sorted(REQUIRED_STOP_CONDITIONS.difference(str(item) for item in stop_conditions))
        if missing:
            errors.append("legal_gate_stop_conditions_missing: " + ",".join(missing))
    else:
        errors.append("legal_gate_stop_conditions_must_be_list")
    if get_path(data, "ai_compliance_review.legal_gate_review.legal_advice_claimed") is not False:
        errors.append("ai_self_filing_must_not_claim_legal_advice")
    if get_path(data, "ai_compliance_review.legal_gate_review.lawyer_or_agent_review_claimed") is not False:
        errors.append("ai_self_filing_must_not_claim_lawyer_or_agent_review")

    actions = action_text(get_path(data, "applicant_authorization.allowed_actions"))
    if "submit" not in actions and "file" not in actions:
        errors.append("authorization_scope_missing_submit_or_file")
    if "pay" not in actions:
        warnings.append("authorization_scope_missing_pay_action")

    if get_path(data, "inventor_confirmation.contribution_confirmed") is not True:
        errors.append("inventor_contribution_must_be_confirmed")
    if get_path(data, "ownership.dispute_absent") is not True:
        errors.append("ownership_dispute_absent_must_be_true")

    secrecy_status = str(get_path(data, "secrecy_review.status") or "").lower()
    if secrecy_status not in {"not_required", "completed", "passed"}:
        errors.append("secrecy_review_status_invalid")
    if get_path(data, "secrecy_review.foreign_or_pct_planned") is True and secrecy_status != "completed":
        errors.append("foreign_or_pct_planned_requires_completed_secrecy_review")

    if get_path(data, "filing_channel.official_account_registered") is not True:
        errors.append("official_account_registered_must_be_true")
    if get_path(data, "filing_channel.automation_allowed") is not True:
        errors.append("automation_allowed_must_be_true_for_ai_self_filing")
    if get_path(data, "filing_channel.bypasses_access_controls") is not False:
        errors.append("must_not_bypass_access_controls")
    human_steps = get_path(data, "filing_channel.human_only_steps")
    if human_steps:
        errors.append("human_only_steps_must_be_empty_for_ai_self_filing_adapter")

    if get_path(data, "fees.auto_pay_authorized") is not True:
        errors.append("fees_auto_pay_authorized_must_be_true")

    if get_path(data, "decision.status") != "ready_for_package_validation":
        errors.append("decision_status_must_be_ready_for_package_validation")

    if data.get("counsel_review") or data.get("patent_agent_review") or data.get("lawyer_review"):
        errors.append("ai_self_filing_packet_must_not_use_lawyer_or_agent_review")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.packet), base_dir=args.packet.parent)
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
