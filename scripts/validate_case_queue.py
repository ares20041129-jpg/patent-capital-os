#!/usr/bin/env python3
"""Validate a case queue for batch processing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {
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
}

SUBMISSION_STATUSES = {
    "submitted_pending_receipt",
    "official_receipt_received",
    "accepted_or_application_number_received",
}

APPROVED_ADAPTER_EVIDENCE_OUTCOMES = {"adapter_execution"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ["queue_id", "created_at", "execution_mode", "queue_owner", "items"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    execution_mode = data.get("execution_mode")
    if execution_mode not in {"dry_run", "handoff", "approved_adapter"}:
        errors.append("execution_mode_invalid")

    submission_allowed = data.get("official_submission_allowed") is True
    touch_allowed = data.get("official_system_touch_allowed") is True
    if execution_mode in {"dry_run", "handoff"}:
        if submission_allowed:
            errors.append("dry_run_or_handoff_queue_must_not_allow_official_submission")
        if touch_allowed:
            errors.append("dry_run_or_handoff_queue_must_not_allow_official_system_touch")
    if execution_mode == "approved_adapter":
        if data.get("approved_adapter_evidence_mode") is not True:
            errors.append("approved_adapter_queue_requires_evidence_mode")
        if submission_allowed:
            errors.append("approved_adapter_evidence_queue_must_not_allow_official_submission")
        if touch_allowed:
            errors.append("approved_adapter_evidence_queue_must_not_allow_official_system_touch")

    items = data.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items_must_be_nonempty_list")
        return False, errors, warnings

    seen: set[str] = set()
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"item_{index}_must_be_object")
            continue
        for key in ["case_id", "priority", "current_status", "target_status", "expected_outcome", "owner", "required_validators"]:
            if is_blank(item.get(key)):
                errors.append(f"item_{index}_missing_required_field: {key}")
        case_id = str(item.get("case_id") or "")
        if case_id in seen:
            errors.append(f"duplicate_case_id: {case_id}")
        seen.add(case_id)
        current = item.get("current_status")
        target = item.get("target_status")
        if current not in ALLOWED_STATUSES:
            errors.append(f"item_{index}_current_status_invalid")
        if target not in ALLOWED_STATUSES:
            errors.append(f"item_{index}_target_status_invalid")
        readonly_evidence_audit = (
            item.get("expected_outcome")
            in {"adapter_execution", "application_number", "lifecycle_audit", "official_session_authorization", "production_adapter_readiness", "production_official_evidence", "receipt_capture"}
            and current == target
        )
        if execution_mode in {"dry_run", "handoff"} and target in SUBMISSION_STATUSES and not readonly_evidence_audit:
            errors.append(f"item_{index}_dry_run_or_handoff_cannot_target_submission_status")
        if execution_mode == "approved_adapter":
            if item.get("expected_outcome") not in APPROVED_ADAPTER_EVIDENCE_OUTCOMES:
                errors.append(f"item_{index}_approved_adapter_evidence_requires_adapter_execution_outcome")
            if current != "submitted_pending_receipt" or target != "submitted_pending_receipt" or current != target:
                errors.append(f"item_{index}_approved_adapter_evidence_requires_readonly_submitted_pending_receipt")
        validators = item.get("required_validators")
        if not isinstance(validators, list) or not validators:
            errors.append(f"item_{index}_required_validators_must_be_nonempty_list")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("queue", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.queue))
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
