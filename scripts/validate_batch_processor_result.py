#!/usr/bin/env python3
"""Validate batch processor result summaries."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


SUBMISSION_STATUSES = {
    "submitted_pending_receipt",
    "official_receipt_received",
    "accepted_or_application_number_received",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ["queue_id", "processed_at", "execution_mode", "summary", "results"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    execution_mode = data.get("execution_mode")
    if execution_mode not in {"dry_run", "handoff", "approved_adapter"}:
        errors.append("execution_mode_invalid")

    if execution_mode in {"dry_run", "handoff"}:
        if data.get("official_system_touched") is not False:
            errors.append("dry_run_or_handoff_must_not_touch_official_system")
        if data.get("official_submission_performed") is not False:
            errors.append("dry_run_or_handoff_must_not_perform_official_submission")
    if execution_mode == "approved_adapter":
        if data.get("approved_adapter_evidence_mode") is not True:
            errors.append("approved_adapter_result_requires_evidence_mode")
        if data.get("official_system_touched") is not False:
            errors.append("approved_adapter_evidence_result_must_not_touch_official_system")
        if data.get("official_submission_performed") is not False:
            errors.append("approved_adapter_evidence_result_must_not_perform_official_submission")
        if data.get("generator_official_system_touched") is not False:
            errors.append("approved_adapter_evidence_generator_must_not_touch_official_system")
        if data.get("generator_official_submission_performed") is not False:
            errors.append("approved_adapter_evidence_generator_must_not_perform_official_submission")
        if data.get("generator_adapter_execution_performed") is not False:
            errors.append("approved_adapter_evidence_generator_must_not_perform_adapter_execution")

    results = data.get("results")
    if not isinstance(results, list) or not results:
        errors.append("results_must_be_nonempty_list")
        return False, errors, warnings

    seen: set[str] = set()
    counters = Counter()
    for index, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            errors.append(f"result_{index}_must_be_object")
            continue
        for key in ["case_id", "input_status", "output_status", "decision", "outcome", "validators_run", "next_action", "owner"]:
            if is_blank(item.get(key)):
                errors.append(f"result_{index}_missing_required_field: {key}")
        case_id = str(item.get("case_id") or "")
        if case_id in seen:
            errors.append(f"duplicate_case_id: {case_id}")
        seen.add(case_id)
        outcome = str(item.get("outcome") or "")
        counters[outcome] += 1
        if not isinstance(item.get("validators_run"), list) or not item.get("validators_run"):
            errors.append(f"result_{index}_validators_run_must_be_nonempty_list")
        if execution_mode in {"dry_run", "handoff"}:
            if item.get("official_system_touched") is not False:
                errors.append(f"result_{index}_must_not_touch_official_system")
            if item.get("official_submission_performed") is not False:
                errors.append(f"result_{index}_must_not_perform_official_submission")
            readonly_evidence_audit = (
                item.get("expected_outcome")
                in {"adapter_execution", "application_number", "lifecycle_audit", "official_session_authorization", "production_adapter_readiness", "production_official_evidence", "receipt_capture"}
                and item.get("input_status") == item.get("output_status")
            )
            if item.get("output_status") in SUBMISSION_STATUSES and not readonly_evidence_audit:
                errors.append(f"result_{index}_must_not_output_submission_status")
        if execution_mode == "approved_adapter":
            if item.get("official_system_touched") is not False:
                errors.append(f"result_{index}_approved_adapter_evidence_must_not_touch_official_system")
            if item.get("official_submission_performed") is not False:
                errors.append(f"result_{index}_approved_adapter_evidence_must_not_perform_official_submission")
            if item.get("generator_official_system_touched") is not False:
                errors.append(f"result_{index}_approved_adapter_evidence_generator_must_not_touch_official_system")
            if item.get("generator_official_submission_performed") is not False:
                errors.append(f"result_{index}_approved_adapter_evidence_generator_must_not_perform_official_submission")
            if item.get("generator_adapter_execution_performed") is not False:
                errors.append(f"result_{index}_approved_adapter_evidence_generator_must_not_perform_adapter_execution")
            if item.get("expected_outcome") != "adapter_execution":
                errors.append(f"result_{index}_approved_adapter_evidence_requires_adapter_execution_outcome")
            if item.get("input_status") != "submitted_pending_receipt" or item.get("output_status") != "submitted_pending_receipt":
                errors.append(f"result_{index}_approved_adapter_evidence_requires_readonly_submitted_pending_receipt")

    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    if summary.get("total") != len(results):
        errors.append("summary_total_mismatch")
    if summary.get("passed") != counters["passed"]:
        errors.append("summary_passed_mismatch")
    if summary.get("blocked") != counters["blocked"]:
        errors.append("summary_blocked_mismatch")
    if summary.get("handoff") != counters["handoff"]:
        errors.append("summary_handoff_mismatch")
    if summary.get("deficiency") != counters["deficiency"]:
        errors.append("summary_deficiency_mismatch")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.result))
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
