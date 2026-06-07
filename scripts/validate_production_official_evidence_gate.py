#!/usr/bin/env python3
"""Validate production official evidence before treating a case as truly filed."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_adapter_execution_result
import validate_application_number_evidence
import validate_receipt_capture


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

FORBIDDEN_KEYS = {
    "password",
    "private_key",
    "captcha_bypass",
    "mfa_secret",
    "session_token",
    "cookie",
    "raw_credentials",
}

REQUIRED_PACKET_PATHS = [
    "case_id",
    "evidence_gate",
    "evidence_mode",
    "legal_gate_mode",
    "official_system",
    "source.capture_method",
    "source.captured_at",
    "source.captured_by",
    "source.official_account_role",
    "source.authorization_packet_hash",
    "source.official_session_reference_hash",
    "package.final_package_hash",
    "package.reviewed_package_hash",
    "package.submitted_package_hash",
    "artifacts.adapter_execution_result.path",
    "artifacts.adapter_execution_result.sha256",
    "artifacts.adapter_execution_result.adapter_production_readiness_hash",
    "artifacts.adapter_execution_result.official_session_authorization_hash",
    "artifacts.adapter_execution_result.official_session_reference_hash",
    "artifacts.receipt_capture.path",
    "artifacts.receipt_capture.sha256",
    "artifacts.receipt_capture.official_session_authorization_hash",
    "artifacts.receipt_capture.official_session_reference_hash",
    "artifacts.application_number_evidence.path",
    "artifacts.application_number_evidence.sha256",
    "artifacts.application_number_evidence.official_session_authorization_hash",
    "artifacts.application_number_evidence.official_session_reference_hash",
    "decision.status",
    "decision.reason",
]

HASH_PATHS = [
    "source.authorization_packet_hash",
    "source.official_session_reference_hash",
    "package.final_package_hash",
    "package.reviewed_package_hash",
    "package.submitted_package_hash",
    "artifacts.adapter_execution_result.sha256",
    "artifacts.adapter_execution_result.adapter_production_readiness_hash",
    "artifacts.adapter_execution_result.official_session_authorization_hash",
    "artifacts.adapter_execution_result.official_session_reference_hash",
    "artifacts.receipt_capture.sha256",
    "artifacts.receipt_capture.official_session_authorization_hash",
    "artifacts.receipt_capture.official_session_reference_hash",
    "artifacts.application_number_evidence.sha256",
    "artifacts.application_number_evidence.official_session_authorization_hash",
    "artifacts.application_number_evidence.official_session_reference_hash",
]

REFERENCE_DELTA_KEYS = [
    "application_materials_hash",
    "reference_patent_delta_hash",
    "reference_delta_rows_count",
    "reference_delta_claim_elements_count",
    "reference_delta_boundary_preserved",
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


def extract_reference_delta_metadata(data: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    if not isinstance(data, dict):
        return metadata
    nested = data.get("reference_delta")
    if isinstance(nested, dict):
        for key in REFERENCE_DELTA_KEYS:
            value = nested.get(key)
            if value not in (None, "", [], {}):
                metadata[key] = value
    for key in REFERENCE_DELTA_KEYS:
        value = data.get(key)
        if value not in (None, "", [], {}):
            metadata[key] = value
    return metadata


def validate_reference_delta_metadata(label: str, metadata: dict[str, Any], errors: list[str]) -> None:
    require_hash(metadata.get("reference_patent_delta_hash"), f"{label}.reference_patent_delta_hash", errors)
    if metadata.get("application_materials_hash"):
        require_hash(metadata.get("application_materials_hash"), f"{label}.application_materials_hash", errors)
    if positive_int(metadata.get("reference_delta_rows_count")) is None:
        errors.append(f"{label}_reference_delta_rows_count_must_be_positive_integer")
    if positive_int(metadata.get("reference_delta_claim_elements_count")) is None:
        errors.append(f"{label}_reference_delta_claim_elements_count_must_be_positive_integer")
    if metadata.get("reference_delta_boundary_preserved") is not True:
        errors.append(f"{label}_reference_delta_boundary_preserved_must_be_true")


def has_forbidden_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_KEYS:
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


def mock_or_test_marker(value: Any, allow_production_shape_test: bool) -> str | None:
    if isinstance(value, dict):
        if value.get("benchmark_mock") is True:
            return "benchmark_mock"
        if value.get("not_real_official_evidence") is True and not allow_production_shape_test:
            return "not_real_official_evidence"
        if value.get("production_shape_test") is True and not allow_production_shape_test:
            return "production_shape_test"
        for key, child in value.items():
            if key in {"benchmark_mock"} and child is True:
                return key
            found = mock_or_test_marker(child, allow_production_shape_test)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = mock_or_test_marker(child, allow_production_shape_test)
            if found:
                return found
    elif isinstance(value, str) and not allow_production_shape_test:
        lowered = value.lower()
        for marker in ["mock", "benchmark", "placeholder", "shape-test"]:
            if marker in lowered:
                return marker
    return None


def resolve_artifact(packet_path: Path, packet: dict[str, Any], key: str, errors: list[str]) -> Path | None:
    raw = get_path(packet, f"artifacts.{key}.path")
    expected_hash = get_path(packet, f"artifacts.{key}.sha256")
    if is_blank(raw):
        return None
    path = Path(str(raw))
    if not path.is_absolute():
        path = (packet_path.parent / path).resolve()
    if not path.exists():
        errors.append(f"{key}_artifact_missing: {path}")
        return None
    actual_hash = sha256_file(path)
    if expected_hash != actual_hash:
        errors.append(f"{key}_artifact_hash_mismatch")
    return path


def validate_packet(
    packet_path: Path,
    allow_production_shape_test: bool = False,
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    packet = load_json(packet_path)
    for path in REQUIRED_PACKET_PATHS:
        if is_blank(get_path(packet, path)):
            errors.append(f"missing_required_field: {path}")
    for path in HASH_PATHS:
        require_hash(get_path(packet, path), path, errors)

    forbidden = has_forbidden_key(packet)
    if forbidden:
        errors.append(f"forbidden_field_present: {forbidden}")

    if packet.get("evidence_gate") != "production_official_evidence_gate":
        errors.append("evidence_gate_must_be_production_official_evidence_gate")

    evidence_mode = packet.get("evidence_mode")
    if evidence_mode == "production_shape_test":
        if allow_production_shape_test:
            if packet.get("not_real_official_evidence") is not True:
                errors.append("production_shape_test_requires_not_real_official_evidence_true")
            warnings.append("production_shape_test_not_real_official_evidence")
        else:
            errors.append("production_shape_test_not_allowed_in_strict_production_gate")
    elif evidence_mode != "production_official_evidence":
        errors.append("evidence_mode_must_be_production_official_evidence")

    marker = mock_or_test_marker(packet, allow_production_shape_test)
    if marker:
        errors.append(f"packet_contains_mock_or_test_marker: {marker}")

    legal_gate_mode = packet.get("legal_gate_mode")
    if legal_gate_mode == "ai_self_filing_no_external_lawyer":
        if packet.get("external_lawyer_involved") is not False:
            errors.append("ai_self_filing_production_gate_requires_external_lawyer_false")
    elif legal_gate_mode != "counsel_or_agent_review":
        errors.append("legal_gate_mode_invalid")

    source = packet.get("source") if isinstance(packet.get("source"), dict) else {}
    if source.get("credential_material_included") is not False:
        errors.append("credential_material_included_must_be_false")
    if source.get("human_only_step_bypassed") is not False:
        errors.append("human_only_step_bypassed_must_be_false")
    if source.get("capture_method") not in {"official_channel_export", "official_channel_screen_capture", "approved_adapter_capture"}:
        errors.append("source_capture_method_invalid")

    package = packet.get("package") if isinstance(packet.get("package"), dict) else {}
    final_hash = package.get("final_package_hash")
    reviewed_hash = package.get("reviewed_package_hash")
    submitted_hash = package.get("submitted_package_hash")
    if final_hash and reviewed_hash and final_hash != reviewed_hash:
        errors.append("hash_mismatch: package.final_package_hash != package.reviewed_package_hash")
    if final_hash and submitted_hash and final_hash != submitted_hash:
        errors.append("hash_mismatch: package.submitted_package_hash != package.final_package_hash")

    adapter_path = resolve_artifact(packet_path, packet, "adapter_execution_result", errors)
    receipt_path = resolve_artifact(packet_path, packet, "receipt_capture", errors)
    application_path = resolve_artifact(packet_path, packet, "application_number_evidence", errors)

    adapter: dict[str, Any] = {}
    receipt: dict[str, Any] = {}
    application: dict[str, Any] = {}

    if adapter_path:
        adapter = load_json(adapter_path)
        adapter_base_dir = adapter_path.parent
        if allow_production_shape_test and (
            packet.get("evidence_mode") == "production_shape_test"
            or adapter.get("production_shape_test") is True
            or adapter.get("not_real_official_evidence") is True
        ):
            adapter_base_dir = None
        ok, errs, warns = validate_adapter_execution_result.validate(adapter, base_dir=adapter_base_dir)
        if not ok:
            errors.extend([f"adapter_execution_result: {item}" for item in errs])
        warnings.extend([f"adapter_execution_result: {item}" for item in warns])
        marker = mock_or_test_marker(adapter, allow_production_shape_test)
        if marker:
            errors.append(f"adapter_execution_result_contains_mock_or_test_marker: {marker}")
        if adapter.get("generator_official_system_touched") is not False:
            errors.append("adapter_execution_generator_must_not_touch_official_system")
        if adapter.get("generator_official_submission_performed") is not False:
            errors.append("adapter_execution_generator_must_not_perform_official_submission")
        if adapter.get("evidence_claims_official_submission_performed") is not True:
            errors.append("adapter_execution_must_mark_submission_as_evidence_claim")
        if get_path(adapter, "adapter_production_readiness_hash") != get_path(packet, "artifacts.adapter_execution_result.adapter_production_readiness_hash"):
            errors.append("adapter_execution_production_readiness_hash_mismatch")
        if get_path(adapter, "official_session_authorization_hash") != get_path(packet, "artifacts.adapter_execution_result.official_session_authorization_hash"):
            errors.append("adapter_execution_session_authorization_hash_mismatch")
        if get_path(adapter, "official_session_reference_hash") != get_path(packet, "artifacts.adapter_execution_result.official_session_reference_hash"):
            errors.append("adapter_execution_session_reference_hash_mismatch")
        if get_path(adapter, "official_session_reference_hash") != get_path(packet, "source.official_session_reference_hash"):
            errors.append("adapter_execution_source_session_reference_hash_mismatch")

    if receipt_path:
        receipt = validate_receipt_capture.load_packet(receipt_path)
        receipt_base_dir = receipt_path.parent
        if allow_production_shape_test and (
            packet.get("evidence_mode") == "production_shape_test"
            or receipt.get("production_shape_test") is True
            or receipt.get("not_real_official_evidence") is True
        ):
            receipt_base_dir = None
        ok, errs, warns = validate_receipt_capture.validate(receipt, base_dir=receipt_base_dir)
        if not ok:
            errors.extend([f"receipt_capture: {item}" for item in errs])
        warnings.extend([f"receipt_capture: {item}" for item in warns])
        marker = mock_or_test_marker(receipt, allow_production_shape_test)
        if marker:
            errors.append(f"receipt_capture_contains_mock_or_test_marker: {marker}")
        if receipt.get("status") != "official_receipt_received":
            errors.append("receipt_capture_status_must_be_official_receipt_received")
        if receipt.get("official_session_authorization_hash") != get_path(packet, "artifacts.receipt_capture.official_session_authorization_hash"):
            errors.append("receipt_capture_session_authorization_hash_mismatch")
        if receipt.get("official_session_reference_hash") != get_path(packet, "artifacts.receipt_capture.official_session_reference_hash"):
            errors.append("receipt_capture_session_reference_hash_mismatch")
        if receipt.get("official_session_reference_hash") != get_path(packet, "source.official_session_reference_hash"):
            errors.append("receipt_capture_source_session_reference_hash_mismatch")

    if application_path:
        application = load_json(application_path)
        application_base_dir = application_path.parent
        if allow_production_shape_test and (
            packet.get("evidence_mode") == "production_shape_test"
            or application.get("production_shape_test") is True
            or application.get("not_real_official_evidence") is True
        ):
            application_base_dir = None
        ok, errs, warns = validate_application_number_evidence.validate(application, base_dir=application_base_dir)
        if not ok:
            errors.extend([f"application_number_evidence: {item}" for item in errs])
        warnings.extend([f"application_number_evidence: {item}" for item in warns])
        marker = mock_or_test_marker(application, allow_production_shape_test)
        if marker:
            errors.append(f"application_number_evidence_contains_mock_or_test_marker: {marker}")
        if application.get("official_session_authorization_hash") != get_path(packet, "artifacts.application_number_evidence.official_session_authorization_hash"):
            errors.append("application_number_session_authorization_hash_mismatch")
        if application.get("official_session_reference_hash") != get_path(packet, "artifacts.application_number_evidence.official_session_reference_hash"):
            errors.append("application_number_session_reference_hash_mismatch")
        if application.get("official_session_reference_hash") != get_path(packet, "source.official_session_reference_hash"):
            errors.append("application_number_source_session_reference_hash_mismatch")

    if adapter and receipt and application:
        case_ids = {packet.get("case_id"), adapter.get("case_id"), receipt.get("case_id"), application.get("case_id")}
        if len(case_ids) != 1:
            errors.append("case_id_mismatch_across_production_evidence")
        if packet.get("official_system") != adapter.get("official_system") or packet.get("official_system") != receipt.get("official_system") or packet.get("official_system") != application.get("official_system"):
            errors.append("official_system_mismatch_across_production_evidence")
        if get_path(adapter, "official_submission_evidence.submitted_package_hash") != final_hash:
            errors.append("adapter_submitted_package_hash_mismatch")
        if get_path(receipt, "official_receipt.receipt_hash") != get_path(application, "official_receipt.receipt_hash"):
            errors.append("receipt_hash_mismatch_between_receipt_and_application_evidence")
        if get_path(application, "package.final_package_hash") != final_hash:
            errors.append("application_package_final_hash_mismatch")
        if get_path(application, "package.reviewed_package_hash") != reviewed_hash:
            errors.append("application_package_reviewed_hash_mismatch")
        if get_path(application, "package.submitted_package_hash") != submitted_hash:
            errors.append("application_package_submitted_hash_mismatch")
        adapter_session_authorization_hash = get_path(adapter, "official_session_authorization_hash")
        adapter_session_reference_hash = get_path(adapter, "official_session_reference_hash")
        if receipt.get("official_session_authorization_hash") != adapter_session_authorization_hash:
            errors.append("receipt_adapter_session_authorization_hash_mismatch")
        if application.get("official_session_authorization_hash") != adapter_session_authorization_hash:
            errors.append("application_adapter_session_authorization_hash_mismatch")
        if receipt.get("official_session_reference_hash") != adapter_session_reference_hash:
            errors.append("receipt_adapter_session_reference_hash_mismatch")
        if application.get("official_session_reference_hash") != adapter_session_reference_hash:
            errors.append("application_adapter_session_reference_hash_mismatch")

        reference_delta_sources = [
            ("packet", extract_reference_delta_metadata(packet)),
            ("adapter_execution_result", extract_reference_delta_metadata(adapter)),
            ("receipt_capture", extract_reference_delta_metadata(receipt)),
            ("application_number_evidence", extract_reference_delta_metadata(application)),
        ]
        if any(source.get("reference_patent_delta_hash") for _, source in reference_delta_sources):
            expected_reference_delta_hash = ""
            expected_application_materials_hash = ""
            expected_rows_count: int | None = None
            expected_claim_elements_count: int | None = None
            for label, metadata in reference_delta_sources:
                validate_reference_delta_metadata(label, metadata, errors)
                reference_delta_hash = metadata.get("reference_patent_delta_hash")
                if reference_delta_hash:
                    expected_reference_delta_hash = expected_reference_delta_hash or str(reference_delta_hash)
                    if reference_delta_hash != expected_reference_delta_hash:
                        errors.append(f"{label}_reference_patent_delta_hash_mismatch")
                application_materials_hash = metadata.get("application_materials_hash")
                if application_materials_hash:
                    expected_application_materials_hash = expected_application_materials_hash or str(application_materials_hash)
                    if application_materials_hash != expected_application_materials_hash:
                        errors.append(f"{label}_application_materials_hash_mismatch")
                rows_count = positive_int(metadata.get("reference_delta_rows_count"))
                if rows_count is not None:
                    expected_rows_count = expected_rows_count or rows_count
                    if rows_count != expected_rows_count:
                        errors.append(f"{label}_reference_delta_rows_count_mismatch")
                claim_elements_count = positive_int(metadata.get("reference_delta_claim_elements_count"))
                if claim_elements_count is not None:
                    expected_claim_elements_count = expected_claim_elements_count or claim_elements_count
                    if claim_elements_count != expected_claim_elements_count:
                        errors.append(f"{label}_reference_delta_claim_elements_count_mismatch")

    expected_decision = "production_shape_test_verified" if evidence_mode == "production_shape_test" else "production_official_evidence_verified"
    if get_path(packet, "decision.status") != expected_decision:
        errors.append(f"decision_status_must_be_{expected_decision}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--allow-production-shape-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate_packet(
            args.packet,
            allow_production_shape_test=args.allow_production_shape_test,
        )
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
