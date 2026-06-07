#!/usr/bin/env python3
"""Prepare official-channel preflight artifacts up to ready_for_authorized_filing."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_ai_self_filing_authorization
import validate_filing_package_manifest
import validate_filing_status_transition
import validate_official_channel_preflight
import validate_patent_application_materials
import validate_receipt_capture
import validate_submission_packet


REQUIRED_SOURCE_PATHS = [
    "case_id",
    "checked_by",
    "account.role",
    "account.authorization_evidence",
    "signature.authority_holder",
    "signature.authority_evidence",
    "signature.human_only",
    "automation.automation_allowed",
    "automation.adapter_name",
    "automation.adapter_version",
    "automation.bypasses_access_controls",
    "fees.payment_method_reference",
    "receipt_capture.destination",
    "receipt_capture.responsible_owner",
    "receipt_capture.planned_docket_entry_id",
    "receipt_capture.next_deadlines",
    "decision.status",
    "decision.reason",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".json":
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
    return path.resolve().relative_to(root.resolve()).as_posix()


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


def resolve_reference(base_file: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else (base_file.resolve().parent / path).resolve()


def validate_application_materials_reference(
    source_path: Path,
    source: dict[str, Any],
    case_id: str,
    final_package_hash: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ref = source.get("application_materials") if isinstance(source.get("application_materials"), dict) else {}
    raw_path = str(ref.get("path") or "")
    expected_hash = str(ref.get("hash") or "")
    if not raw_path:
        return {}, ["application_materials_path_missing"], []
    if not expected_hash.startswith("sha256:"):
        errors.append("application_materials_hash_missing_or_invalid")
    materials_path = resolve_reference(source_path, raw_path)
    if not materials_path.exists():
        return {}, [*errors, f"application_materials_file_not_found: {materials_path}"], warnings
    actual_hash = sha256_file(materials_path)
    if expected_hash and expected_hash != actual_hash:
        errors.append("application_materials_hash_mismatch")
    materials = load_json(materials_path)
    ok, material_errors, material_warnings = validate_patent_application_materials.validate(materials, materials_path.parent)
    if not ok:
        errors.extend([f"application_materials: {item}" for item in material_errors])
    warnings.extend([f"application_materials: {item}" for item in material_warnings])
    if materials.get("case_id") != case_id:
        errors.append("application_materials_case_id_mismatch")
    if materials.get("final_package_hash") != final_package_hash:
        errors.append("application_materials_final_package_hash_mismatch")
    if materials.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("application_materials_legal_gate_mode_must_be_ai_self_filing")
    if materials.get("external_lawyer_involved") is not False:
        errors.append("application_materials_external_lawyer_involved_must_be_false")
    if materials.get("official_system_touched") is not False:
        errors.append("application_materials_must_not_touch_official_system")
    if materials.get("official_submission_performed") is not False:
        errors.append("application_materials_must_not_submit")
    summary = {
        "path": raw_path,
        "hash": actual_hash,
        "status": materials.get("status"),
        "decision": materials.get("decision"),
    }
    evidence = materials.get("evidence_provenance") if isinstance(materials.get("evidence_provenance"), dict) else {}
    abnormal = materials.get("abnormal_filing_risk_assessment") if isinstance(materials.get("abnormal_filing_risk_assessment"), dict) else {}
    reference_hash = abnormal.get("reference_patent_delta_hash") or evidence.get("reference_patent_delta_hash")
    if reference_hash:
        summary.update(
            {
                "reference_patent_delta_hash": reference_hash,
                "reference_delta_rows_count": abnormal.get("reference_delta_rows_count") or evidence.get("reference_delta_rows_count"),
                "reference_delta_claim_elements_count": (
                    abnormal.get("reference_delta_claim_elements_count")
                    or evidence.get("reference_delta_claim_elements_count")
                ),
                "reference_delta_boundary_preserved": abnormal.get("reference_delta_boundary_preserved") is True,
            }
        )
    return summary, errors, warnings


def validate_source(data: dict[str, Any], expected_case_id: str) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for path in REQUIRED_SOURCE_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")
    if data.get("case_id") != expected_case_id:
        errors.append("case_id_mismatch_between_preflight_source_and_package")
    if get_path(data, "automation.bypasses_access_controls") is not False:
        errors.append("automation_must_not_bypass_access_controls")
    if get_path(data, "automation.automation_allowed") is not True:
        errors.append("automation_not_authorized")
    if get_path(data, "signature.human_only") is True:
        errors.append("human_only_signature_step_requires_handoff")
    if get_path(data, "decision.status") != "ready_for_authorized_filing":
        errors.append("decision_status_must_be_ready_for_authorized_filing")
    return len(errors) == 0, errors, warnings


def render_official_preflight_yaml(preflight: dict[str, Any]) -> str:
    lines = [
        f"case_id: {q(preflight.get('case_id'))}",
        f"jurisdiction: {q(preflight.get('jurisdiction'))}",
        f"official_system: {q(preflight.get('official_system'))}",
        f"checked_at: {q(preflight.get('checked_at'))}",
        f"checked_by: {q(preflight.get('checked_by'))}",
        "account:",
        f"  owner: {q(get_path(preflight, 'account.owner'))}",
        f"  role: {q(get_path(preflight, 'account.role'))}",
        f"  authorization_evidence: {q(get_path(preflight, 'account.authorization_evidence'))}",
        "signature:",
        f"  authority_holder: {q(get_path(preflight, 'signature.authority_holder'))}",
        f"  authority_evidence: {q(get_path(preflight, 'signature.authority_evidence'))}",
        f"  human_only: {str(get_path(preflight, 'signature.human_only')).lower()}",
        "automation:",
        f"  automation_allowed: {str(get_path(preflight, 'automation.automation_allowed')).lower()}",
        f"  adapter_name: {q(get_path(preflight, 'automation.adapter_name'))}",
        f"  adapter_version: {q(get_path(preflight, 'automation.adapter_version'))}",
        f"  bypasses_access_controls: {str(get_path(preflight, 'automation.bypasses_access_controls')).lower()}",
        "package:",
        f"  final_package_hash: {q(get_path(preflight, 'package.final_package_hash'))}",
        f"  reviewed_package_hash: {q(get_path(preflight, 'package.reviewed_package_hash'))}",
        f"  xml_validation_result: {q(get_path(preflight, 'package.xml_validation_result'))}",
        f"  attachment_list_hash: {q(get_path(preflight, 'package.attachment_list_hash'))}",
    ]
    if isinstance(preflight.get("application_materials"), dict):
        lines.extend(
            [
                "application_materials:",
                f"  path: {q(get_path(preflight, 'application_materials.path'))}",
                f"  hash: {q(get_path(preflight, 'application_materials.hash'))}",
                f"  status: {q(get_path(preflight, 'application_materials.status'))}",
                f"  decision: {q(get_path(preflight, 'application_materials.decision'))}",
            ]
        )
        if get_path(preflight, "application_materials.reference_patent_delta_hash"):
            lines.extend(
                [
                    f"  reference_patent_delta_hash: {q(get_path(preflight, 'application_materials.reference_patent_delta_hash'))}",
                    f"  reference_delta_rows_count: {q(get_path(preflight, 'application_materials.reference_delta_rows_count'))}",
                    f"  reference_delta_claim_elements_count: {q(get_path(preflight, 'application_materials.reference_delta_claim_elements_count'))}",
                    f"  reference_delta_boundary_preserved: {str(get_path(preflight, 'application_materials.reference_delta_boundary_preserved')).lower()}",
                ]
            )
    lines.extend(
        [
            "fees:",
            f"  payer: {q(get_path(preflight, 'fees.payer'))}",
            f"  auto_pay_authorized: {str(get_path(preflight, 'fees.auto_pay_authorized')).lower()}",
            f"  payment_method_reference: {q(get_path(preflight, 'fees.payment_method_reference'))}",
            "receipt_capture:",
            f"  destination: {q(get_path(preflight, 'receipt_capture.destination'))}",
            f"  responsible_owner: {q(get_path(preflight, 'receipt_capture.responsible_owner'))}",
            "decision:",
            f"  status: {q(get_path(preflight, 'decision.status'))}",
            f"  reason: {q(get_path(preflight, 'decision.reason'))}",
            "",
        ]
    )
    return "\n".join(lines)


def render_receipt_plan_yaml(plan: dict[str, Any]) -> str:
    lines = [
        f"case_id: {q(plan.get('case_id'))}",
        f"filing_action_id: {q(plan.get('filing_action_id'))}",
        f"status: {q(plan.get('status'))}",
        'submitted_at: ""',
        f"official_system: {q(plan.get('official_system'))}",
        "official_receipt:",
        '  receipt_id: ""',
        '  receipt_file: ""',
        '  receipt_hash: ""',
        "application:",
        '  application_number: ""',
        '  filing_date: ""',
        '  official_file_list_hash: ""',
        "fees:",
        f"  payment_status: {q(get_path(plan, 'fees.payment_status'))}",
        '  payment_receipt_file: ""',
        '  payment_receipt_hash: ""',
        "docket:",
        f"  docket_entry_id: {q(get_path(plan, 'docket.docket_entry_id'))}",
        "  next_deadlines:",
    ]
    deadlines = get_path(plan, "docket.next_deadlines")
    if isinstance(deadlines, list):
        for item in deadlines:
            if isinstance(item, dict):
                lines.extend(
                    [
                        f"    - name: {q(item.get('name'))}",
                        f"      due_date: {q(item.get('due_date'))}",
                    ]
                )
    lines.extend([f"evidence_notes: {q(plan.get('evidence_notes'))}", ""])
    return "\n".join(lines)


def render_report(
    case_id: str,
    final_package_hash: str,
    legal_gate_mode: str,
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
            "# Official Channel Preflight Readiness Report",
            "",
            f"Case ID: {case_id}",
            route_line,
            "Status: ready_for_authorized_filing",
            f"Legal gate mode: {legal_gate_mode}",
            f"Final package hash: {final_package_hash}",
            f"Application materials hash: {application_materials_hash or 'not required for this route'}",
            f"Reference-patent delta hash: {reference_delta_hash or 'not present'}",
            "Official submission performed: no",
            "Official system touched: no",
            "",
            "## Decision",
            "",
            "Ready for authorized filing handoff or approved adapter preflight. No filing, payment, signature, upload, or submission has occurred.",
            "",
            "## Reference Delta Boundary",
            "",
            "When present, reference-patent delta evidence remains boundary and claim-strategy evidence only. It is not applicant claim support, legal advice, filing authorization, official submission evidence, receipt evidence, or application-number evidence.",
            "",
            "## Boundary",
            "",
            "The case must not advance to `submitted_pending_receipt` until a lawful authorized official action actually occurs. It must not claim `official_receipt_received` or `accepted_or_application_number_received` without receipt and application-number evidence.",
            "",
        ]
    )


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


def prepare(validated_package_dir: Path, preflight_source_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    package_root = validated_package_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    manifest_path = package_root / "filing-package-manifest.yaml"
    status_path = package_root / "filing-status.json"
    if not manifest_path.exists() or not status_path.exists():
        raise RuntimeError("validated_package_dir_missing_manifest_or_status")
    packet_path, legal_gate_mode = find_authorization_packet(package_root)

    manifest = validate_filing_package_manifest.load_packet(manifest_path)
    packet = load_json(packet_path)
    prior_status = load_json(status_path)
    manifest_ok, manifest_errors, manifest_warnings = validate_filing_package_manifest.validate(manifest, base_dir=package_root)
    if legal_gate_mode == "ai_self_filing_no_external_lawyer":
        packet_ok, packet_errors, packet_warnings = validate_ai_self_filing_authorization.validate(packet, base_dir=package_root)
    else:
        packet_ok, packet_errors, packet_warnings = validate_submission_packet.validate(packet, base_dir=package_root)
    prior_status_ok, prior_status_errors, prior_status_warnings = validate_filing_status_transition.validate(prior_status)
    case_id = str(manifest.get("case_id") or packet.get("case_id") or "")
    source = load_json(preflight_source_path)
    source_ok, source_errors, source_warnings = validate_source(source, case_id)
    final_hash = str(manifest.get("final_package_hash") or "")
    application_materials: dict[str, Any] = {}
    application_materials_errors: list[str] = []
    application_materials_warnings: list[str] = []
    if legal_gate_mode == "ai_self_filing_no_external_lawyer" and manifest_ok:
        application_materials, application_materials_errors, application_materials_warnings = validate_application_materials_reference(
            preflight_source_path,
            source,
            case_id,
            final_hash,
        )
    if not (manifest_ok and packet_ok and prior_status_ok and source_ok):
        return {
            "ok": False,
            "case_id": case_id,
            "manifest_errors": manifest_errors,
            "packet_errors": packet_errors,
            "prior_status_errors": prior_status_errors,
            "source_errors": source_errors,
            "application_materials_errors": application_materials_errors,
            "manifest_warnings": manifest_warnings,
            "packet_warnings": packet_warnings,
            "prior_status_warnings": prior_status_warnings,
            "source_warnings": source_warnings,
            "application_materials_warnings": application_materials_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
        }, 1
    if application_materials_errors:
        return {
            "ok": False,
            "case_id": case_id,
            "application_materials_errors": application_materials_errors,
            "application_materials_warnings": application_materials_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
        }, 1

    documents = manifest.get("documents") if isinstance(manifest.get("documents"), list) else []
    attachment_payload = json.dumps(documents, ensure_ascii=False, sort_keys=True)
    checked_at = build_case_queue.utc_plus_8_now()
    official_system = str(get_path(packet, "filing_channel.official_system") or "CNIPA patent business processing system")
    preflight = {
        "case_id": case_id,
        "jurisdiction": manifest.get("jurisdiction"),
        "official_system": official_system,
        "checked_at": checked_at,
        "checked_by": source.get("checked_by"),
        "account": {
            "owner": get_path(packet, "filing_channel.account_owner"),
            "role": get_path(source, "account.role"),
            "authorization_evidence": get_path(source, "account.authorization_evidence"),
        },
        "signature": source.get("signature", {}),
        "automation": source.get("automation", {}),
        "package": {
            "final_package_hash": final_hash,
            "reviewed_package_hash": manifest.get("reviewed_package_hash"),
            "xml_validation_result": get_path(manifest, "xml_validation.validation_result"),
            "attachment_list_hash": sha256_text(attachment_payload),
        },
        "fees": {
            "payer": get_path(packet, "fees.payer"),
            "auto_pay_authorized": get_path(packet, "fees.auto_pay_authorized"),
            "payment_method_reference": get_path(source, "fees.payment_method_reference"),
        },
        "receipt_capture": {
            "destination": get_path(source, "receipt_capture.destination"),
            "responsible_owner": get_path(source, "receipt_capture.responsible_owner"),
        },
        "decision": source.get("decision", {}),
    }
    if legal_gate_mode == "ai_self_filing_no_external_lawyer":
        preflight["legal_gate_mode"] = legal_gate_mode
        preflight["external_lawyer_involved"] = False
        preflight["application_materials"] = application_materials

    preflight_path = output_root / "official-channel-preflight.yaml"
    receipt_plan_path = output_root / "receipt-capture-plan.yaml"
    ready_status_path = output_root / "filing-status.json"
    report_path = output_root / "readiness-report.md"
    hashes_path = output_root / "artifact-hashes.json"

    preflight_path.write_text(render_official_preflight_yaml(preflight), encoding="utf-8")
    preflight_ok, preflight_errors, preflight_warnings = validate_official_channel_preflight.validate(preflight)

    receipt_plan = {
        "case_id": case_id,
        "filing_action_id": "planned-action-" + case_id,
        "status": "planned",
        "official_system": official_system,
        "fees": {"payment_status": "pending"},
        "docket": {
            "docket_entry_id": get_path(source, "receipt_capture.planned_docket_entry_id"),
            "next_deadlines": get_path(source, "receipt_capture.next_deadlines"),
        },
        "evidence_notes": "Plan only. No official submission, payment, signature, or receipt exists.",
    }
    receipt_plan_path.write_text(render_receipt_plan_yaml(receipt_plan), encoding="utf-8")
    receipt_ok, receipt_errors, receipt_warnings = validate_receipt_capture.validate(receipt_plan, allow_plan_only=True, base_dir=output_root)

    ready_status = {
        "case_id": case_id,
        "previous_status": "package_valid_official_preflight_pending",
        "status": "ready_for_authorized_filing",
        "legal_gate": "passed",
        "legal_gate_mode": legal_gate_mode,
        "package_validation": "passed",
        "official_channel_preflight": "passed",
        "receipt_capture_plan": "planned",
        "failed_gates": [],
        "decision": "ready_for_authorized_filing",
        "final_package_hash": final_hash,
        "reviewed_package_hash": manifest.get("reviewed_package_hash"),
        "official_receipt_hash": "",
        "application_number": "",
        "official_system_touched": False,
        "official_submission_performed": False,
        "updated_at": checked_at,
    }
    if legal_gate_mode == "ai_self_filing_no_external_lawyer":
        ready_status["ai_self_filing_gate"] = "passed"
        ready_status["application_materials_generation"] = "passed"
        ready_status["application_materials_hash"] = application_materials.get("hash")
        ready_status["external_lawyer_involved"] = False
        if application_materials.get("reference_patent_delta_hash"):
            ready_status["reference_patent_delta_hash"] = application_materials.get("reference_patent_delta_hash")
            ready_status["reference_delta_boundary_preserved"] = application_materials.get("reference_delta_boundary_preserved")
    write_json(ready_status_path, ready_status)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(ready_status)

    report_path.write_text(
        render_report(
            case_id,
            final_hash,
            legal_gate_mode,
            str(application_materials.get("hash") or ""),
            str(application_materials.get("reference_patent_delta_hash") or ""),
        ),
        encoding="utf-8",
    )
    write_json(hashes_path, artifact_manifest(output_root, case_id, [preflight_path, receipt_plan_path, ready_status_path, report_path]))
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)

    ok = preflight_ok and receipt_ok and status_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "official_channel_preflight": str(preflight_path),
            "receipt_capture_plan": str(receipt_plan_path),
            "filing_status": str(ready_status_path),
            "readiness_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "preflight_errors": preflight_errors,
        "preflight_warnings": preflight_warnings,
        "receipt_errors": receipt_errors,
        "receipt_warnings": receipt_warnings,
        "application_materials_warnings": application_materials_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "status": "ready_for_authorized_filing",
        "legal_gate_mode": legal_gate_mode,
        "official_system_touched": False,
        "official_submission_performed": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("validated_package_dir", type=Path)
    parser.add_argument("official_preflight_source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.validated_package_dir, args.official_preflight_source, args.output_dir)
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
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
