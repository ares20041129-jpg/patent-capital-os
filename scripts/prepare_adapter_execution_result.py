#!/usr/bin/env python3
"""Prepare adapter execution result artifacts from returned adapter evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

import build_case_queue
import validate_adapter_execution_result
import validate_artifact_hash_manifest
import validate_approved_adapter_preflight
import validate_filing_adapter_contract
import validate_filing_status_transition
import validate_receipt_capture


FORBIDDEN_KEYS = {
    "password",
    "private_key",
    "captcha_bypass",
    "mfa_secret",
    "session_token",
    "cookie",
    "raw_credentials",
}

REQUIRED_SOURCE_PATHS = [
    "case_id",
    "execution_mode",
    "adapter.name",
    "adapter.version",
    "execution.action_started_at",
    "execution.action_completed_at",
    "execution.response_state",
    "execution.official_system_touched",
    "execution.official_submission_performed",
    "execution.adapter_execution_performed",
    "execution.submission_reference",
    "execution.official_status_snapshot_file",
    "execution.official_status_snapshot_hash",
    "execution.submitted_file_list_file",
    "execution.submitted_file_list_hash",
    "execution.payment_status",
    "receipt_followup.docket_entry_id",
    "receipt_followup.next_deadline_due_date",
    "decision.status",
    "decision.reason",
]

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_reference(reference: Any, base_dir: Path) -> Path:
    path = Path(str(reference or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def copy_evidence_file(raw_path: Any, source_dir: Path, output_dir: Path) -> tuple[str, str, Path]:
    source_file = resolve_reference(raw_path, source_dir)
    if not source_file.exists():
        raise RuntimeError(f"evidence_file_not_found: {raw_path}")
    dest = output_dir / source_file.name
    if source_file.resolve() != dest.resolve():
        shutil.copy2(source_file, dest)
    return dest.name, sha256_file(dest), dest


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def q(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


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


def render_yaml(path: Path, data: dict[str, Any]) -> None:
    def lines_for(mapping: dict[str, Any], indent: int = 0) -> list[str]:
        lines: list[str] = []
        prefix = " " * indent
        for key, value in mapping.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.extend(lines_for(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        lines.extend(lines_for(item, indent + 4))
                    else:
                        lines.append(f"{prefix}  - {q(item)}")
            elif isinstance(value, bool):
                lines.append(f"{prefix}{key}: {str(value).lower()}")
            else:
                lines.append(f"{prefix}{key}: {q(value)}")
        return lines

    path.write_text("\n".join(lines_for(data)) + "\n", encoding="utf-8")


def reference_delta_metadata(approved_preflight: dict[str, Any]) -> dict[str, Any]:
    materials = approved_preflight.get("application_materials") if isinstance(approved_preflight.get("application_materials"), dict) else {}
    reference_hash = materials.get("reference_patent_delta_hash")
    if not reference_hash:
        return {}
    return {
        "application_materials_hash": materials.get("hash"),
        "reference_patent_delta_hash": reference_hash,
        "reference_delta_rows_count": materials.get("reference_delta_rows_count"),
        "reference_delta_claim_elements_count": materials.get("reference_delta_claim_elements_count"),
        "reference_delta_boundary_preserved": materials.get("reference_delta_boundary_preserved") is True,
    }


def artifact_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [
            {
                "path": rel(path, output_dir),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
    }


def validate_source(
    source: dict[str, Any],
    approved_preflight: dict[str, Any],
    adapter_request: dict[str, Any],
    approved_status: dict[str, Any],
    source_dir: Path | None = None,
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_SOURCE_PATHS:
        if is_blank(get_path(source, path)):
            errors.append(f"missing_required_field: {path}")

    forbidden = has_forbidden_key(source)
    if forbidden:
        errors.append(f"forbidden_field_present: {forbidden}")

    case_id = str(approved_preflight.get("case_id") or "")
    if source.get("case_id") != case_id or adapter_request.get("case_id") != case_id or approved_status.get("case_id") != case_id:
        errors.append("case_id_mismatch")
    if source.get("execution_mode") != "approved_adapter":
        errors.append("execution_mode_must_be_approved_adapter")
    if get_path(source, "adapter.name") != get_path(approved_preflight, "adapter.name"):
        errors.append("adapter_name_mismatch")
    if get_path(source, "adapter.version") != get_path(approved_preflight, "adapter.version"):
        errors.append("adapter_version_mismatch")
    readiness_hash = get_path(approved_preflight, "adapter.production_readiness.packet_hash")
    request_readiness_hash = adapter_request.get("adapter_production_readiness_hash")
    status_readiness_hash = approved_status.get("production_adapter_readiness_hash")
    session_hash = get_path(approved_preflight, "official_channel.session_authorization.packet_hash")
    request_session_hash = adapter_request.get("official_session_authorization_hash")
    status_session_hash = approved_status.get("official_session_authorization_hash")
    session_reference_hash = get_path(approved_preflight, "official_channel.session_authorization.session_reference_hash")
    request_session_reference_hash = adapter_request.get("official_session_reference_hash")
    status_session_reference_hash = approved_status.get("official_session_reference_hash")
    require_hash(readiness_hash, "adapter.production_readiness.packet_hash", errors)
    require_hash(request_readiness_hash, "adapter_request.adapter_production_readiness_hash", errors)
    require_hash(session_hash, "official_channel.session_authorization.packet_hash", errors)
    require_hash(request_session_hash, "adapter_request.official_session_authorization_hash", errors)
    require_hash(status_session_hash, "approved_status.official_session_authorization_hash", errors)
    require_hash(session_reference_hash, "official_channel.session_authorization.session_reference_hash", errors)
    require_hash(request_session_reference_hash, "adapter_request.official_session_reference_hash", errors)
    require_hash(status_session_reference_hash, "approved_status.official_session_reference_hash", errors)
    if readiness_hash and request_readiness_hash and readiness_hash != request_readiness_hash:
        errors.append("adapter_production_readiness_hash_mismatch_between_preflight_and_request")
    if status_readiness_hash and readiness_hash and status_readiness_hash != readiness_hash:
        errors.append("adapter_production_readiness_hash_mismatch_between_preflight_and_status")
    if session_hash and request_session_hash and session_hash != request_session_hash:
        errors.append("official_session_authorization_hash_mismatch_between_preflight_and_request")
    if status_session_hash and session_hash and status_session_hash != session_hash:
        errors.append("official_session_authorization_hash_mismatch_between_preflight_and_status")
    if session_reference_hash and request_session_reference_hash and session_reference_hash != request_session_reference_hash:
        errors.append("official_session_reference_hash_mismatch_between_preflight_and_request")
    if status_session_reference_hash and session_reference_hash and status_session_reference_hash != session_reference_hash:
        errors.append("official_session_reference_hash_mismatch_between_preflight_and_status")
    if approved_status.get("production_adapter_readiness") != "passed":
        errors.append("input_status_requires_production_adapter_readiness_passed")
    if approved_status.get("official_session_authorization") != "passed":
        errors.append("input_status_requires_official_session_authorization_passed")
    if get_path(source, "execution.response_state") != "submitted_pending_receipt":
        errors.append("response_state_must_be_submitted_pending_receipt")
    for path in [
        "execution.official_system_touched",
        "execution.official_submission_performed",
        "execution.adapter_execution_performed",
    ]:
        if get_path(source, path) is not True:
            errors.append(f"{path}_must_be_true")
    require_hash(get_path(source, "execution.official_status_snapshot_hash"), "execution.official_status_snapshot_hash", errors)
    require_hash(get_path(source, "execution.submitted_file_list_hash"), "execution.submitted_file_list_hash", errors)
    validate_file_hash_reference(
        source,
        "execution.official_status_snapshot_file",
        "execution.official_status_snapshot_hash",
        "execution.official_status_snapshot",
        source_dir,
        errors,
    )
    validate_file_hash_reference(
        source,
        "execution.submitted_file_list_file",
        "execution.submitted_file_list_hash",
        "execution.submitted_file_list",
        source_dir,
        errors,
    )
    payment_status = str(get_path(source, "execution.payment_status") or "").lower()
    if payment_status not in {"paid", "pending", "not_due", "deferred"}:
        errors.append("execution.payment_status_invalid")
    if payment_status == "paid":
        require_hash(get_path(source, "execution.payment_receipt_hash"), "execution.payment_receipt_hash", errors)
    if source.get("official_receipt_hash") or source.get("application_number"):
        errors.append("source_must_not_include_receipt_or_application_number")
    if get_path(source, "decision.status") != "submitted_pending_receipt":
        errors.append("decision_status_must_be_submitted_pending_receipt")
    if approved_status.get("status") != "approved_for_adapter_execution":
        errors.append("input_status_must_be_approved_for_adapter_execution")
    reference_metadata = reference_delta_metadata(approved_preflight)
    if reference_metadata:
        for packet, label in [(adapter_request, "adapter_request"), (approved_status, "approved_status")]:
            if packet.get("application_materials_hash") != reference_metadata.get("application_materials_hash"):
                errors.append(f"{label}_application_materials_hash_mismatch")
            if packet.get("reference_patent_delta_hash") != reference_metadata.get("reference_patent_delta_hash"):
                errors.append(f"{label}_reference_patent_delta_hash_mismatch")
            if packet.get("reference_delta_boundary_preserved") is not True:
                errors.append(f"{label}_reference_delta_boundary_must_be_true")
    if get_path(source, "execution.benchmark_mock") is True:
        warnings.append("benchmark_mock_not_real_official_submission")
    return len(errors) == 0, errors, warnings


def render_report(case_id: str, source: dict[str, Any], reference_delta_hash: str = "") -> str:
    benchmark = "yes" if get_path(source, "execution.benchmark_mock") is True else "no"
    lines = [
        "# Adapter Execution Result Report",
        "",
        f"Case ID: {case_id}",
        "Status: submitted_pending_receipt",
        f"Benchmark mock: {benchmark}",
        "",
        "## Boundary",
        "",
        "This artifact records returned adapter execution evidence. It is not a real CNIPA submission when benchmark mock is yes.",
        "It is not a real filing unless the source evidence comes from a lawful approved adapter action outside this generator.",
        "It is not a real receipt and does not contain an application number.",
        "The next allowed step is receipt capture.",
        "",
    ]
    if reference_delta_hash:
        lines.extend(
            [
                "## Reference Delta Boundary",
                "",
                f"Reference-patent delta hash: {reference_delta_hash}",
                "Reference-patent delta evidence remains boundary and claim-strategy evidence only. It is not applicant claim support, legal advice, filing authorization, official submission evidence, receipt evidence, or application-number evidence.",
                "",
            ]
        )
    return "\n".join(lines)


def prepare(preflight_dir: Path, source_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    preflight_root = preflight_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    approved_preflight_path = preflight_root / "approved-adapter-preflight.json"
    adapter_request_path = preflight_root / "filing-adapter-request.json"
    approved_status_path = preflight_root / "filing-status.json"
    if not all(path.exists() for path in [approved_preflight_path, adapter_request_path, approved_status_path]):
        raise RuntimeError("approved_adapter_preflight_dir_missing_required_artifacts")

    approved_preflight = load_json(approved_preflight_path)
    adapter_request = load_json(adapter_request_path)
    approved_status = load_json(approved_status_path)
    source = load_json(source_path)

    preflight_ok, preflight_errors, preflight_warnings = validate_approved_adapter_preflight.validate(
        approved_preflight,
        base_dir=preflight_root,
    )
    request_ok, request_errors, request_warnings = validate_filing_adapter_contract.validate_request(adapter_request, base_dir=preflight_root)
    approved_status_ok, approved_status_errors, approved_status_warnings = validate_filing_status_transition.validate(approved_status)
    source_ok, source_errors, source_warnings = validate_source(source, approved_preflight, adapter_request, approved_status, source_path.parent)

    if not all([preflight_ok, request_ok, approved_status_ok, source_ok]):
        return {
            "ok": False,
            "case_id": approved_preflight.get("case_id"),
            "preflight_errors": preflight_errors,
            "request_errors": request_errors,
            "approved_status_errors": approved_status_errors,
            "source_errors": source_errors,
            "preflight_warnings": preflight_warnings,
            "request_warnings": request_warnings,
            "approved_status_warnings": approved_status_warnings,
            "source_warnings": source_warnings,
            "generator_official_system_touched": False,
            "generator_official_submission_performed": False,
            "generator_adapter_execution_performed": False,
        }, 1

    case_id = str(approved_preflight["case_id"])
    legal_gate_mode = str(
        approved_status.get("legal_gate_mode")
        or get_path(approved_preflight, "authorization.authorization_packet_type")
        or ""
    )
    ai_self_filing = legal_gate_mode == "ai_self_filing_no_external_lawyer"
    final_hash = str(adapter_request.get("final_package_hash") or get_path(approved_preflight, "package.final_package_hash") or "")
    reviewed_hash = str(adapter_request.get("reviewed_package_hash") or get_path(approved_preflight, "package.reviewed_package_hash") or "")
    if final_hash != reviewed_hash:
        return {
            "ok": False,
            "case_id": case_id,
            "errors": ["hash_mismatch: final_package_hash != reviewed_package_hash"],
            "generator_official_system_touched": False,
            "generator_official_submission_performed": False,
            "generator_adapter_execution_performed": False,
        }, 1

    source_copy_path = output_root / "adapter-execution-source.json"
    receipt_pending_path = output_root / "receipt-capture-pending.yaml"
    audit_path = output_root / "audit-log-entry.yaml"
    docket_path = output_root / "docket-entry.yaml"
    execution_path = output_root / "adapter-execution-result.json"
    response_path = output_root / "filing-adapter-response.json"
    status_path = output_root / "filing-status.json"
    report_path = output_root / "adapter-execution-report.md"
    hashes_path = output_root / "artifact-hashes.json"

    status_snapshot_file, status_snapshot_hash, status_snapshot_path = copy_evidence_file(
        get_path(source, "execution.official_status_snapshot_file"),
        source_path.parent,
        output_root,
    )
    submitted_file_list_file, submitted_file_list_hash, submitted_file_list_path = copy_evidence_file(
        get_path(source, "execution.submitted_file_list_file"),
        source_path.parent,
        output_root,
    )
    source["execution"]["official_status_snapshot_file"] = status_snapshot_file
    source["execution"]["official_status_snapshot_hash"] = status_snapshot_hash
    source["execution"]["submitted_file_list_file"] = submitted_file_list_file
    source["execution"]["submitted_file_list_hash"] = submitted_file_list_hash

    write_json(source_copy_path, source)

    submitted_at = str(get_path(source, "execution.action_completed_at"))
    submission_reference = str(get_path(source, "execution.submission_reference"))
    receipt_pending = {
        "case_id": case_id,
        "filing_action_id": submission_reference,
        "status": "submitted_pending_receipt",
        "submitted_at": submitted_at,
        "official_system": adapter_request.get("official_system"),
        "official_session_authorization_hash": str(get_path(approved_preflight, "official_channel.session_authorization.packet_hash") or adapter_request.get("official_session_authorization_hash") or ""),
        "official_session_reference_hash": str(get_path(approved_preflight, "official_channel.session_authorization.session_reference_hash") or adapter_request.get("official_session_reference_hash") or ""),
        "official_receipt": {
            "receipt_id": "",
            "receipt_file": "",
            "receipt_hash": "",
        },
        "application": {
            "application_number": "",
            "filing_date": "",
            "official_file_list_hash": "",
        },
        "fees": {
            "payment_status": get_path(source, "execution.payment_status"),
            "payment_receipt_file": "",
            "payment_receipt_hash": get_path(source, "execution.payment_receipt_hash") or "",
        },
        "docket": {
            "docket_entry_id": get_path(source, "receipt_followup.docket_entry_id"),
            "next_deadlines": [
                {
                    "name": get_path(source, "receipt_followup.next_deadline_name") or "capture official filing receipt",
                    "due_date": get_path(source, "receipt_followup.next_deadline_due_date"),
                }
            ],
        },
        "evidence_notes": get_path(source, "receipt_followup.evidence_notes"),
    }
    render_yaml(receipt_pending_path, receipt_pending)

    request_hash = sha256_file(adapter_request_path)
    approved_preflight_hash = sha256_file(approved_preflight_path)
    adapter_readiness_hash = str(get_path(approved_preflight, "adapter.production_readiness.packet_hash") or adapter_request.get("adapter_production_readiness_hash") or "")
    session_authorization_hash = str(get_path(approved_preflight, "official_channel.session_authorization.packet_hash") or adapter_request.get("official_session_authorization_hash") or "")
    session_reference_hash = str(get_path(approved_preflight, "official_channel.session_authorization.session_reference_hash") or adapter_request.get("official_session_reference_hash") or "")
    reference_metadata = reference_delta_metadata(approved_preflight)
    receipt_pending_hash = sha256_file(receipt_pending_path)
    audit = {
        "case_id": case_id,
        "event_id": "adapter-execution-" + case_id,
        "event_type": "adapter_execution_submitted_pending_receipt",
        "actor": get_path(source, "adapter.name"),
        "actor_role": "approved filing adapter",
        "timestamp": submitted_at,
        "input_hashes": [final_hash, request_hash, approved_preflight_hash, adapter_readiness_hash, session_authorization_hash, session_reference_hash],
        "output_hashes": [
            status_snapshot_hash,
            submitted_file_list_hash,
            receipt_pending_hash,
        ],
        "decision": "submitted_pending_receipt",
        "external_system": adapter_request.get("official_system"),
        "receipt_or_error_evidence": "receipt-capture-pending.yaml",
        "notes": "Benchmark mock only." if get_path(source, "execution.benchmark_mock") is True else "Adapter evidence captured; receipt remains pending.",
    }
    if reference_metadata:
        audit["input_hashes"].extend(
            [
                reference_metadata["application_materials_hash"],
                reference_metadata["reference_patent_delta_hash"],
            ]
        )
    docket = {
        "case_id": case_id,
        "docket_entry_id": get_path(source, "receipt_followup.docket_entry_id"),
        "jurisdiction": "CN",
        "event_type": "submitted_pending_receipt",
        "event_date": submitted_at,
        "source_evidence": "adapter-execution-result.json",
        "source_hash": "see artifact-hashes.json",
        "related_application_number": "",
        "next_deadline": get_path(source, "receipt_followup.next_deadline_due_date"),
        "notes": "Do not mark receipt or application number until receipt capture evidence validates.",
    }
    render_yaml(audit_path, audit)
    render_yaml(docket_path, docket)
    audit_hash = sha256_file(audit_path)
    docket_hash = sha256_file(docket_path)

    execution_result = {
        "case_id": case_id,
        "execution_mode": "approved_adapter",
        "adapter_name": get_path(source, "adapter.name"),
        "adapter_version": get_path(source, "adapter.version"),
        "adapter_request": rel(adapter_request_path, output_root),
        "adapter_request_hash": request_hash,
        "approved_adapter_preflight": rel(approved_preflight_path, output_root),
        "approved_adapter_preflight_hash": approved_preflight_hash,
        "adapter_production_readiness_hash": adapter_readiness_hash,
        "official_session_authorization_hash": session_authorization_hash,
        "official_session_reference_hash": session_reference_hash,
        "official_system": adapter_request.get("official_system"),
        "official_action": "submit_package",
        "action_started_at": get_path(source, "execution.action_started_at"),
        "action_completed_at": submitted_at,
        "response_state": "submitted_pending_receipt",
        "next_status": "submitted_pending_receipt",
        "official_system_touched": True,
        "official_submission_performed": True,
        "adapter_execution_performed": True,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_adapter_execution_performed": False,
        "evidence_claims_official_system_touched": True,
        "evidence_claims_official_submission_performed": True,
        "evidence_claims_adapter_execution_performed": True,
        "final_package_hash": final_hash,
        "reviewed_package_hash": reviewed_hash,
        "receipt_capture_status": "submitted_pending_receipt",
        "receipt_capture_plan": "receipt-capture-pending.yaml",
        "receipt_capture_plan_hash": receipt_pending_hash,
        "audit_log_entry": "audit-log-entry.yaml",
        "audit_log_entry_hash": audit_hash,
        "docket_entry": "docket-entry.yaml",
        "docket_entry_hash": docket_hash,
        "official_submission_evidence": {
            "submission_reference": submission_reference,
            "official_status_snapshot_file": status_snapshot_file,
            "official_status_snapshot_hash": status_snapshot_hash,
            "submitted_package_hash": final_hash,
            "submitted_file_list_file": submitted_file_list_file,
            "submitted_file_list_hash": submitted_file_list_hash,
        },
        "fees": {
            "payment_status": get_path(source, "execution.payment_status"),
            "payment_receipt_hash": get_path(source, "execution.payment_receipt_hash") or "",
        },
        "official_receipt_hash": "",
        "application_number": "",
        "benchmark_mock": get_path(source, "execution.benchmark_mock") is True,
        "decision": {
            "status": "submitted_pending_receipt",
            "reason": get_path(source, "decision.reason"),
        },
    }
    if ai_self_filing:
        execution_result["legal_gate_mode"] = legal_gate_mode
        execution_result["ai_self_filing_gate"] = "passed"
        execution_result["external_lawyer_involved"] = False
    if reference_metadata:
        execution_result.update(reference_metadata)
    write_json(execution_path, execution_result)
    execution_hash = sha256_file(execution_path)

    response = {
        "case_id": case_id,
        "execution_mode": "approved_adapter",
        "adapter_name": get_path(source, "adapter.name"),
        "adapter_version": get_path(source, "adapter.version"),
        "response_state": "submitted_pending_receipt",
        "official_system_touched": True,
        "official_submission_performed": True,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_adapter_execution_performed": False,
        "evidence_claims_official_system_touched": True,
        "evidence_claims_official_submission_performed": True,
        "evidence_claims_adapter_execution_performed": True,
        "final_package_hash": final_hash,
        "reviewed_package_hash": reviewed_hash,
        "receipt_capture_status": "submitted_pending_receipt",
        "next_status": "submitted_pending_receipt",
        "handoff_required": False,
        "human_action": "",
        "errors": [],
        "warnings": ["receipt_capture_followup_required"] + (
            ["mock_adapter_execution_for_benchmark_only"] if get_path(source, "execution.benchmark_mock") is True else []
        ),
        "approved_adapter_preflight_hash": approved_preflight_hash,
        "adapter_production_readiness_hash": adapter_readiness_hash,
        "official_session_authorization_hash": session_authorization_hash,
        "official_session_reference_hash": session_reference_hash,
        "adapter_execution_result": "adapter-execution-result.json",
        "adapter_execution_result_hash": execution_hash,
        "audit_log_entry": "audit-log-entry.yaml",
    }
    if ai_self_filing:
        response["legal_gate_mode"] = legal_gate_mode
        response["external_lawyer_involved"] = False
    if reference_metadata:
        response.update(reference_metadata)
    write_json(response_path, response)

    status = {
        "case_id": case_id,
        "previous_status": "approved_for_adapter_execution",
        "status": "submitted_pending_receipt",
        "legal_gate": "passed",
        "official_channel_preflight": "passed",
        "approved_adapter_preflight": "passed",
        "production_adapter_readiness": "passed",
        "production_adapter_readiness_hash": adapter_readiness_hash,
        "official_session_authorization": "passed",
        "official_session_authorization_hash": session_authorization_hash,
        "official_session_reference_hash": session_reference_hash,
        "adapter_execution": "performed_mock" if get_path(source, "execution.benchmark_mock") is True else "performed",
        "decision": "submitted_pending_receipt_mock_for_benchmark_only"
        if get_path(source, "execution.benchmark_mock") is True
        else "submitted_pending_receipt",
        "final_package_hash": final_hash,
        "reviewed_package_hash": reviewed_hash,
        "official_system_touched": True,
        "official_submission_performed": True,
        "adapter_execution_performed": True,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_adapter_execution_performed": False,
        "evidence_claims_official_system_touched": True,
        "evidence_claims_official_submission_performed": True,
        "evidence_claims_adapter_execution_performed": True,
        "official_receipt_hash": "",
        "application_number": "",
        "benchmark_mock": get_path(source, "execution.benchmark_mock") is True,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    if ai_self_filing:
        status["legal_gate_mode"] = legal_gate_mode
        status["ai_self_filing_gate"] = "passed"
        status["external_lawyer_involved"] = False
    if reference_metadata:
        status.update(reference_metadata)
    write_json(status_path, status)
    report_path.write_text(render_report(case_id, source, str(reference_metadata.get("reference_patent_delta_hash") or "")), encoding="utf-8")

    write_json(
        hashes_path,
        artifact_manifest(
            output_root,
            case_id,
            [
                source_copy_path,
                execution_path,
                response_path,
                receipt_pending_path,
                status_path,
                report_path,
                audit_path,
                docket_path,
                status_snapshot_path,
                submitted_file_list_path,
            ],
        ),
    )

    result_ok, result_errors, result_warnings = validate_adapter_execution_result.validate(execution_result, base_dir=output_root)
    response_ok, response_errors, response_warnings = validate_filing_adapter_contract.validate_response(response, base_dir=output_root)
    receipt_ok, receipt_errors, receipt_warnings = validate_receipt_capture.validate(
        validate_receipt_capture.load_packet(receipt_pending_path),
        base_dir=output_root,
    )
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)

    ok = result_ok and response_ok and receipt_ok and status_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "adapter_execution_source": str(source_copy_path),
            "adapter_execution_result": str(execution_path),
            "filing_adapter_response": str(response_path),
            "receipt_capture_pending": str(receipt_pending_path),
            "filing_status": str(status_path),
            "adapter_execution_report": str(report_path),
            "audit_log_entry": str(audit_path),
            "docket_entry": str(docket_path),
            "artifact_hashes": str(hashes_path),
        },
        "source_warnings": source_warnings,
        "result_errors": result_errors,
        "result_warnings": result_warnings,
        "response_errors": response_errors,
        "response_warnings": response_warnings,
        "receipt_errors": receipt_errors,
        "receipt_warnings": receipt_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "status": "submitted_pending_receipt",
        "adapter_production_readiness_hash": adapter_readiness_hash,
        "official_session_authorization_hash": session_authorization_hash,
        "official_session_reference_hash": session_reference_hash,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_adapter_execution_performed": False,
        "evidence_claims_official_system_touched": True,
        "evidence_claims_official_submission_performed": True,
        "evidence_claims_adapter_execution_performed": True,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("approved_adapter_preflight_dir", type=Path)
    parser.add_argument("adapter_execution_source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(
            args.approved_adapter_preflight_dir,
            args.adapter_execution_source,
            args.output_dir,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "generator_official_system_touched": False,
            "generator_official_submission_performed": False,
            "generator_adapter_execution_performed": False,
        }, 1
    rendered = json.dumps(response, ensure_ascii=False, indent=2)
    if args.json:
        print(rendered)
    else:
        print("PASS" if response.get("ok") else "FAIL")
        print(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
