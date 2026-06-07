#!/usr/bin/env python3
"""Validate an inbox handoff index benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_inbox_to_handoff_benchmark


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_path(raw: Any, base: Path) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        return path.resolve()
    return (base / path).resolve()


def validate_artifact_ref(
    ref: Any,
    base: Path,
    label: str,
    errors: list[str],
) -> Path | None:
    if not isinstance(ref, dict):
        errors.append(f"{label}_artifact_ref_must_be_object")
        return None
    raw_path = ref.get("path")
    expected_hash = ref.get("sha256")
    if not isinstance(raw_path, str) or not raw_path:
        errors.append(f"{label}_path_missing")
        return None
    if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
        errors.append(f"{label}_sha256_invalid")
        return None
    path = resolve_path(raw_path, base)
    if not path.exists() or not path.is_file():
        errors.append(f"{label}_file_missing")
        return path
    if sha256_file(path) != expected_hash:
        errors.append(f"{label}_hash_mismatch")
    return path


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    index_path = benchmark_dir / "inbox-handoff-index.json"
    report_path = benchmark_dir / "inbox-handoff-index.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if not index_path.exists():
        return False, [f"missing_file: {index_path}"], warnings
    index = load_json(index_path)

    if index.get("ok") is not True:
        errors.append("inbox_handoff_index_ok_must_be_true")
    if index.get("index_type") != "inbox_handoff_index_ai_self_filing_no_external_lawyer":
        errors.append("inbox_handoff_index_type_invalid")
    if index.get("status") != "approved_for_adapter_execution":
        errors.append("inbox_handoff_index_status_must_remain_approved_for_adapter_execution")
    if index.get("decision") != "handoff_index_ready_no_auto_submit":
        errors.append("inbox_handoff_index_decision_invalid")
    if index.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("inbox_handoff_index_legal_gate_mode_invalid")
    for field in [
        "external_lawyer_involved",
        "official_system_touched",
        "official_submission_performed",
        "adapter_execution_performed",
        "automatic_submission_performed",
    ]:
        if index.get(field) is not False:
            errors.append(f"inbox_handoff_index_{field}_must_be_false")

    source_dir_raw = index.get("source_inbox_dir")
    if not isinstance(source_dir_raw, str) or not source_dir_raw:
        errors.append("source_inbox_dir_missing")
        source_dir = benchmark_dir
    else:
        source_dir = resolve_path(source_dir_raw, benchmark_dir)
        if not source_dir.exists() or not source_dir.is_dir():
            errors.append("source_inbox_dir_missing_on_disk")
        else:
            ok, errs, warns = validate_inbox_to_handoff_benchmark.validate(source_dir)
            if not ok:
                errors.extend([f"source_inbox_to_handoff: {item}" for item in errs])
            warnings.extend([f"source_inbox_to_handoff: {item}" for item in warns])

    source_result_path = source_dir / "inbox-to-handoff-result.json"
    batch_result_path = source_dir / "batch-processor-result.json"
    source_result = load_json(source_result_path) if source_result_path.exists() else {}
    batch_result = load_json(batch_result_path) if batch_result_path.exists() else {}
    batch_by_case = {
        str(item.get("case_id")): item
        for item in batch_result.get("results", [])
        if isinstance(item, dict) and item.get("case_id")
    }

    source_artifacts = index.get("source_artifacts") if isinstance(index.get("source_artifacts"), dict) else {}
    for key in ["inbox_to_handoff_result", "case_queue", "batch_processor_result", "source_artifact_hashes"]:
        validate_artifact_ref(source_artifacts.get(key), benchmark_dir, f"source_artifacts_{key}", errors)

    source_cases = source_result.get("case_results") if isinstance(source_result.get("case_results"), list) else []
    cases = index.get("cases") if isinstance(index.get("cases"), list) else []
    summary = index.get("summary") if isinstance(index.get("summary"), dict) else {}
    if not cases:
        errors.append("inbox_handoff_index_cases_must_be_nonempty")
    if len(cases) != len(source_cases):
        errors.append("inbox_handoff_index_case_count_must_match_source")
    if summary.get("total") != len(cases):
        errors.append("inbox_handoff_index_summary_total_mismatch")
    if summary.get("passed") != len(cases):
        errors.append("inbox_handoff_index_summary_passed_mismatch")
    if summary.get("blocked") != 0:
        errors.append("inbox_handoff_index_summary_blocked_must_be_zero")

    source_by_case = {
        str(item.get("case_id")): item
        for item in source_cases
        if isinstance(item, dict) and item.get("case_id")
    }
    reference_delta_seen = False
    seen: set[str] = set()
    for index_number, item in enumerate(cases, start=1):
        if not isinstance(item, dict):
            errors.append(f"case_{index_number}_must_be_object")
            continue
        case_id = str(item.get("case_id") or "")
        if not case_id:
            errors.append(f"case_{index_number}_case_id_missing")
        if case_id in seen:
            errors.append(f"duplicate_case_id: {case_id}")
        seen.add(case_id)
        source_case = source_by_case.get(case_id, {})
        if not source_case:
            errors.append(f"case_{index_number}_missing_in_source_result")
        if item.get("status") != "approved_for_adapter_execution":
            errors.append(f"case_{index_number}_status_invalid")
        if item.get("decision") != "handoff_ready_no_auto_submit":
            errors.append(f"case_{index_number}_decision_invalid")
        if item.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append(f"case_{index_number}_legal_gate_mode_invalid")
        for field in [
            "external_lawyer_involved",
            "official_system_touched",
            "official_submission_performed",
            "adapter_execution_performed",
            "automatic_submission_performed",
        ]:
            if item.get(field) is not False:
                errors.append(f"case_{index_number}_{field}_must_be_false")
        if item.get("errors") not in ([], None):
            errors.append(f"case_{index_number}_errors_must_be_empty")

        quality = item.get("quality_gate") if isinstance(item.get("quality_gate"), dict) else {}
        if quality.get("status") != "passed":
            errors.append(f"case_{index_number}_quality_gate_must_pass")
        if float(quality.get("weighted_score") or 0) < 85:
            errors.append(f"case_{index_number}_quality_score_too_low")
        if quality.get("official_preflight_allowed") is not True:
            errors.append(f"case_{index_number}_quality_official_preflight_allowed_missing")
        if isinstance(quality.get("review_hash"), str) and not SHA256_RE.fullmatch(str(quality.get("review_hash"))):
            errors.append(f"case_{index_number}_quality_review_hash_invalid")

        handoff_path = validate_artifact_ref(item.get("handoff_package"), benchmark_dir, f"case_{index_number}_handoff", errors)
        result_path = validate_artifact_ref(
            item.get("pre_submission_to_handoff_result"),
            benchmark_dir,
            f"case_{index_number}_pre_submission_to_handoff_result",
            errors,
        )
        if handoff_path and handoff_path.exists():
            if item.get("handoff_package_hash") != sha256_file(handoff_path):
                errors.append(f"case_{index_number}_handoff_package_hash_mismatch")
        if result_path and result_path.exists():
            result = load_json(result_path)
            if item.get("lifecycle_trace_hash") != result.get("lifecycle_trace_hash"):
                errors.append(f"case_{index_number}_lifecycle_trace_hash_mismatch")
            if item.get("source_pre_submission_hash") != result.get("source_pre_submission_hash"):
                errors.append(f"case_{index_number}_source_pre_submission_hash_mismatch")

        source_has_delta = bool(source_case.get("reference_delta_source"))
        if item.get("reference_delta_present") is True:
            reference_delta_seen = True
        if bool(item.get("reference_delta_present")) != source_has_delta:
            errors.append(f"case_{index_number}_reference_delta_presence_mismatch")
        if source_has_delta:
            if not isinstance(item.get("reference_patent_delta_hash"), str) or not SHA256_RE.fullmatch(str(item.get("reference_patent_delta_hash"))):
                errors.append(f"case_{index_number}_reference_delta_hash_invalid")
            if item.get("reference_delta_boundary_preserved") is not True:
                errors.append(f"case_{index_number}_reference_delta_boundary_not_preserved")
            if int(item.get("reference_delta_rows_count") or 0) <= 0:
                errors.append(f"case_{index_number}_reference_delta_rows_missing")
            if int(item.get("reference_delta_claim_elements_count") or 0) <= 0:
                errors.append(f"case_{index_number}_reference_delta_claim_elements_missing")

        batch_item = batch_by_case.get(case_id, {})
        if batch_item.get("outcome") != "passed":
            errors.append(f"case_{index_number}_batch_outcome_must_pass")
        next_action = str(item.get("next_action") or "").lower()
        if "adapter execution" not in next_action or "application-number" not in next_action:
            errors.append(f"case_{index_number}_next_action_boundary_missing")

    if summary.get("reference_delta_cases") != sum(1 for item in cases if isinstance(item, dict) and item.get("reference_delta_present") is True):
        errors.append("inbox_handoff_index_reference_delta_summary_mismatch")
    if not reference_delta_seen:
        errors.append("inbox_handoff_index_reference_delta_case_missing")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "inbox handoff index",
            "index status: pass",
            "ai self-filing",
            "official system touched: no",
            "official submission performed: no",
            "adapter execution performed: no",
            "automatic submission performed: no",
            "external lawyer involved: no",
            "local read-only handoff evidence",
            "does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number",
        ]:
            if needle not in text:
                errors.append(f"inbox_handoff_index_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
        manifest = load_json(hashes_path)
        paths = {item.get("path") for item in manifest.get("files", []) if isinstance(item, dict)}
        for required in ["inbox-handoff-index.json", "inbox-handoff-index.md"]:
            if required not in paths:
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
