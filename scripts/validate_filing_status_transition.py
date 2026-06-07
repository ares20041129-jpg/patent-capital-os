#!/usr/bin/env python3
"""Validate filing status transitions and evidence boundaries."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

ORDER = [
    "intake_received",
    "draft_only",
    "legal_gate_failed",
    "ready_for_package_validation",
    "package_valid_official_preflight_pending",
    "ready_for_authorized_filing",
    "approved_for_adapter_execution",
    "submitted_pending_receipt",
    "official_receipt_received",
    "accepted_or_application_number_received",
]

PRE_OFFICIAL_ACTION_STATUSES = {
    "intake_received",
    "draft_only",
    "legal_gate_failed",
    "ready_for_package_validation",
    "package_valid_official_preflight_pending",
    "ready_for_authorized_filing",
    "approved_for_adapter_execution",
}

POST_SUBMISSION_STATUSES = {
    "submitted_pending_receipt",
    "official_receipt_received",
    "accepted_or_application_number_received",
}

LEGAL_GATE_MODES = {
    "ai_self_filing_no_external_lawyer",
    "counsel_or_agent_review",
}

ALLOWED_TRANSITIONS = {
    "intake_received": {"draft_only", "legal_gate_failed", "ready_for_package_validation"},
    "draft_only": {"legal_gate_failed", "ready_for_package_validation"},
    "legal_gate_failed": {"draft_only", "ready_for_package_validation"},
    "ready_for_package_validation": {"package_valid_official_preflight_pending", "legal_gate_failed"},
    "package_valid_official_preflight_pending": {"ready_for_authorized_filing", "legal_gate_failed"},
    "ready_for_authorized_filing": {"approved_for_adapter_execution", "submitted_pending_receipt"},
    "approved_for_adapter_execution": {"submitted_pending_receipt"},
    "submitted_pending_receipt": {"official_receipt_received"},
    "official_receipt_received": {"accepted_or_application_number_received"},
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    previous = data.get("previous_status")
    current = data.get("status")
    if previous and current:
        if current not in ALLOWED_TRANSITIONS.get(previous, set()):
            errors.append(f"invalid_transition: {previous} -> {current}")
    elif not current:
        errors.append("missing_required_field: status")

    if current not in ORDER:
        errors.append("status_not_in_allowed_statuses")

    legal_gate_mode = data.get("legal_gate_mode")
    if legal_gate_mode and legal_gate_mode not in LEGAL_GATE_MODES:
        errors.append("legal_gate_mode_not_allowed")

    if legal_gate_mode == "ai_self_filing_no_external_lawyer" and data.get("external_lawyer_involved") is not False:
        errors.append("ai_self_filing_requires_external_lawyer_involved_false")
    elif data.get("external_lawyer_involved") is True:
        errors.append("external_lawyer_involved_must_not_be_true")

    if data.get("generator_official_system_touched") is True:
        errors.append("generator_must_not_touch_official_system")
    if data.get("generator_official_submission_performed") is True:
        errors.append("generator_must_not_perform_official_submission")

    if current in PRE_OFFICIAL_ACTION_STATUSES:
        if data.get("official_system_touched") is not False:
            errors.append("pre_official_status_requires_official_system_touched_false")
        if data.get("official_submission_performed") is not False:
            errors.append("pre_official_status_requires_official_submission_performed_false")

    if current in POST_SUBMISSION_STATUSES:
        if data.get("official_system_touched") is not True:
            errors.append("post_submission_status_requires_official_system_touched_true")
        if data.get("official_submission_performed") is not True:
            errors.append("post_submission_status_requires_official_submission_performed_true")

    final_hash = data.get("final_package_hash")
    reviewed_hash = data.get("reviewed_package_hash")
    if current in {"ready_for_authorized_filing", "approved_for_adapter_execution", "submitted_pending_receipt", "official_receipt_received", "accepted_or_application_number_received"}:
        if not final_hash or not reviewed_hash:
            errors.append("ready_or_later_status_requires_final_and_reviewed_hash")
        elif not SHA256_RE.fullmatch(str(final_hash)) or not SHA256_RE.fullmatch(str(reviewed_hash)):
            errors.append("ready_or_later_status_requires_exact_final_and_reviewed_sha256")
        elif final_hash != reviewed_hash:
            errors.append("hash_mismatch: final_package_hash != reviewed_package_hash")

    if current == "ready_for_authorized_filing":
        if data.get("legal_gate") != "passed":
            errors.append("ready_for_authorized_filing_requires_legal_gate_passed")
        if data.get("official_channel_preflight") != "passed":
            errors.append("ready_for_authorized_filing_requires_official_channel_preflight_passed")
        if data.get("official_submission_performed") is not False:
            errors.append("ready_for_authorized_filing_must_not_have_submission_performed")
        if data.get("official_receipt_hash") or data.get("application_number"):
            errors.append("ready_for_authorized_filing_must_not_have_receipt_or_application_number")

    if current == "approved_for_adapter_execution":
        if data.get("legal_gate") != "passed":
            errors.append("approved_adapter_execution_requires_legal_gate_passed")
        if data.get("official_channel_preflight") != "passed":
            errors.append("approved_adapter_execution_requires_official_channel_preflight_passed")
        if data.get("approved_adapter_preflight") != "passed":
            errors.append("approved_adapter_execution_requires_approved_adapter_preflight_passed")
        if data.get("official_system_touched") is not False:
            errors.append("approved_adapter_execution_must_not_have_touched_official_system")
        if data.get("official_submission_performed") is not False:
            errors.append("approved_adapter_execution_must_not_have_submission_performed")
        if data.get("adapter_execution_performed") is not False:
            errors.append("approved_adapter_execution_must_not_have_adapter_execution_performed")
        if data.get("official_receipt_hash") or data.get("application_number"):
            errors.append("approved_adapter_execution_must_not_have_receipt_or_application_number")

    if current == "submitted_pending_receipt":
        if data.get("official_submission_performed") is not True:
            errors.append("submitted_pending_receipt_requires_submission_performed_true")
        if data.get("official_receipt_hash"):
            errors.append("submitted_pending_receipt_must_not_have_receipt_hash")
        if data.get("application_number"):
            errors.append("submitted_pending_receipt_must_not_have_application_number")

    if current in {"official_receipt_received", "accepted_or_application_number_received"}:
        if data.get("official_submission_performed") is not True:
            errors.append("receipt_status_requires_submission_performed_true")
        if is_blank(data.get("official_receipt_hash")):
            errors.append("receipt_status_requires_official_receipt_hash")
        if current == "accepted_or_application_number_received" and is_blank(data.get("application_number")):
            errors.append("accepted_status_requires_application_number")

    if current == "legal_gate_failed" and not data.get("failed_gates"):
        warnings.append("legal_gate_failed_without_failed_gates_list")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("status_file", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.status_file))
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
