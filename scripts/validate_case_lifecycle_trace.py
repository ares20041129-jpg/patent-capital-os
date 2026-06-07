#!/usr/bin/env python3
"""Validate a Patent Capital OS end-to-end lifecycle trace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


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

STATUS_RANK = {status: index for index, status in enumerate(ORDER)}

REQUIRED_TOP_LEVEL = [
    "lifecycle_id",
    "case_id",
    "jurisdiction",
    "trace_type",
    "generated_at",
    "final_status",
    "stages",
    "invariants",
]

REQUIRED_STAGE_FIELDS = [
    "order",
    "stage",
    "status",
    "artifact",
    "artifact_hash",
    "validator",
    "validation_result",
    "legal_gate",
    "official_system_touched",
    "official_submission_performed",
    "adapter_execution_performed",
    "benchmark_mock",
    "decision",
    "next_required_gate",
]

REQUIRED_INVARIANTS = [
    "legal_gate_never_skipped",
    "package_hash_consistent",
    "no_receipt_before_submission",
    "no_application_number_before_receipt",
    "official_session_hash_consistent",
    "mock_evidence_marked",
]

REFERENCE_DELTA_FIELDS = [
    "reference_patent_delta_hash",
    "reference_delta_rows_count",
    "reference_delta_claim_elements_count",
    "reference_delta_boundary_preserved",
]

OFFICIAL_SESSION_STAGES = {
    "approved_adapter_preflight",
    "adapter_execution_result",
    "receipt_capture",
    "application_number_evidence",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.isdigit():
        parsed = int(value)
        return parsed if parsed > 0 else None
    return None


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    trace_type = data.get("trace_type")
    if trace_type not in {"production", "benchmark_mock"}:
        errors.append("trace_type_invalid")

    final_status = data.get("final_status")
    if final_status not in STATUS_RANK:
        errors.append("final_status_invalid")

    invariants = data.get("invariants") if isinstance(data.get("invariants"), dict) else {}
    for key in REQUIRED_INVARIANTS:
        if invariants.get(key) is not True:
            errors.append(f"invariant_must_be_true: {key}")

    trace_application_materials_hash = data.get("application_materials_hash")
    if not is_blank(trace_application_materials_hash):
        require_hash(trace_application_materials_hash, "application_materials_hash", errors)

    trace_reference_delta_hash = data.get("reference_patent_delta_hash")
    if not is_blank(trace_reference_delta_hash):
        require_hash(trace_reference_delta_hash, "reference_patent_delta_hash", errors)
        if positive_int(data.get("reference_delta_rows_count")) is None:
            errors.append("reference_delta_rows_count_must_be_positive_integer")
        if positive_int(data.get("reference_delta_claim_elements_count")) is None:
            errors.append("reference_delta_claim_elements_count_must_be_positive_integer")
        if data.get("reference_delta_boundary_preserved") is not True:
            errors.append("reference_delta_boundary_preserved_must_be_true")
        if invariants.get("reference_delta_boundary_preserved") is not True:
            errors.append("invariant_must_be_true: reference_delta_boundary_preserved")

    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        errors.append("stages_must_be_nonempty_list")
        return False, errors, warnings
    session_required = any(
        isinstance(stage, dict) and stage.get("stage") in {"approved_adapter_preflight", "adapter_execution_result"}
        for stage in stages
    )

    previous_rank = -1
    seen_orders: set[int] = set()
    seen_stages: set[str] = set()
    saw_legal_pass = False
    saw_submission = False
    saw_receipt = False
    saw_application_number = False
    final_package_hash = ""
    reviewed_package_hash = ""
    submitted_package_hash = ""
    official_session_authorization_hash = ""
    official_session_reference_hash = ""
    application_materials_hash = str(trace_application_materials_hash or "")
    reference_patent_delta_hash = str(trace_reference_delta_hash or "")
    reference_delta_rows_count: int | None = positive_int(data.get("reference_delta_rows_count"))
    reference_delta_claim_elements_count: int | None = positive_int(data.get("reference_delta_claim_elements_count"))

    for index, stage in enumerate(stages, start=1):
        if not isinstance(stage, dict):
            errors.append(f"stage_{index}_must_be_object")
            continue

        for key in REQUIRED_STAGE_FIELDS:
            if is_blank(stage.get(key)):
                errors.append(f"stage_{index}_missing_required_field: {key}")

        order = stage.get("order")
        if not isinstance(order, int):
            errors.append(f"stage_{index}_order_must_be_integer")
        else:
            if order in seen_orders:
                errors.append(f"duplicate_stage_order: {order}")
            seen_orders.add(order)
            if order != index:
                errors.append(f"stage_{index}_order_must_equal_position")

        stage_name = str(stage.get("stage") or "")
        if stage_name in seen_stages:
            errors.append(f"duplicate_stage_name: {stage_name}")
        seen_stages.add(stage_name)

        status = stage.get("status")
        if status not in STATUS_RANK:
            errors.append(f"stage_{index}_status_invalid")
            continue

        stage_session_authorization_hash = stage.get("official_session_authorization_hash")
        stage_session_reference_hash = stage.get("official_session_reference_hash")
        if session_required and stage_name in OFFICIAL_SESSION_STAGES:
            require_hash(stage_session_authorization_hash, f"stage_{index}.official_session_authorization_hash", errors)
            require_hash(stage_session_reference_hash, f"stage_{index}.official_session_reference_hash", errors)
        if not is_blank(stage_session_authorization_hash):
            require_hash(stage_session_authorization_hash, f"stage_{index}.official_session_authorization_hash", errors)
            official_session_authorization_hash = official_session_authorization_hash or str(stage_session_authorization_hash)
            if stage_session_authorization_hash != official_session_authorization_hash:
                errors.append(f"stage_{index}_official_session_authorization_hash_changed")
        if not is_blank(stage_session_reference_hash):
            require_hash(stage_session_reference_hash, f"stage_{index}.official_session_reference_hash", errors)
            official_session_reference_hash = official_session_reference_hash or str(stage_session_reference_hash)
            if stage_session_reference_hash != official_session_reference_hash:
                errors.append(f"stage_{index}_official_session_reference_hash_changed")

        rank = STATUS_RANK[status]
        if rank < previous_rank:
            errors.append(f"stage_{index}_status_regressed")
        previous_rank = rank

        require_hash(stage.get("artifact_hash"), f"stage_{index}.artifact_hash", errors)
        if base_dir is not None and not is_blank(stage.get("artifact")) and not is_blank(stage.get("artifact_hash")):
            artifact_path = (base_dir / str(stage.get("artifact"))).resolve()
            if not artifact_path.exists():
                errors.append(f"stage_{index}_artifact_missing: {stage.get('artifact')}")
            elif sha256_file(artifact_path) != stage.get("artifact_hash"):
                errors.append(f"stage_{index}_artifact_hash_mismatch: {stage.get('artifact')}")

        if stage.get("validation_result") != "passed":
            errors.append(f"stage_{index}_validation_result_must_be_passed")

        if stage.get("legal_gate") not in {"pending", "failed", "passed"}:
            errors.append(f"stage_{index}_legal_gate_invalid")

        if stage.get("legal_gate") == "passed":
            saw_legal_pass = True

        if rank >= STATUS_RANK["ready_for_package_validation"] and not saw_legal_pass:
            errors.append(f"stage_{index}_ready_or_later_requires_prior_legal_gate_passed")

        official_touched = stage.get("official_system_touched") is True
        official_submitted = stage.get("official_submission_performed") is True
        adapter_performed = stage.get("adapter_execution_performed") is True

        if status in {
            "intake_received",
            "draft_only",
            "legal_gate_failed",
            "ready_for_package_validation",
            "package_valid_official_preflight_pending",
            "ready_for_authorized_filing",
            "approved_for_adapter_execution",
        }:
            if official_touched:
                errors.append(f"stage_{index}_must_not_touch_official_system")
            if official_submitted:
                errors.append(f"stage_{index}_must_not_perform_official_submission")

        if status == "approved_for_adapter_execution" and adapter_performed:
            errors.append(f"stage_{index}_approved_preflight_must_not_perform_adapter_execution")

        if official_submitted:
            saw_submission = True

        receipt_hash = stage.get("receipt_hash")
        if receipt_hash:
            require_hash(receipt_hash, f"stage_{index}.receipt_hash", errors)
            saw_receipt = True
            if not saw_submission:
                errors.append(f"stage_{index}_receipt_before_submission")

        application_number = stage.get("application_number")
        if application_number:
            saw_application_number = True
            if not saw_receipt:
                errors.append(f"stage_{index}_application_number_before_receipt")

        if trace_type == "benchmark_mock" and stage.get("benchmark_mock") is not True:
            errors.append(f"stage_{index}_benchmark_trace_stage_must_be_marked_mock")

        if trace_type == "production" and stage.get("benchmark_mock") is True:
            errors.append(f"stage_{index}_production_trace_must_not_use_mock_stage")

        if stage.get("final_package_hash"):
            require_hash(stage.get("final_package_hash"), f"stage_{index}.final_package_hash", errors)
            final_package_hash = final_package_hash or str(stage.get("final_package_hash"))
            if stage.get("final_package_hash") != final_package_hash:
                errors.append(f"stage_{index}_final_package_hash_changed")

        if stage.get("reviewed_package_hash"):
            require_hash(stage.get("reviewed_package_hash"), f"stage_{index}.reviewed_package_hash", errors)
            reviewed_package_hash = reviewed_package_hash or str(stage.get("reviewed_package_hash"))
            if stage.get("reviewed_package_hash") != reviewed_package_hash:
                errors.append(f"stage_{index}_reviewed_package_hash_changed")

        if stage.get("submitted_package_hash"):
            require_hash(stage.get("submitted_package_hash"), f"stage_{index}.submitted_package_hash", errors)
            submitted_package_hash = submitted_package_hash or str(stage.get("submitted_package_hash"))
            if stage.get("submitted_package_hash") != submitted_package_hash:
                errors.append(f"stage_{index}_submitted_package_hash_changed")

        stage_application_materials_hash = stage.get("application_materials_hash")
        if not is_blank(stage_application_materials_hash):
            require_hash(stage_application_materials_hash, f"stage_{index}.application_materials_hash", errors)
            application_materials_hash = application_materials_hash or str(stage_application_materials_hash)
            if stage_application_materials_hash != application_materials_hash:
                errors.append(f"stage_{index}_application_materials_hash_changed")
        if application_materials_hash and rank >= STATUS_RANK["ready_for_authorized_filing"]:
            if is_blank(stage_application_materials_hash):
                errors.append(f"stage_{index}_application_materials_hash_required_after_official_preflight")

        has_reference_delta_field = any(not is_blank(stage.get(field)) for field in REFERENCE_DELTA_FIELDS)
        stage_reference_delta_hash = stage.get("reference_patent_delta_hash")
        if has_reference_delta_field and is_blank(stage_reference_delta_hash):
            errors.append(f"stage_{index}_reference_delta_fields_require_reference_patent_delta_hash")
        if not is_blank(stage_reference_delta_hash):
            require_hash(stage_reference_delta_hash, f"stage_{index}.reference_patent_delta_hash", errors)
            reference_patent_delta_hash = reference_patent_delta_hash or str(stage_reference_delta_hash)
            if stage_reference_delta_hash != reference_patent_delta_hash:
                errors.append(f"stage_{index}_reference_patent_delta_hash_changed")

            stage_rows_count = positive_int(stage.get("reference_delta_rows_count"))
            stage_claim_elements_count = positive_int(stage.get("reference_delta_claim_elements_count"))
            if stage_rows_count is None:
                errors.append(f"stage_{index}_reference_delta_rows_count_must_be_positive_integer")
            elif reference_delta_rows_count is None:
                reference_delta_rows_count = stage_rows_count
            elif stage_rows_count != reference_delta_rows_count:
                errors.append(f"stage_{index}_reference_delta_rows_count_changed")
            if stage_claim_elements_count is None:
                errors.append(f"stage_{index}_reference_delta_claim_elements_count_must_be_positive_integer")
            elif reference_delta_claim_elements_count is None:
                reference_delta_claim_elements_count = stage_claim_elements_count
            elif stage_claim_elements_count != reference_delta_claim_elements_count:
                errors.append(f"stage_{index}_reference_delta_claim_elements_count_changed")
            if stage.get("reference_delta_boundary_preserved") is not True:
                errors.append(f"stage_{index}_reference_delta_boundary_preserved_must_be_true")
        if reference_patent_delta_hash and rank >= STATUS_RANK["ready_for_package_validation"]:
            if is_blank(stage_reference_delta_hash):
                errors.append(f"stage_{index}_reference_patent_delta_hash_required_after_legal_gate")

    if stages[-1].get("status") != final_status:
        errors.append("final_status_must_match_last_stage_status")

    if final_package_hash and reviewed_package_hash and final_package_hash != reviewed_package_hash:
        errors.append("lifecycle_hash_mismatch: final_package_hash != reviewed_package_hash")
    if final_package_hash and submitted_package_hash and final_package_hash != submitted_package_hash:
        errors.append("lifecycle_hash_mismatch: submitted_package_hash != final_package_hash")

    if session_required and (not official_session_authorization_hash or not official_session_reference_hash):
        errors.append("lifecycle_missing_official_session_hashes")

    if final_status == "accepted_or_application_number_received" and not saw_application_number:
        errors.append("accepted_final_status_requires_application_number")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.trace), base_dir=args.trace.parent)
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
