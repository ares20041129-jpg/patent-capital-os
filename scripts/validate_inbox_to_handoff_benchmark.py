#!/usr/bin/env python3
"""Validate an inbox-to-handoff batch benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_batch_processor_result
import validate_case_queue
import validate_pre_submission_to_handoff_benchmark


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    result_path = benchmark_dir / "inbox-to-handoff-result.json"
    report_path = benchmark_dir / "inbox-to-handoff-report.md"
    queue_path = benchmark_dir / "case-queue.json"
    batch_result_path = benchmark_dir / "batch-processor-result.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    processed_dir = benchmark_dir / "processed-cases"

    result: dict[str, Any] = {}
    if result_path.exists():
        result = load_json(result_path)
        if result.get("ok") is not True:
            errors.append("inbox_to_handoff_result_ok_must_be_true")
        if result.get("pipeline_type") != "inbox_to_handoff_ai_self_filing_no_external_lawyer":
            errors.append("inbox_to_handoff_pipeline_type_invalid")
        if result.get("status") != "approved_for_adapter_execution":
            errors.append("inbox_to_handoff_status_must_remain_approved_for_adapter_execution")
        if result.get("decision") != "handoff_ready_no_auto_submit":
            errors.append("inbox_to_handoff_decision_must_be_handoff_ready_no_auto_submit")
        if result.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("inbox_to_handoff_legal_gate_mode_invalid")
        for field in [
            "external_lawyer_involved",
            "official_system_touched",
            "official_submission_performed",
            "adapter_execution_performed",
            "automatic_submission_performed",
        ]:
            if result.get(field) is not False:
                errors.append(f"inbox_to_handoff_{field}_must_be_false")
    else:
        errors.append(f"missing_file: {result_path}")

    if processed_dir.exists():
        case_dirs = sorted(item for item in processed_dir.iterdir() if item.is_dir())
        if not case_dirs:
            errors.append("processed_cases_must_be_nonempty")
        for case_dir in case_dirs:
            ok, errs, warns = validate_pre_submission_to_handoff_benchmark.validate(case_dir)
            if not ok:
                errors.extend([f"processed_case:{case_dir.name}: {item}" for item in errs])
            warnings.extend([f"processed_case:{case_dir.name}: {item}" for item in warns])
    else:
        errors.append(f"missing_dir: {processed_dir}")
        case_dirs = []

    case_results = result.get("case_results") if isinstance(result.get("case_results"), list) else []
    if not case_results:
        errors.append("case_results_must_be_nonempty_list")
    elif processed_dir.exists() and len(case_results) != len(case_dirs):
        errors.append("case_results_count_must_match_processed_cases")

    seen_case_ids: set[str] = set()
    reference_delta_seen = False
    for index, item in enumerate(case_results, start=1):
        if not isinstance(item, dict):
            errors.append(f"case_result_{index}_must_be_object")
            continue
        case_id = str(item.get("case_id") or "")
        if not case_id:
            errors.append(f"case_result_{index}_case_id_missing")
        if case_id in seen_case_ids:
            errors.append(f"duplicate_case_id: {case_id}")
        seen_case_ids.add(case_id)
        if item.get("ok") is not True:
            errors.append(f"case_result_{index}_ok_must_be_true")
        if item.get("decision") != "handoff_ready_no_auto_submit":
            errors.append(f"case_result_{index}_decision_invalid")
        if item.get("reference_delta_source"):
            reference_delta_seen = True
        output_dir_raw = item.get("output_dir")
        if not isinstance(output_dir_raw, str) or not output_dir_raw:
            errors.append(f"case_result_{index}_output_dir_missing")
            continue
        output_dir = Path(output_dir_raw)
        if not output_dir.is_absolute():
            output_dir = (benchmark_dir / output_dir).resolve()
        if not output_dir.exists() or not output_dir.is_dir():
            errors.append(f"case_result_{index}_output_dir_missing_on_disk")
        else:
            try:
                output_dir.resolve().relative_to(benchmark_dir.resolve())
            except ValueError:
                errors.append(f"case_result_{index}_output_dir_outside_benchmark")

    if not reference_delta_seen:
        errors.append("inbox_to_handoff_reference_delta_case_missing")

    if queue_path.exists():
        ok, errs, warns = validate_case_queue.validate(load_json(queue_path))
        if not ok:
            errors.extend([f"case_queue: {item}" for item in errs])
        warnings.extend([f"case_queue: {item}" for item in warns])
        queue = load_json(queue_path)
        if queue.get("official_submission_allowed") is not False:
            errors.append("case_queue_must_not_allow_official_submission")
        if queue.get("official_system_touch_allowed") is not False:
            errors.append("case_queue_must_not_allow_official_touch")
        for item in queue.get("items", []):
            if not isinstance(item, dict):
                continue
            if item.get("expected_outcome") != "pre_submission_to_handoff":
                errors.append("case_queue_items_must_validate_pre_submission_to_handoff_cases")
            if item.get("external_lawyer_involved") is not False:
                errors.append("case_queue_item_external_lawyer_must_be_false")
    else:
        errors.append(f"missing_file: {queue_path}")

    if batch_result_path.exists():
        ok, errs, warns = validate_batch_processor_result.validate(load_json(batch_result_path))
        if not ok:
            errors.extend([f"batch_processor_result: {item}" for item in errs])
        warnings.extend([f"batch_processor_result: {item}" for item in warns])
        batch_result = load_json(batch_result_path)
        summary = batch_result.get("summary") if isinstance(batch_result.get("summary"), dict) else {}
        if summary.get("blocked") != 0 or summary.get("deficiency") != 0:
            errors.append("batch_result_must_not_have_blocked_or_deficiency_cases")
        if batch_result.get("official_system_touched") is not False:
            errors.append("batch_result_official_system_touched_must_be_false")
        if batch_result.get("official_submission_performed") is not False:
            errors.append("batch_result_official_submission_performed_must_be_false")
    else:
        errors.append(f"missing_file: {batch_result_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "inbox to handoff report",
            "pipeline status: pass",
            "ai self-filing",
            "official system touched: no",
            "official submission performed: no",
            "adapter execution performed: no",
            "automatic submission performed: no",
            "external lawyer involved: no",
            "read-only handoff packages",
            "does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number",
        ]:
            if needle not in text:
                errors.append(f"inbox_to_handoff_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
        manifest = load_json(hashes_path)
        manifest_paths = {item.get("path") for item in manifest.get("files", []) if isinstance(item, dict)}
        for required in [
            "case-queue.json",
            "batch-processor-result.json",
            "inbox-to-handoff-result.json",
            "inbox-to-handoff-report.md",
        ]:
            if required not in manifest_paths:
                errors.append(f"artifact_manifest_missing_required_path: {required}")
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
