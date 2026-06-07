#!/usr/bin/env python3
"""Validate approved-adapter evidence-only queue benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_batch_processor_result
import validate_case_queue


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    queue_path = benchmark_dir / "case-queue.json"
    result_path = benchmark_dir / "runner-result.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if queue_path.exists():
        queue = load_json(queue_path)
        ok, errs, warns = validate_case_queue.validate(queue)
        if not ok:
            errors.extend([f"case_queue: {item}" for item in errs])
        warnings.extend([f"case_queue: {item}" for item in warns])

        if queue.get("execution_mode") != "approved_adapter":
            errors.append("queue_execution_mode_must_be_approved_adapter")
        if queue.get("approved_adapter_evidence_mode") is not True:
            errors.append("queue_must_enable_approved_adapter_evidence_mode")
        if queue.get("official_system_touch_allowed") is not False:
            errors.append("queue_must_not_allow_official_system_touch")
        if queue.get("official_submission_allowed") is not False:
            errors.append("queue_must_not_allow_official_submission")

        items = queue.get("items")
        if not isinstance(items, list) or len(items) != 1:
            errors.append("queue_must_have_one_evidence_item")
        else:
            item = items[0]
            if item.get("current_status") != "submitted_pending_receipt":
                errors.append("queue_item_current_status_must_be_submitted_pending_receipt")
            if item.get("target_status") != "submitted_pending_receipt":
                errors.append("queue_item_target_status_must_be_submitted_pending_receipt")
            if item.get("expected_outcome") != "adapter_execution":
                errors.append("queue_item_expected_outcome_must_be_adapter_execution")
            if item.get("external_lawyer_involved") is not False:
                errors.append("queue_item_external_lawyer_involved_must_be_false")
            validators = item.get("required_validators")
            if "validate_generated_adapter_execution_result_benchmark" not in (validators or []):
                errors.append("queue_item_missing_generated_adapter_execution_validator")
    else:
        errors.append(f"missing_file: {queue_path}")

    if result_path.exists():
        result = load_json(result_path)
        ok, errs, warns = validate_batch_processor_result.validate(result)
        if not ok:
            errors.extend([f"runner_result: {item}" for item in errs])
        warnings.extend([f"runner_result: {item}" for item in warns])

        if result.get("execution_mode") != "approved_adapter":
            errors.append("runner_result_execution_mode_must_be_approved_adapter")
        if result.get("approved_adapter_evidence_mode") is not True:
            errors.append("runner_result_must_enable_approved_adapter_evidence_mode")
        for field in [
            "official_system_touched",
            "official_submission_performed",
            "generator_official_system_touched",
            "generator_official_submission_performed",
            "generator_adapter_execution_performed",
        ]:
            if result.get(field) is not False:
                errors.append(f"runner_result_{field}_must_be_false")
        if result.get("batch_errors"):
            errors.append("runner_result_batch_errors_present")

        rows = result.get("results")
        if not isinstance(rows, list) or len(rows) != 1:
            errors.append("runner_result_must_have_one_evidence_row")
        else:
            row = rows[0]
            if row.get("decision") != "adapter_execution_result_captured":
                errors.append("runner_result_decision_must_capture_adapter_execution")
            if row.get("outcome") != "passed":
                errors.append("runner_result_outcome_must_pass")
            if row.get("input_status") != "submitted_pending_receipt":
                errors.append("runner_result_input_status_must_be_submitted_pending_receipt")
            if row.get("output_status") != "submitted_pending_receipt":
                errors.append("runner_result_output_status_must_be_submitted_pending_receipt")
            if row.get("external_lawyer_involved") is not False:
                errors.append("runner_result_external_lawyer_involved_must_be_false")
            for field in [
                "official_system_touched",
                "official_submission_performed",
                "generator_official_system_touched",
                "generator_official_submission_performed",
                "generator_adapter_execution_performed",
            ]:
                if row.get(field) is not False:
                    errors.append(f"runner_result_row_{field}_must_be_false")
            validators = row.get("validators_run")
            if "validate_generated_adapter_execution_result_benchmark" not in (validators or []):
                errors.append("runner_result_missing_generated_adapter_execution_validator")
    else:
        errors.append(f"missing_file: {result_path}")

    if queue_path.exists() and result_path.exists():
        queue = load_json(queue_path)
        result = load_json(result_path)
        if queue.get("queue_id") != result.get("queue_id"):
            errors.append("queue_runner_id_mismatch")

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
