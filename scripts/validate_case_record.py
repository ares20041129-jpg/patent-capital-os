#!/usr/bin/env python3
"""Validate a Patent Capital OS case processor record."""

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
    "submitted_pending_receipt",
    "official_receipt_received",
    "accepted_or_application_number_received",
}

REQUIRED_BY_TARGET = {
    "draft_only": ["source_material_manifest", "invention_disclosure", "patent_application_draft", "claim_support_map", "filing_status"],
    "ready_for_package_validation": ["submission_authorization_packet", "filing_status"],
    "package_valid_official_preflight_pending": ["submission_authorization_packet", "filing_package_manifest", "filing_status"],
    "ready_for_authorized_filing": ["submission_authorization_packet", "filing_package_manifest", "official_channel_preflight", "receipt_capture", "filing_status"],
    "submitted_pending_receipt": ["submission_authorization_packet", "filing_package_manifest", "official_channel_preflight", "receipt_capture", "filing_status"],
    "official_receipt_received": ["receipt_capture", "filing_status"],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ["case_id", "previous_status", "current_status", "target_status", "decision", "execution_mode", "case_owner"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    current = data.get("current_status")
    target = data.get("target_status")
    if current and current not in ALLOWED_STATUSES:
        errors.append("current_status_invalid")
    if target and target not in ALLOWED_STATUSES:
        errors.append("target_status_invalid")

    execution_mode = data.get("execution_mode")
    if execution_mode not in {"handoff", "dry_run", "adapter"}:
        errors.append("execution_mode_invalid")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("artifacts_must_be_object")
        artifacts = {}

    for key in REQUIRED_BY_TARGET.get(str(target), []):
        if is_blank(artifacts.get(key)):
            errors.append(f"target_{target}_missing_artifact: {key}")

    validators_required = data.get("validators_required")
    validators_run = data.get("validators_run")
    if not isinstance(validators_required, list) or not validators_required:
        errors.append("validators_required_missing")
    if not isinstance(validators_run, list):
        errors.append("validators_run_must_be_list")
        validators_run = []

    missing_validators = sorted(set(validators_required or []) - set(validators_run or []))
    if missing_validators:
        errors.append("validators_not_run: " + ",".join(missing_validators))

    if target == "ready_for_authorized_filing" and data.get("decision") != "ready_for_authorized_filing":
        errors.append("decision_must_match_ready_for_authorized_filing")

    if target == "submitted_pending_receipt" and execution_mode == "dry_run":
        errors.append("dry_run_cannot_target_submitted_pending_receipt")

    next_allowed = data.get("next_allowed_states")
    if not isinstance(next_allowed, list) or not next_allowed:
        warnings.append("next_allowed_states_missing")

    audit = data.get("audit")
    if not isinstance(audit, dict) or is_blank(audit.get("audit_log_entry")):
        warnings.append("audit_log_entry_missing")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_record", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.case_record))
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
