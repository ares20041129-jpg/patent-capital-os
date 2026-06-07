#!/usr/bin/env python3
"""Validate filing adapter request/response contract for dry-run or handoff use."""

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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


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


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


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
) -> Path | None:
    if base_dir is None or is_blank(data.get(path_key)):
        return None
    path = resolve_reference(data.get(path_key), base_dir)
    if not path.exists():
        errors.append(f"{label}_file_not_found")
        return None
    if data.get(hash_key) and sha256_file(path) != data.get(hash_key):
        errors.append(f"{label}_hash_mismatch")
    return path


def validate_request(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in [
        "case_id",
        "execution_mode",
        "requested_action",
        "official_system",
        "account_role",
        "authorization_evidence",
        "signature_authority_evidence",
        "payment_authority_evidence",
        "package_manifest",
        "receipt_capture_destination",
    ]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("execution_mode") not in {"dry_run", "handoff", "approved_adapter"}:
        errors.append("execution_mode_invalid")

    if data.get("requested_action") not in {"submit_package", "handoff", "dry_run_validate"}:
        errors.append("requested_action_invalid")

    require_hash(data.get("final_package_hash"), "final_package_hash", errors)
    require_hash(data.get("reviewed_package_hash"), "reviewed_package_hash", errors)
    if data.get("final_package_hash") and data.get("reviewed_package_hash") and data["final_package_hash"] != data["reviewed_package_hash"]:
        errors.append("hash_mismatch: final_package_hash != reviewed_package_hash")

    forbidden = has_forbidden_key(data)
    if forbidden:
        errors.append(f"forbidden_request_field_present: {forbidden}")

    if data.get("forbidden_fields_absent_confirmed") is not True:
        errors.append("forbidden_fields_absent_confirmed_must_be_true")

    if data.get("execution_mode") == "approved_adapter":
        for key in [
            "approved_adapter_preflight",
            "approved_adapter_preflight_hash",
            "adapter_security_review_hash",
            "adapter_production_readiness_hash",
            "official_session_authorization_hash",
            "official_session_reference_hash",
        ]:
            if is_blank(data.get(key)):
                errors.append(f"approved_adapter_missing_required_field: {key}")
        require_hash(data.get("approved_adapter_preflight_hash"), "approved_adapter_preflight_hash", errors)
        require_hash(data.get("adapter_security_review_hash"), "adapter_security_review_hash", errors)
        require_hash(data.get("adapter_production_readiness_hash"), "adapter_production_readiness_hash", errors)
        require_hash(data.get("official_session_authorization_hash"), "official_session_authorization_hash", errors)
        require_hash(data.get("official_session_reference_hash"), "official_session_reference_hash", errors)
        preflight_path = validate_file_hash_reference(
            data,
            "approved_adapter_preflight",
            "approved_adapter_preflight_hash",
            "approved_adapter_preflight",
            base_dir,
            errors,
        )
        validate_file_hash_reference(
            data,
            "adapter_production_readiness_packet",
            "adapter_production_readiness_hash",
            "adapter_production_readiness_packet",
            base_dir,
            errors,
        )
        validate_file_hash_reference(
            data,
            "official_session_authorization_packet",
            "official_session_authorization_hash",
            "official_session_authorization_packet",
            base_dir,
            errors,
        )
        if data.get("requested_action") != "submit_package":
            errors.append("approved_adapter_requested_action_must_be_submit_package")
        if data.get("human_only_steps"):
            errors.append("approved_adapter_request_must_not_include_human_only_steps")
        if preflight_path is not None:
            try:
                preflight = load_json(preflight_path)
                package = preflight.get("package") if isinstance(preflight.get("package"), dict) else {}
                adapter = preflight.get("adapter") if isinstance(preflight.get("adapter"), dict) else {}
                readiness = adapter.get("production_readiness") if isinstance(adapter.get("production_readiness"), dict) else {}
                security = adapter.get("security_review") if isinstance(adapter.get("security_review"), dict) else {}
                channel = preflight.get("official_channel") if isinstance(preflight.get("official_channel"), dict) else {}
                session = channel.get("session_authorization") if isinstance(channel.get("session_authorization"), dict) else {}
                materials = preflight.get("application_materials") if isinstance(preflight.get("application_materials"), dict) else {}
                for key, expected in [
                    ("case_id", preflight.get("case_id")),
                    ("official_system", channel.get("official_system")),
                    ("final_package_hash", package.get("final_package_hash")),
                    ("reviewed_package_hash", package.get("reviewed_package_hash")),
                    ("adapter_security_review_hash", security.get("review_artifact_hash")),
                    ("adapter_production_readiness_hash", readiness.get("packet_hash")),
                    ("official_session_authorization_hash", session.get("packet_hash")),
                    ("official_session_reference_hash", session.get("session_reference_hash")),
                ]:
                    if expected and data.get(key) != expected:
                        errors.append(f"approved_adapter_request_{key}_preflight_mismatch")
                if data.get("application_materials_hash") and materials.get("hash") and data.get("application_materials_hash") != materials.get("hash"):
                    errors.append("approved_adapter_request_application_materials_hash_preflight_mismatch")
                if materials.get("reference_patent_delta_hash") or data.get("reference_patent_delta_hash"):
                    if materials.get("hash") and data.get("application_materials_hash") != materials.get("hash"):
                        errors.append("approved_adapter_request_application_materials_hash_preflight_mismatch")
                    if data.get("reference_patent_delta_hash") != materials.get("reference_patent_delta_hash"):
                        errors.append("approved_adapter_request_reference_patent_delta_hash_preflight_mismatch")
                    if data.get("reference_delta_boundary_preserved") is not True:
                        errors.append("approved_adapter_request_reference_delta_boundary_must_be_true")
            except Exception as exc:
                errors.append(f"approved_adapter_preflight_unreadable: {exc}")

    return len(errors) == 0, errors, warnings


def validate_response(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ["case_id", "execution_mode", "adapter_name", "adapter_version", "response_state", "next_status", "audit_log_entry"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("response_state") not in {"dry_run_ok", "handoff_required", "submitted_pending_receipt", "blocked"}:
        errors.append("response_state_invalid")

    require_hash(data.get("final_package_hash"), "final_package_hash", errors)
    require_hash(data.get("reviewed_package_hash"), "reviewed_package_hash", errors)
    if data.get("final_package_hash") and data.get("reviewed_package_hash") and data["final_package_hash"] != data["reviewed_package_hash"]:
        errors.append("hash_mismatch: final_package_hash != reviewed_package_hash")

    if data.get("execution_mode") == "dry_run":
        if data.get("official_system_touched") is not False:
            errors.append("dry_run_must_not_touch_official_system")
        if data.get("official_submission_performed") is not False:
            errors.append("dry_run_must_not_perform_official_submission")
        if data.get("response_state") not in {"dry_run_ok", "handoff_required", "blocked"}:
            errors.append("dry_run_response_state_invalid")
        if data.get("next_status") not in {"ready_for_authorized_filing", "submitted_pending_receipt"}:
            errors.append("dry_run_next_status_invalid")
        if data.get("next_status") == "submitted_pending_receipt":
            errors.append("dry_run_cannot_advance_to_submitted_pending_receipt")

    if data.get("response_state") == "handoff_required" and data.get("handoff_required") is not True:
        errors.append("handoff_required_response_must_set_handoff_required_true")

    if data.get("response_state") == "submitted_pending_receipt":
        if data.get("official_system_touched") is not True or data.get("official_submission_performed") is not True:
            errors.append("submitted_pending_receipt_requires_official_action_true")
        if data.get("next_status") != "submitted_pending_receipt":
            errors.append("submitted_pending_receipt_response_requires_next_status_submitted_pending_receipt")
        warnings.append("submitted_pending_receipt_requires_receipt_capture_followup")

    if data.get("execution_mode") == "approved_adapter":
        if data.get("response_state") == "submitted_pending_receipt":
            for key in [
                "approved_adapter_preflight_hash",
                "adapter_production_readiness_hash",
                "official_session_authorization_hash",
                "official_session_reference_hash",
                "adapter_execution_result",
                "adapter_execution_result_hash",
            ]:
                if is_blank(data.get(key)):
                    errors.append(f"approved_adapter_response_missing_required_field: {key}")
            require_hash(data.get("approved_adapter_preflight_hash"), "approved_adapter_preflight_hash", errors)
            require_hash(data.get("adapter_production_readiness_hash"), "adapter_production_readiness_hash", errors)
            require_hash(data.get("official_session_authorization_hash"), "official_session_authorization_hash", errors)
            require_hash(data.get("official_session_reference_hash"), "official_session_reference_hash", errors)
            require_hash(data.get("adapter_execution_result_hash"), "adapter_execution_result_hash", errors)
            result_path = validate_file_hash_reference(
                data,
                "adapter_execution_result",
                "adapter_execution_result_hash",
                "adapter_execution_result",
                base_dir,
                errors,
            )
            if result_path is not None:
                try:
                    result = load_json(result_path)
                    for key in [
                        "case_id",
                        "adapter_name",
                        "adapter_version",
                        "approved_adapter_preflight_hash",
                        "adapter_production_readiness_hash",
                        "official_session_authorization_hash",
                        "official_session_reference_hash",
                        "final_package_hash",
                        "reviewed_package_hash",
                    ]:
                        if result.get(key) and data.get(key) != result.get(key):
                            errors.append(f"adapter_response_{key}_result_mismatch")
                    if result.get("reference_patent_delta_hash") or data.get("reference_patent_delta_hash"):
                        for key in [
                            "application_materials_hash",
                            "reference_patent_delta_hash",
                            "reference_delta_rows_count",
                            "reference_delta_claim_elements_count",
                        ]:
                            if data.get(key) != result.get(key):
                                errors.append(f"adapter_response_{key}_result_mismatch")
                        if data.get("reference_delta_boundary_preserved") is not True:
                            errors.append("adapter_response_reference_delta_boundary_must_be_true")
                except Exception as exc:
                    errors.append(f"adapter_execution_result_unreadable: {exc}")
        elif data.get("response_state") == "handoff_required":
            errors.append("approved_adapter_response_must_not_handoff_after_execution")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["request", "response"])
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        data = load_json(args.path)
        ok, errors, warnings = validate_request(data, args.path.parent) if args.mode == "request" else validate_response(data, args.path.parent)
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
