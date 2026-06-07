#!/usr/bin/env python3
"""Validate approved-adapter execution result evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_REQUEST_KEYS = {
    "password",
    "private_key",
    "captcha_bypass",
    "mfa_secret",
    "session_token",
    "cookie",
    "raw_credentials",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED_PATHS = [
    "case_id",
    "execution_mode",
    "adapter_name",
    "adapter_version",
    "adapter_request",
    "adapter_request_hash",
    "approved_adapter_preflight",
    "approved_adapter_preflight_hash",
    "adapter_production_readiness_hash",
    "official_session_authorization_hash",
    "official_session_reference_hash",
    "official_system",
    "official_action",
    "action_started_at",
    "action_completed_at",
    "response_state",
    "next_status",
    "final_package_hash",
    "reviewed_package_hash",
    "receipt_capture_status",
    "receipt_capture_plan",
    "receipt_capture_plan_hash",
    "audit_log_entry",
    "audit_log_entry_hash",
    "docket_entry",
    "docket_entry_hash",
    "official_submission_evidence.submission_reference",
    "official_submission_evidence.official_status_snapshot_file",
    "official_submission_evidence.official_status_snapshot_hash",
    "official_submission_evidence.submitted_package_hash",
    "official_submission_evidence.submitted_file_list_file",
    "official_submission_evidence.submitted_file_list_hash",
    "fees.payment_status",
    "decision.status",
    "decision.reason",
]

HASH_PATHS = [
    "adapter_request_hash",
    "approved_adapter_preflight_hash",
    "adapter_production_readiness_hash",
    "official_session_authorization_hash",
    "official_session_reference_hash",
    "final_package_hash",
    "reviewed_package_hash",
    "receipt_capture_plan_hash",
    "audit_log_entry_hash",
    "docket_entry_hash",
    "official_submission_evidence.official_status_snapshot_hash",
    "official_submission_evidence.submitted_package_hash",
    "official_submission_evidence.submitted_file_list_hash",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def require_hash(data: dict[str, Any], dotted: str, errors: list[str]) -> None:
    value = get_path(data, dotted)
    if is_blank(value):
        errors.append(f"missing_required_field: {dotted}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{dotted}_must_be_sha256_64_hex")


def require_positive_int(value: Any, label: str, errors: list[str]) -> None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        errors.append(f"{label}_must_be_positive_integer")
        return
    if parsed <= 0:
        errors.append(f"{label}_must_be_positive_integer")


def resolve_reference(reference: Any, base_dir: Path) -> Path:
    path = Path(str(reference or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def validate_file_hash_reference(
    data: dict[str, Any],
    path_key: str,
    hash_key: str,
    label: str,
    base_dir: Path | None,
    errors: list[str],
) -> None:
    if base_dir is None or is_blank(get_path(data, path_key)):
        return
    path = resolve_reference(get_path(data, path_key), base_dir)
    if not path.exists():
        errors.append(f"{label}_file_not_found")
        return
    if get_path(data, hash_key) and sha256_file(path) != get_path(data, hash_key):
        errors.append(f"{label}_hash_mismatch")


def has_forbidden_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_REQUEST_KEYS:
                return key
            found = has_forbidden_key(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = has_forbidden_key(child)
            if found:
                return found
    return None


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")

    for path in HASH_PATHS:
        require_hash(data, path, errors)

    for path_key, hash_key, label in [
        ("adapter_request", "adapter_request_hash", "adapter_request"),
        ("approved_adapter_preflight", "approved_adapter_preflight_hash", "approved_adapter_preflight"),
        ("receipt_capture_plan", "receipt_capture_plan_hash", "receipt_capture_plan"),
        ("audit_log_entry", "audit_log_entry_hash", "audit_log_entry"),
        ("docket_entry", "docket_entry_hash", "docket_entry"),
        (
            "official_submission_evidence.official_status_snapshot_file",
            "official_submission_evidence.official_status_snapshot_hash",
            "official_status_snapshot",
        ),
        (
            "official_submission_evidence.submitted_file_list_file",
            "official_submission_evidence.submitted_file_list_hash",
            "submitted_file_list",
        ),
    ]:
        validate_file_hash_reference(data, path_key, hash_key, label, base_dir, errors)

    approved_preflight: dict[str, Any] = {}
    preflight_materials: dict[str, Any] = {}
    if base_dir is not None and not is_blank(get_path(data, "approved_adapter_preflight")):
        try:
            preflight_path = resolve_reference(get_path(data, "approved_adapter_preflight"), base_dir)
            approved_preflight = load_json(preflight_path)
            loaded_materials = approved_preflight.get("application_materials")
            if isinstance(loaded_materials, dict):
                preflight_materials = loaded_materials
        except Exception:
            preflight_materials = {}
    preflight_reference_hash = preflight_materials.get("reference_patent_delta_hash")
    result_reference_hash = data.get("reference_patent_delta_hash")
    if preflight_reference_hash or result_reference_hash:
        if preflight_materials:
            if data.get("application_materials_hash") != preflight_materials.get("hash"):
                errors.append("application_materials_hash_mismatch_with_approved_preflight")
            if result_reference_hash != preflight_reference_hash:
                errors.append("reference_patent_delta_hash_mismatch_with_approved_preflight")
        if is_blank(result_reference_hash):
            errors.append("missing_required_field: reference_patent_delta_hash")
        elif not SHA256_RE.fullmatch(str(result_reference_hash)):
            errors.append("reference_patent_delta_hash_must_be_sha256_64_hex")
        require_positive_int(data.get("reference_delta_rows_count"), "reference_delta_rows_count", errors)
        require_positive_int(data.get("reference_delta_claim_elements_count"), "reference_delta_claim_elements_count", errors)
        if data.get("reference_delta_boundary_preserved") is not True:
            errors.append("reference_delta_boundary_must_be_true")

    forbidden = has_forbidden_key(data)
    if forbidden:
        errors.append(f"forbidden_field_present: {forbidden}")

    if get_path(data, "execution_mode") != "approved_adapter":
        errors.append("execution_mode_must_be_approved_adapter")

    if get_path(data, "official_action") != "submit_package":
        errors.append("official_action_must_be_submit_package")

    if get_path(data, "response_state") != "submitted_pending_receipt":
        errors.append("response_state_must_be_submitted_pending_receipt")

    if get_path(data, "next_status") != "submitted_pending_receipt":
        errors.append("next_status_must_be_submitted_pending_receipt")

    if get_path(data, "official_system_touched") is not True:
        errors.append("official_system_touched_must_be_true")

    if get_path(data, "official_submission_performed") is not True:
        errors.append("official_submission_performed_must_be_true")

    if get_path(data, "adapter_execution_performed") is not True:
        errors.append("adapter_execution_performed_must_be_true")

    final_hash = get_path(data, "final_package_hash")
    reviewed_hash = get_path(data, "reviewed_package_hash")
    submitted_hash = get_path(data, "official_submission_evidence.submitted_package_hash")
    if final_hash and reviewed_hash and final_hash != reviewed_hash:
        errors.append("hash_mismatch: final_package_hash != reviewed_package_hash")
    if final_hash and submitted_hash and final_hash != submitted_hash:
        errors.append("hash_mismatch: submitted_package_hash != final_package_hash")

    if get_path(data, "receipt_capture_status") != "submitted_pending_receipt":
        errors.append("receipt_capture_status_must_be_submitted_pending_receipt")

    if get_path(data, "official_receipt_hash"):
        errors.append("submitted_pending_receipt_must_not_have_official_receipt_hash")

    if get_path(data, "application_number"):
        errors.append("submitted_pending_receipt_must_not_have_application_number")

    payment_status = str(get_path(data, "fees.payment_status") or "").lower()
    if payment_status not in {"paid", "pending", "not_due", "deferred"}:
        errors.append("fees.payment_status_invalid")
    if payment_status == "paid":
        require_hash(data, "fees.payment_receipt_hash", errors)

    if get_path(data, "decision.status") != "submitted_pending_receipt":
        errors.append("decision_status_must_be_submitted_pending_receipt")

    if data.get("benchmark_mock") is True:
        warnings.append("benchmark_mock_not_real_official_submission")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.result), base_dir=args.result.parent)
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
