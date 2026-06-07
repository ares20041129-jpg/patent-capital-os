#!/usr/bin/env python3
"""Validate case queue batch processor benchmark."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import validate_artifact_hash_manifest
import validate_batch_processor_result
import validate_case_queue


PROHIBITED_AI_ONLY_DEFAULT_TERMS = re.compile(
    r"\b(attorney|lawyer|counsel)\b|patent-agent|patent agent|counsel_review_needed",
    re.IGNORECASE,
)


def require_no_default_review_terms(text: str, label: str, errors: list[str]) -> None:
    if PROHIBITED_AI_ONLY_DEFAULT_TERMS.search(text):
        errors.append(f"{label}_must_not_default_to_lawyer_or_patent_agent_review")


def require_legal_gate_metadata(rows: list, label: str, errors: list[str]) -> None:
    for index, item in enumerate(rows, start=1):
        if not isinstance(item, dict):
            continue
        if not item.get("legal_gate_mode"):
            errors.append(f"{label}_{index}_missing_legal_gate_mode")
        if item.get("external_lawyer_involved") is not False:
            errors.append(f"{label}_{index}_external_lawyer_involved_must_be_false")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    queue_path = benchmark_dir / "case-queue.json"
    result_path = benchmark_dir / "batch-processor-result.json"
    runner_result_path = benchmark_dir / "runner-result.json"
    report_path = benchmark_dir / "batch-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if queue_path.exists():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_case_queue.validate(queue)
        if not ok:
            errors.extend([f"case_queue: {item}" for item in errs])
        warnings.extend([f"case_queue: {item}" for item in warns])
        require_legal_gate_metadata(queue.get("items", []), "queue_item", errors)
    else:
        errors.append(f"missing_file: {queue_path}")

    if result_path.exists():
        result_text = result_path.read_text(encoding="utf-8")
        result_data = json.loads(result_text)
        ok, errs, warns = validate_batch_processor_result.validate(result_data)
        if not ok:
            errors.extend([f"batch_result: {item}" for item in errs])
        warnings.extend([f"batch_result: {item}" for item in warns])
        require_no_default_review_terms(result_text, "batch_result", errors)
        require_legal_gate_metadata(result_data.get("results", []), "batch_result", errors)
    else:
        errors.append(f"missing_file: {result_path}")

    if queue_path.exists() and result_path.exists():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        result = json.loads(result_path.read_text(encoding="utf-8"))
        queue_ids = {item["case_id"] for item in queue.get("items", []) if isinstance(item, dict) and item.get("case_id")}
        result_ids = {item["case_id"] for item in result.get("results", []) if isinstance(item, dict) and item.get("case_id")}
        if queue_ids != result_ids:
            errors.append("queue_result_case_id_set_mismatch")
        if queue.get("queue_id") != result.get("queue_id"):
            errors.append("queue_id_mismatch")

    if runner_result_path.exists():
        runner_text = runner_result_path.read_text(encoding="utf-8")
        runner_result = json.loads(runner_text)
        ok, errs, warns = validate_batch_processor_result.validate(runner_result)
        if not ok:
            errors.extend([f"runner_result: {item}" for item in errs])
        warnings.extend([f"runner_result: {item}" for item in warns])
        require_no_default_review_terms(runner_text, "runner_result", errors)
        require_legal_gate_metadata(runner_result.get("results", []), "runner_result", errors)
        if queue_path.exists():
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
            queue_ids = {item["case_id"] for item in queue.get("items", []) if isinstance(item, dict) and item.get("case_id")}
            runner_ids = {item["case_id"] for item in runner_result.get("results", []) if isinstance(item, dict) and item.get("case_id")}
            if queue_ids != runner_ids:
                errors.append("queue_runner_case_id_set_mismatch")
            if queue.get("queue_id") != runner_result.get("queue_id"):
                errors.append("queue_runner_id_mismatch")
        if runner_result.get("batch_errors"):
            errors.append("runner_result_batch_errors_present")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "execution mode: dry_run",
            "official system touched: no",
            "official submission performed: no",
            "external professional involved: no",
            "legal gate metadata: present",
            "per-case results",
            "ai self-filing legal/compliance authorization",
        ]:
            if needle not in text:
                errors.append(f"batch_report_missing_text: {needle}")
        require_no_default_review_terms(text, "batch_report", errors)
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        warnings.append("artifact_hashes_missing_until_manifest_generated")

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
