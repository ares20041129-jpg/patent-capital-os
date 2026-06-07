#!/usr/bin/env python3
"""Prepare approved-adapter preflight artifacts without executing a filing adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import build_case_queue
import validate_approved_adapter_preflight
import validate_artifact_hash_manifest
import validate_ai_self_filing_authorization
import validate_filing_adapter_contract
import validate_filing_package_manifest
import validate_filing_status_transition
import validate_official_channel_preflight
import validate_official_session_authorization
import validate_production_adapter_readiness
import validate_receipt_capture
import validate_submission_packet


REQUIRED_SOURCE_PATHS = [
    "case_id",
    "adapter.name",
    "adapter.version",
    "adapter.approved_for_production",
    "adapter.registry_entry_hash",
    "adapter.dry_run_result_hash",
    "adapter.security_review.reviewed_by",
    "adapter.security_review.reviewed_at",
    "adapter.security_review.result",
    "adapter.security_review.review_artifact_hash",
    "adapter.security_review.scope",
    "production_readiness.packet",
    "official_session_authorization.packet",
    "authorization.account_owner_authorization",
    "authorization.allowed_actions",
    "authorization.two_person_approval.legal_approver",
    "authorization.two_person_approval.ops_approver",
    "authorization.two_person_approval.approved_at",
    "authorization.two_person_approval.evidence_hash",
    "credential_handling.raw_credentials_in_request",
    "credential_handling.private_keys_in_request",
    "credential_handling.captcha_bypass",
    "credential_handling.mfa_secret_in_request",
    "credential_handling.session_token_in_request",
    "credential_handling.stores_credentials",
    "execution_controls.payment_allowed",
    "decision.status",
    "decision.reason",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return load_json(path)
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("YAML input requires PyYAML.") from exc
    return yaml.safe_load(text) or {}


def find_authorization_packet(package_root: Path) -> tuple[Path, str]:
    submission_packet = package_root / "submission-authorization-packet.json"
    ai_self_filing_packet = package_root / "ai-self-filing-authorization-packet.json"
    if submission_packet.exists():
        return submission_packet, "counsel_or_agent_review"
    if ai_self_filing_packet.exists():
        return ai_self_filing_packet, "ai_self_filing_no_external_lawyer"
    raise RuntimeError("validated_package_dir_missing_authorization_packet")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def resolve_reference(reference: Any, origin_dir: Path) -> Path:
    path = Path(str(reference))
    if path.is_absolute():
        return path
    return (origin_dir / path).resolve()


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


def validate_source(data: dict[str, Any], expected_case_id: str) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for path in REQUIRED_SOURCE_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")
    if data.get("case_id") != expected_case_id:
        errors.append("case_id_mismatch_between_adapter_source_and_ready_case")
    if get_path(data, "adapter.approved_for_production") is not True:
        errors.append("adapter_must_be_approved_for_production")
    if str(get_path(data, "adapter.security_review.result") or "").lower() != "passed":
        errors.append("adapter_security_review_must_pass")
    if get_path(data, "authorization.two_person_approval.legal_approver") == get_path(data, "authorization.two_person_approval.ops_approver"):
        errors.append("two_person_approval_requires_distinct_approvers")
    for path in [
        "credential_handling.raw_credentials_in_request",
        "credential_handling.private_keys_in_request",
        "credential_handling.captcha_bypass",
        "credential_handling.mfa_secret_in_request",
        "credential_handling.session_token_in_request",
        "credential_handling.stores_credentials",
    ]:
        if get_path(data, path) is not False:
            errors.append(f"credential_flag_must_be_false: {path}")
    if get_path(data, "decision.status") != "approved_for_adapter_execution":
        errors.append("decision_status_must_be_approved_for_adapter_execution")
    return len(errors) == 0, errors, warnings


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


def render_report(
    case_id: str,
    legal_gate_mode: str,
    readiness_hash: str,
    session_hash: str,
    session_reference_hash: str,
    application_materials_hash: str = "",
    reference_delta_hash: str = "",
) -> str:
    route_line = (
        "Route: AI self-filing with no external lawyer or patent agent"
        if legal_gate_mode == "ai_self_filing_no_external_lawyer"
        else "Route: counsel or patent-agent reviewed package"
    )
    return "\n".join(
        [
            "# Approved Adapter Boundary Report",
            "",
            "Execution mode: approved_adapter_preflight",
            f"Case ID: {case_id}",
            route_line,
            "Decision: approved_for_adapter_execution",
            f"Legal gate mode: {legal_gate_mode}",
            "Production adapter readiness: passed",
            f"Production adapter readiness hash: {readiness_hash}",
            "Official session authorization: passed",
            f"Official session authorization hash: {session_hash}",
            f"Official session reference hash: {session_reference_hash}",
            f"Application materials hash: {application_materials_hash or 'not present'}",
            f"Reference-patent delta hash: {reference_delta_hash or 'not present'}",
            "Official system touched: no",
            "Official submission performed: no",
            "Adapter execution performed: no",
            "",
            "## Reference Delta Boundary",
            "",
            "When present, reference-patent delta evidence remains boundary and claim-strategy evidence only. It is not applicant claim support, legal advice, filing authorization, official submission evidence, receipt evidence, or application-number evidence.",
            "",
            "## Boundary",
            "",
            "This preflight permits only a later approved adapter execution attempt. It is not evidence of upload, signature, payment, official submission, receipt, acceptance, or application number.",
            "",
        ]
    )


def prepare(ready_dir: Path, validated_package_dir: Path, adapter_source_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    ready_root = ready_dir.resolve()
    package_root = validated_package_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    ready_status_path = ready_root / "filing-status.json"
    official_preflight_path = ready_root / "official-channel-preflight.yaml"
    receipt_plan_path = ready_root / "receipt-capture-plan.yaml"
    manifest_path = package_root / "filing-package-manifest.yaml"
    if not all(path.exists() for path in [ready_status_path, official_preflight_path, receipt_plan_path, manifest_path]):
        raise RuntimeError("ready_or_package_dir_missing_required_artifacts")
    packet_path, legal_gate_mode = find_authorization_packet(package_root)

    ready_status = load_json(ready_status_path)
    case_id = str(ready_status.get("case_id") or "")
    source = load_json(adapter_source_path)
    source_ok, source_errors, source_warnings = validate_source(source, case_id)
    ready_ok, ready_errors, ready_warnings = validate_filing_status_transition.validate(ready_status)
    preflight_data = load_yaml_or_json(official_preflight_path)
    preflight_ok, preflight_errors, preflight_warnings = validate_official_channel_preflight.validate(preflight_data)
    receipt_data = load_yaml_or_json(receipt_plan_path)
    receipt_ok, receipt_errors, receipt_warnings = validate_receipt_capture.validate(receipt_data, allow_plan_only=True, base_dir=ready_root)
    packet = load_json(packet_path)
    if legal_gate_mode == "ai_self_filing_no_external_lawyer":
        packet_ok, packet_errors, packet_warnings = validate_ai_self_filing_authorization.validate(packet, base_dir=package_root)
    else:
        packet_ok, packet_errors, packet_warnings = validate_submission_packet.validate(packet, base_dir=package_root)
    manifest = validate_filing_package_manifest.load_packet(manifest_path)
    manifest_ok, manifest_errors, manifest_warnings = validate_filing_package_manifest.validate(manifest, base_dir=package_root)

    readiness_errors: list[str] = []
    readiness_warnings: list[str] = []
    readiness_packet: dict[str, Any] = {}
    readiness_packet_path: Path | None = None
    readiness_ref = get_path(source, "production_readiness.packet")
    if is_blank(readiness_ref):
        readiness_errors.append("missing_required_field: production_readiness.packet")
    else:
        readiness_packet_path = resolve_reference(readiness_ref, adapter_source_path.parent)
        if not readiness_packet_path.exists():
            readiness_errors.append("production_readiness_packet_missing")
        else:
            readiness_packet = load_json(readiness_packet_path)
            _, packet_errors, packet_warnings = validate_production_adapter_readiness.validate_packet(readiness_packet)
            readiness_errors.extend(packet_errors)
            readiness_warnings.extend(packet_warnings)
            if get_path(readiness_packet, "adapter.name") != get_path(source, "adapter.name"):
                readiness_errors.append("production_readiness_adapter_name_mismatch")
            if get_path(readiness_packet, "adapter.version") != get_path(source, "adapter.version"):
                readiness_errors.append("production_readiness_adapter_version_mismatch")
            if get_path(readiness_packet, "adapter.registry_entry_hash") != get_path(source, "adapter.registry_entry_hash"):
                readiness_errors.append("production_readiness_registry_entry_hash_mismatch")
            if get_path(readiness_packet, "official_system") != get_path(preflight_data, "official_system"):
                readiness_errors.append("production_readiness_official_system_mismatch")
            if legal_gate_mode == "ai_self_filing_no_external_lawyer":
                if get_path(readiness_packet, "legal_gate_mode") != "ai_self_filing_no_external_lawyer":
                    readiness_errors.append("ai_self_filing_requires_ai_readiness_legal_gate_mode")
                if get_path(readiness_packet, "external_lawyer_involved") is not False:
                    readiness_errors.append("ai_self_filing_requires_readiness_external_lawyer_false")
    readiness_ok = len(readiness_errors) == 0

    session_errors: list[str] = []
    session_warnings: list[str] = []
    session_packet: dict[str, Any] = {}
    session_packet_path: Path | None = None
    session_ref = get_path(source, "official_session_authorization.packet")
    if is_blank(session_ref):
        session_errors.append("missing_required_field: official_session_authorization.packet")
    else:
        session_packet_path = resolve_reference(session_ref, adapter_source_path.parent)
        if not session_packet_path.exists():
            session_errors.append("official_session_authorization_packet_missing")
        else:
            session_packet = load_json(session_packet_path)
            _, packet_errors, packet_warnings = validate_official_session_authorization.validate_packet(session_packet)
            session_errors.extend(packet_errors)
            session_warnings.extend(packet_warnings)
            if get_path(session_packet, "official_system") != get_path(preflight_data, "official_system"):
                session_errors.append("official_session_authorization_official_system_mismatch")
            if legal_gate_mode == "ai_self_filing_no_external_lawyer":
                if get_path(session_packet, "legal_gate_mode") != "ai_self_filing_no_external_lawyer":
                    session_errors.append("ai_self_filing_requires_ai_session_authorization_legal_gate_mode")
                if get_path(session_packet, "external_lawyer_involved") is not False:
                    session_errors.append("ai_self_filing_requires_session_authorization_external_lawyer_false")
    session_ok = len(session_errors) == 0

    if not all([source_ok, ready_ok, preflight_ok, receipt_ok, packet_ok, manifest_ok, readiness_ok, session_ok]):
        return {
            "ok": False,
            "case_id": case_id,
            "source_errors": source_errors,
            "ready_errors": ready_errors,
            "preflight_errors": preflight_errors,
            "receipt_errors": receipt_errors,
            "packet_errors": packet_errors,
            "manifest_errors": manifest_errors,
            "production_readiness_errors": readiness_errors,
            "official_session_authorization_errors": session_errors,
            "source_warnings": source_warnings,
            "ready_warnings": ready_warnings,
            "preflight_warnings": preflight_warnings,
            "receipt_warnings": receipt_warnings,
            "packet_warnings": packet_warnings,
            "manifest_warnings": manifest_warnings,
            "production_readiness_warnings": readiness_warnings,
            "official_session_authorization_warnings": session_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
            "adapter_execution_performed": False,
        }, 1

    output_preflight_path = output_root / "approved-adapter-preflight.json"
    adapter_request_path = output_root / "filing-adapter-request.json"
    status_path = output_root / "filing-status.json"
    report_path = output_root / "adapter-boundary-report.md"
    audit_plan_path = output_root / "audit-log-entry-plan.yaml"
    docket_plan_path = output_root / "docket-entry-plan.yaml"
    hashes_path = output_root / "artifact-hashes.json"

    final_hash = str(manifest.get("final_package_hash") or "")
    reviewed_hash = str(manifest.get("reviewed_package_hash") or "")
    attachment_hash = str(get_path(preflight_data, "package.attachment_list_hash") or "")
    preflight_hash = sha256_file(official_preflight_path)
    receipt_hash = sha256_file(receipt_plan_path)
    manifest_hash = sha256_file(manifest_path)
    packet_hash = sha256_file(packet_path)
    security_hash = str(get_path(source, "adapter.security_review.review_artifact_hash"))
    readiness_hash = sha256_file(readiness_packet_path) if readiness_packet_path else ""
    session_hash = sha256_file(session_packet_path) if session_packet_path else ""
    session_reference_hash = str(get_path(session_packet, "session_broker.session_reference_hash") or "")
    application_materials = preflight_data.get("application_materials") if isinstance(preflight_data.get("application_materials"), dict) else {}
    application_materials_hash = str(application_materials.get("hash") or "")
    reference_delta_hash = str(application_materials.get("reference_patent_delta_hash") or "")

    audit_plan = {
        "case_id": case_id,
        "event_id": "planned-adapter-audit-" + case_id,
        "event_type": "approved_adapter_execution_attempt_plan",
        "actor": get_path(source, "adapter.name"),
        "actor_role": "approved filing adapter",
        "timestamp": build_case_queue.utc_plus_8_now(),
        "input_hashes": [
            item
            for item in [
                final_hash,
                preflight_hash,
                receipt_hash,
                readiness_hash,
                session_hash,
                session_reference_hash,
                application_materials_hash,
                reference_delta_hash,
            ]
            if item
        ],
        "output_hashes": [],
        "approval_basis": get_path(source, "authorization.two_person_approval.evidence_hash"),
        "decision": "proceed",
        "external_system": get_path(preflight_data, "official_system"),
        "receipt_or_error_evidence": "capture after execution attempt",
        "notes": "Plan only. No adapter execution or official submission has occurred.",
    }
    docket_plan = {
        "case_id": case_id,
        "docket_entry_id": "planned-adapter-docket-" + case_id,
        "jurisdiction": manifest.get("jurisdiction"),
        "event_type": "approved_adapter_execution_planned",
        "event_date": build_case_queue.utc_plus_8_now(),
        "due_date": "on adapter execution day",
        "owner": get_path(source, "authorization.two_person_approval.ops_approver"),
        "status": "open",
        "source_evidence": "approved-adapter-preflight.json",
        "source_hash": "pending",
        "related_application_number": "",
        "notes": "Plan only; update after official receipt or error evidence.",
    }
    render_yaml(audit_plan_path, audit_plan)
    render_yaml(docket_plan_path, docket_plan)
    audit_hash = sha256_file(audit_plan_path)
    docket_hash = sha256_file(docket_plan_path)

    adapter = dict(source.get("adapter") or {})
    adapter["production_readiness"] = {
        "readiness_gate": "production_adapter_readiness_gate",
        "evidence_mode": "production_adapter_readiness",
        "packet": rel(readiness_packet_path, output_root) if readiness_packet_path else "",
        "packet_hash": readiness_hash,
        "validation_result": "passed",
        "approved_for_real_execution": True,
        "adapter_name": get_path(readiness_packet, "adapter.name"),
        "adapter_version": get_path(readiness_packet, "adapter.version"),
        "registry_entry_hash": get_path(readiness_packet, "adapter.registry_entry_hash"),
    }

    approved_preflight = {
        "case_id": case_id,
        "execution_mode": "approved_adapter",
        "adapter": adapter,
        "authorization": {
            "submission_authorization_packet": rel(packet_path, output_root),
            "submission_authorization_packet_hash": packet_hash,
            "authorization_packet_type": legal_gate_mode,
            "applicant_authorization_confirmed": True,
            "counsel_review_confirmed": legal_gate_mode == "counsel_or_agent_review",
            "ai_self_filing_confirmed": legal_gate_mode == "ai_self_filing_no_external_lawyer",
            "external_lawyer_involved": False if legal_gate_mode == "ai_self_filing_no_external_lawyer" else None,
            "self_filing_allowed": get_path(packet, "self_filing_eligibility.self_filing_allowed"),
            "mandatory_agent_required": get_path(packet, "self_filing_eligibility.mandatory_agent_required"),
            "foreign_or_hmt_applicant": get_path(packet, "self_filing_eligibility.foreign_or_hmt_applicant"),
            "agency_bypass_requested": get_path(packet, "self_filing_eligibility.agency_bypass_requested"),
            "account_owner_authorization": get_path(source, "authorization.account_owner_authorization"),
            "signature_authority_evidence": get_path(preflight_data, "signature.authority_evidence"),
            "payment_authority_evidence": get_path(preflight_data, "fees.payment_method_reference"),
            "allowed_actions": get_path(source, "authorization.allowed_actions"),
            "two_person_approval": get_path(source, "authorization.two_person_approval"),
        },
        "official_channel": {
            "preflight_file": rel(official_preflight_path, output_root),
            "preflight_hash": preflight_hash,
            "official_system": get_path(preflight_data, "official_system"),
            "automation_allowed": True,
            "bypasses_access_controls": False,
            "human_only_steps": [],
            "human_only_steps_resolved": True,
            "session_authorization": {
                "session_gate": "official_session_authorization_gate",
                "evidence_mode": "official_session_authorization",
                "packet": rel(session_packet_path, output_root) if session_packet_path else "",
                "packet_hash": session_hash,
                "validation_result": "passed",
                "approved_for_real_execution": True,
                "official_account_role": get_path(session_packet, "official_account.role"),
                "session_reference_hash": session_reference_hash,
                "authorization_scope_hash": get_path(session_packet, "official_account.authorization_scope_hash"),
            },
        },
        "package": {
            "manifest_file": rel(manifest_path, output_root),
            "manifest_hash": manifest_hash,
            "final_package_hash": final_hash,
            "reviewed_package_hash": reviewed_hash,
            "xml_validation_result": get_path(manifest, "xml_validation.validation_result"),
            "attachment_list_hash": attachment_hash,
        },
        **({"application_materials": application_materials} if application_materials else {}),
        "evidence": {
            "receipt_capture_plan": rel(receipt_plan_path, output_root),
            "receipt_capture_plan_hash": receipt_hash,
            "audit_log_entry_plan": "audit-log-entry-plan.yaml",
            "audit_log_entry_plan_hash": audit_hash,
            "docket_entry_plan": "docket-entry-plan.yaml",
            "docket_entry_plan_hash": docket_hash,
        },
        "credential_handling": source.get("credential_handling"),
        "execution_controls": {
            "requested_action": "submit_package",
            "payment_allowed": get_path(source, "execution_controls.payment_allowed"),
            "stop_on_hash_mismatch": True,
            "stop_on_human_only_step": True,
            "stop_on_access_control_bypass": True,
            "receipt_capture_required": True,
            "audit_log_required": True,
            "docket_update_required": True,
        },
        "decision": {
            "status": "approved_for_adapter_execution",
            "reason": get_path(source, "decision.reason"),
            "next_status_if_success": "submitted_pending_receipt",
        },
    }
    write_json(output_preflight_path, approved_preflight)
    approved_ok, approved_errors, approved_warnings = validate_approved_adapter_preflight.validate(
        approved_preflight,
        base_dir=output_root,
    )

    adapter_request = {
        "case_id": case_id,
        "execution_mode": "approved_adapter",
        "requested_action": "submit_package",
        "official_system": get_path(preflight_data, "official_system"),
        "account_role": get_path(preflight_data, "account.role"),
        "authorization_evidence": get_path(preflight_data, "account.authorization_evidence"),
        "signature_authority_evidence": get_path(preflight_data, "signature.authority_evidence"),
        "payment_authority_evidence": get_path(preflight_data, "fees.payment_method_reference"),
        "final_package_hash": final_hash,
        "reviewed_package_hash": reviewed_hash,
        "package_manifest": rel(manifest_path, output_root),
        **({"application_materials_hash": application_materials_hash} if application_materials_hash else {}),
        **({"reference_patent_delta_hash": reference_delta_hash} if reference_delta_hash else {}),
        **({"reference_delta_boundary_preserved": application_materials.get("reference_delta_boundary_preserved")} if reference_delta_hash else {}),
        "receipt_capture_destination": get_path(preflight_data, "receipt_capture.destination"),
        "human_only_steps": [],
        "approved_adapter_preflight": "approved-adapter-preflight.json",
        "approved_adapter_preflight_hash": sha256_file(output_preflight_path),
        "adapter_security_review_hash": security_hash,
        "adapter_production_readiness_packet": rel(readiness_packet_path, output_root) if readiness_packet_path else "",
        "adapter_production_readiness_hash": readiness_hash,
        "official_session_authorization_packet": rel(session_packet_path, output_root) if session_packet_path else "",
        "official_session_authorization_hash": session_hash,
        "official_session_reference_hash": session_reference_hash,
        "forbidden_fields_absent_confirmed": True,
    }
    write_json(adapter_request_path, adapter_request)
    request_ok, request_errors, request_warnings = validate_filing_adapter_contract.validate_request(adapter_request, base_dir=output_root)

    status = {
        "case_id": case_id,
        "previous_status": "ready_for_authorized_filing",
        "status": "approved_for_adapter_execution",
        "legal_gate": "passed",
        "legal_gate_mode": legal_gate_mode,
        "package_validation": "passed",
        "official_channel_preflight": "passed",
        "approved_adapter_preflight": "passed",
        "production_adapter_readiness": "passed",
        "production_adapter_readiness_hash": readiness_hash,
        "official_session_authorization": "passed",
        "official_session_authorization_hash": session_hash,
        "official_session_reference_hash": session_reference_hash,
        "failed_gates": [],
        "decision": "approved_for_adapter_execution",
        "final_package_hash": final_hash,
        "reviewed_package_hash": reviewed_hash,
        "official_receipt_hash": "",
        "application_number": "",
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    if legal_gate_mode == "ai_self_filing_no_external_lawyer":
        status["ai_self_filing_gate"] = "passed"
        status["external_lawyer_involved"] = False
        if application_materials_hash:
            status["application_materials_hash"] = application_materials_hash
        if reference_delta_hash:
            status["reference_patent_delta_hash"] = reference_delta_hash
            status["reference_delta_boundary_preserved"] = application_materials.get("reference_delta_boundary_preserved") is True
    write_json(status_path, status)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
    report_path.write_text(
        render_report(
            case_id,
            legal_gate_mode,
            readiness_hash,
            session_hash,
            session_reference_hash,
            application_materials_hash,
            reference_delta_hash,
        ),
        encoding="utf-8",
    )

    write_json(
        hashes_path,
        artifact_manifest(output_root, case_id, [output_preflight_path, adapter_request_path, status_path, report_path, audit_plan_path, docket_plan_path]),
    )
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)

    ok = approved_ok and request_ok and status_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "approved_adapter_preflight": str(output_preflight_path),
            "filing_adapter_request": str(adapter_request_path),
            "filing_status": str(status_path),
            "adapter_boundary_report": str(report_path),
            "audit_log_entry_plan": str(audit_plan_path),
            "docket_entry_plan": str(docket_plan_path),
            "artifact_hashes": str(hashes_path),
        },
        "approved_errors": approved_errors,
        "approved_warnings": approved_warnings,
        "request_errors": request_errors,
        "request_warnings": request_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "status": "approved_for_adapter_execution",
        "legal_gate_mode": legal_gate_mode,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ready_for_authorized_filing_dir", type=Path)
    parser.add_argument("validated_package_dir", type=Path)
    parser.add_argument("approved_adapter_source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(
            args.ready_for_authorized_filing_dir,
            args.validated_package_dir,
            args.approved_adapter_source,
            args.output_dir,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
            "adapter_execution_performed": False,
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
