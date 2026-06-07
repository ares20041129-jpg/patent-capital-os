#!/usr/bin/env python3
"""Validate workflow orchestration dry-run benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_batch_processor_result
import validate_case_queue


def require_queue_legal_gate_metadata(queue: dict, errors: list[str]) -> None:
    items = queue.get("items")
    if not isinstance(items, list):
        return
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        mode = item.get("legal_gate_mode")
        if not mode:
            errors.append(f"item_{index}_missing_legal_gate_mode")
        if item.get("external_lawyer_involved") is not False:
            errors.append(f"item_{index}_external_lawyer_involved_must_be_false")


def require_result_legal_gate_metadata(result: dict, errors: list[str]) -> None:
    rows = result.get("results")
    if not isinstance(rows, list):
        return
    for index, item in enumerate(rows, start=1):
        if not isinstance(item, dict):
            continue
        if not item.get("legal_gate_mode"):
            errors.append(f"result_{index}_missing_legal_gate_mode")
        if item.get("external_lawyer_involved") is not False:
            errors.append(f"result_{index}_external_lawyer_involved_must_be_false")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    queue_path = benchmark_dir / "case-queue.json"
    result_path = benchmark_dir / "batch-processor-result.json"
    report_path = benchmark_dir / "orchestration-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if queue_path.exists():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_case_queue.validate(queue)
        if not ok:
            errors.extend([f"case_queue: {item}" for item in errs])
        warnings.extend([f"case_queue: {item}" for item in warns])
        if queue.get("official_submission_allowed") is not False:
            errors.append("queue_must_not_allow_official_submission")
        if queue.get("official_system_touch_allowed") is not False:
            errors.append("queue_must_not_allow_official_system_touch")
        require_queue_legal_gate_metadata(queue, errors)
    else:
        errors.append(f"missing_file: {queue_path}")

    if result_path.exists():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_batch_processor_result.validate(result)
        if not ok:
            errors.extend([f"batch_result: {item}" for item in errs])
        warnings.extend([f"batch_result: {item}" for item in warns])
        if result.get("official_system_touched") is not False:
            errors.append("batch_result_must_not_touch_official_system")
        if result.get("official_submission_performed") is not False:
            errors.append("batch_result_must_not_perform_official_submission")
        if result.get("batch_errors"):
            errors.append("batch_result_must_not_have_batch_errors")
        require_result_legal_gate_metadata(result, errors)
    else:
        errors.append(f"missing_file: {result_path}")

    if queue_path.exists() and result_path.exists():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        result = json.loads(result_path.read_text(encoding="utf-8"))
        queue_ids = {item.get("case_id") for item in queue.get("items", []) if isinstance(item, dict)}
        result_ids = {item.get("case_id") for item in result.get("results", []) if isinstance(item, dict)}
        if queue_ids != result_ids:
            errors.append("queue_result_case_id_set_mismatch")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "workflow orchestration report",
            "offline orchestration only: yes",
            "official system touched: no",
            "official submission performed: no",
            "external professional involved: no",
            "legal gate metadata: present",
            "per-case results",
        ]:
            if needle not in text:
                errors.append(f"orchestration_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

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
