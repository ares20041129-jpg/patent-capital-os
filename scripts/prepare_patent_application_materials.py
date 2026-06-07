#!/usr/bin/env python3
"""Generate source-bound patent application materials from a validated package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import build_case_queue
import validate_abnormal_filing_risk_assessment
import validate_ai_self_filing_package_benchmark
import validate_artifact_hash_manifest
import validate_draft_evidence_provenance
import validate_filing_package_manifest
import validate_filing_status_transition
import validate_patent_application_materials


CNIPA_BASELINE_URLS = [
    "https://www.cnipa.gov.cn/",
    "https://cponline.cnipa.gov.cn/",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def copy_file(src: Path, dst: Path) -> None:
    if src.resolve() != dst.resolve():
        dst.write_bytes(src.read_bytes())


def extract_section(markdown: str, title: str) -> str:
    pattern = re.compile(rf"^## {re.escape(title)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(markdown)
    return markdown[match.start() : end].strip()


def collect_sections(markdown: str, titles: list[str]) -> str:
    sections = [extract_section(markdown, title) for title in titles]
    return "\n\n".join(section for section in sections if section)


def render_material(title: str, case_id: str, draft_hash: str, final_hash: str, body: str) -> str:
    return (
        f"# {title}\n\n"
        f"Case ID: {case_id}\n"
        f"Source draft hash: {draft_hash}\n"
        f"Final package hash: {final_hash}\n"
        "Route: AI self-filing, no external lawyer or patent agent in default path\n"
        "Boundary: generated material only; not legal advice, not official submission, not receipt evidence.\n\n"
        f"{body.strip()}\n"
    )


def build_request_metadata(packet: dict[str, Any]) -> dict[str, Any]:
    authorization = packet.get("applicant_authorization") if isinstance(packet.get("applicant_authorization"), dict) else {}
    eligibility = packet.get("self_filing_eligibility") if isinstance(packet.get("self_filing_eligibility"), dict) else {}
    inventors = packet.get("inventor_confirmation") if isinstance(packet.get("inventor_confirmation"), dict) else {}
    ownership = packet.get("ownership") if isinstance(packet.get("ownership"), dict) else {}
    secrecy = packet.get("secrecy_review") if isinstance(packet.get("secrecy_review"), dict) else {}
    channel = packet.get("filing_channel") if isinstance(packet.get("filing_channel"), dict) else {}
    fees = packet.get("fees") if isinstance(packet.get("fees"), dict) else {}
    legal_gate = get_path(packet, "ai_compliance_review.legal_gate_review") or {}

    return {
        "case_id": packet.get("case_id"),
        "jurisdiction": packet.get("jurisdiction"),
        "filing_type": packet.get("filing_type"),
        "applicant_name": authorization.get("applicant_name"),
        "applicant_type": eligibility.get("applicant_type"),
        "applicant_region": eligibility.get("applicant_region"),
        "inventors": inventors.get("inventors") or [],
        "inventor_contribution_confirmed": inventors.get("contribution_confirmed"),
        "ownership_basis": ownership.get("basis"),
        "ownership_dispute_absent": ownership.get("dispute_absent"),
        "priority_claims": [],
        "foreign_or_pct_planned": secrecy.get("foreign_or_pct_planned"),
        "secrecy_review_status": secrecy.get("status"),
        "china_secrecy_review_completed": secrecy.get("china_completed"),
        "official_system": channel.get("official_system"),
        "official_account_owner": channel.get("account_owner"),
        "official_account_registered": channel.get("official_account_registered"),
        "signature_authority": channel.get("signature_authority"),
        "automation_allowed": channel.get("automation_allowed"),
        "bypasses_access_controls": channel.get("bypasses_access_controls"),
        "fee_payer": fees.get("payer"),
        "fee_reduction": fees.get("fee_reduction"),
        "auto_pay_authorized": fees.get("auto_pay_authorized"),
        "payment_account_reference": fees.get("payment_account_reference"),
        "authorized_person": authorization.get("authorized_person"),
        "authority_basis": authorization.get("authority_basis"),
        "allowed_actions": authorization.get("allowed_actions") or [],
        "authorization_timestamp": authorization.get("timestamp"),
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "legal_advice_claimed": legal_gate.get("legal_advice_claimed"),
        "lawyer_or_agent_review_claimed": legal_gate.get("lawyer_or_agent_review_claimed"),
        "external_lawyer_involved": packet.get("external_lawyer_involved"),
    }


def build_xml_readiness(manifest: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    xml = manifest.get("xml_validation") if isinstance(manifest.get("xml_validation"), dict) else {}
    return {
        "case_id": packet.get("case_id"),
        "xml_required": True,
        "jurisdiction": packet.get("jurisdiction"),
        "filing_type": packet.get("filing_type"),
        "final_xml_hash": xml.get("final_xml_hash"),
        "standard_or_tool": xml.get("standard_or_tool"),
        "validation_result": xml.get("validation_result"),
        "validation_report_hash": xml.get("validation_report_hash"),
        "sequence_listing_standard": xml.get("sequence_listing_standard"),
        "official_channel_preflight_required": True,
        "official_upload_performed": False,
        "official_system_touched": False,
        "official_submission_performed": False,
    }


def build_generation_plan(packet: dict[str, Any], manifest: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
    source_hashes = {
        "source_draft_hash": packet.get("source_draft_hash"),
        "final_package_hash": packet.get("final_package_hash"),
        "claim_support_map_hash": provenance.get("claim_support_map_hash"),
        "source_material_manifest_hash": provenance.get("source_material_manifest_hash"),
    }
    if provenance.get("reference_patent_delta_hash"):
        source_hashes.update(
            {
                "reference_patent_delta_hash": provenance.get("reference_patent_delta_hash"),
                "reference_delta_rows_count": provenance.get("reference_delta_rows_count"),
                "reference_delta_claim_elements_count": provenance.get("reference_delta_claim_elements_count"),
            }
        )
    return {
        "case_id": packet.get("case_id"),
        "status": "application_materials_generation_plan_ready",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "source_hashes": source_hashes,
        "steps": [
            {
                "step": "claims_material",
                "status": "generated_and_source_bound",
                "source": "patent-application-draft.md Claims Draft section plus provenance rows",
            },
            {
                "step": "specification_material",
                "status": "generated_and_source_bound",
                "source": "technical field, background, problem, solution, effects, drawings, embodiments",
            },
            {
                "step": "abstract_material",
                "status": "generated_and_source_bound",
                "source": "patent-application-draft.md Abstract section",
            },
            {
                "step": "drawings_material",
                "status": "generated_and_source_bound",
                "source": "brief description of drawings and filing manifest drawings document",
            },
            {
                "step": "request_form_metadata",
                "status": "generated_from_authorization_packet",
                "source": "applicant authorization, inventor confirmation, ownership, secrecy, channel, and fee fields",
            },
            {
                "step": "xml_readiness",
                "status": "generated_from_package_manifest",
                "source": manifest.get("xml_validation", {}).get("standard_or_tool"),
            },
        ],
        "stop_conditions": [
            "official_channel_preflight_missing",
            "official_upload_not_performed",
            "official_receipt_missing",
            "application_number_missing",
        ],
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


def build_document_entry(doc_type: str, path: Path, root: Path, fmt: str = "md") -> dict[str, Any]:
    return {
        "type": doc_type,
        "path": rel(path, root),
        "format": fmt,
        "hash": sha256_file(path),
        "required": True,
        "validation_status": "generated_and_source_bound",
    }


def render_report(materials: dict[str, Any]) -> str:
    docs = materials.get("document_materials") if isinstance(materials.get("document_materials"), list) else []
    lines = [
        "# Patent Application Materials Report",
        "",
        f"Case ID: {materials.get('case_id')}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        f"Status: {materials.get('status')}",
        f"Decision: {materials.get('decision')}",
        "Official-channel preflight: required",
        "Official system touched: no",
        "Official submission performed: no",
        "",
        "## Generated Materials",
        "",
    ]
    for doc in docs:
        lines.append(f"- {doc.get('type')}: {doc.get('path')} ({doc.get('hash')})")
    lines.extend(
        [
            "",
            "## Legal And Evidence Gates",
            "",
            "- AI legal/compliance gate: preserved from validated AI self-filing package.",
            "- Claim-support provenance: bound to draft-evidence-provenance.json.",
            "- Abnormal filing risk: bound to same-case low-risk assessment.",
            "- Request form metadata: generated from applicant authorization, inventor, ownership, secrecy, channel, and fee fields.",
            "",
        ]
    )
    abnormal = materials.get("abnormal_filing_risk_assessment") if isinstance(materials.get("abnormal_filing_risk_assessment"), dict) else {}
    if abnormal.get("reference_patent_delta_hash"):
        lines.extend(
            [
                "## Reference Delta Boundary",
                "",
                f"- Reference-patent delta hash: {abnormal.get('reference_patent_delta_hash')}",
                f"- Reference-delta rows: {abnormal.get('reference_delta_rows_count')}",
                f"- Reference-delta claim elements: {abnormal.get('reference_delta_claim_elements_count')}",
                f"- Boundary preserved: {str(abnormal.get('reference_delta_boundary_preserved')).lower()}",
                "- Reference patents remain boundary and claim-strategy evidence only, not applicant claim support.",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "This materials package is not legal advice, not lawyer review, not patent-agent review, not an official submission, not a receipt, and not an application number.",
        ]
    )
    return "\n".join(lines) + "\n"


def prepare(package_dir: Path, draft_package_dir: Path, provenance_dir: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    package_root = package_dir.resolve()
    draft_root = draft_package_dir.resolve()
    provenance_root = provenance_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    package_ok, package_errors, package_warnings = validate_ai_self_filing_package_benchmark.validate(package_root)
    if not package_ok:
        return {
            "ok": False,
            "errors": [f"ai_self_filing_package: {item}" for item in package_errors],
            "warnings": package_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    packet_path = package_root / "ai-self-filing-authorization-packet.json"
    manifest_path = package_root / "filing-package-manifest.yaml"
    package_status_path = package_root / "filing-status.json"
    abnormal_path = package_root / "abnormal-filing-risk-assessment.json"
    draft_path = draft_root / "patent-application-draft.md"
    provenance_path = provenance_root / "draft-evidence-provenance.json"

    for path in [packet_path, manifest_path, package_status_path, abnormal_path, draft_path, provenance_path]:
        if not path.exists():
            return {
                "ok": False,
                "errors": [f"missing_required_input: {path}"],
                "official_system_touched": False,
                "official_submission_performed": False,
                "external_lawyer_involved": False,
            }, 1

    packet = load_json(packet_path)
    manifest = validate_filing_package_manifest.load_packet(manifest_path)
    package_status = load_json(package_status_path)
    abnormal = load_json(abnormal_path)
    provenance = load_json(provenance_path)

    provenance_ok, provenance_errors, provenance_warnings = validate_draft_evidence_provenance.validate(provenance)
    abnormal_ok, abnormal_errors, abnormal_warnings = validate_abnormal_filing_risk_assessment.validate(abnormal)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(package_status)
    if not provenance_ok or not abnormal_ok or not status_ok:
        return {
            "ok": False,
            "errors": (
                [f"draft_evidence_provenance: {item}" for item in provenance_errors]
                + [f"abnormal_filing_risk_assessment: {item}" for item in abnormal_errors]
                + [f"filing_status: {item}" for item in status_errors]
            ),
            "warnings": provenance_warnings + abnormal_warnings + status_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    case_id = str(packet.get("case_id") or "")
    draft_hash = sha256_file(draft_path)
    if draft_hash != packet.get("source_draft_hash") or draft_hash != provenance.get("patent_application_draft_hash"):
        return {
            "ok": False,
            "case_id": case_id,
            "errors": ["source_draft_hash_mismatch"],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1
    if provenance.get("case_id") != case_id or abnormal.get("case_id") != case_id:
        return {
            "ok": False,
            "case_id": case_id,
            "errors": ["case_id_mismatch_between_package_provenance_or_abnormal_risk"],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    draft_text = draft_path.read_text(encoding="utf-8")
    final_hash = str(packet.get("final_package_hash") or "")

    claims_path = output_root / "claims-material.md"
    specification_path = output_root / "specification-material.md"
    abstract_path = output_root / "abstract-material.md"
    drawings_path = output_root / "drawings-materials-plan.md"
    request_path = output_root / "request-form-metadata.json"
    xml_path = output_root / "xml-readiness-checklist.json"
    plan_path = output_root / "document-generation-plan.json"
    materials_path = output_root / "application-materials.json"
    status_path = output_root / "filing-status.json"
    report_path = output_root / "application-materials-report.md"
    hashes_path = output_root / "artifact-hashes.json"
    copied_provenance_path = output_root / "draft-evidence-provenance.json"
    copied_abnormal_path = output_root / "abnormal-filing-risk-assessment.json"

    claims_body = extract_section(draft_text, "Claims Draft") or "Claims section not found in source draft."
    specification_body = collect_sections(
        draft_text,
        [
            "Title",
            "Technical Field",
            "Background",
            "Technical Problem",
            "Technical Solution",
            "Beneficial Technical Effects",
            "Brief Description Of Drawings",
            "Detailed Embodiments",
        ],
    )
    abstract_body = extract_section(draft_text, "Abstract") or "Abstract section not found in source draft."
    drawings_body = extract_section(draft_text, "Brief Description Of Drawings") or "Drawing description section not found in source draft."

    claims_path.write_text(render_material("Claims Material", case_id, draft_hash, final_hash, claims_body), encoding="utf-8")
    specification_path.write_text(render_material("Specification Material", case_id, draft_hash, final_hash, specification_body), encoding="utf-8")
    abstract_path.write_text(render_material("Abstract Material", case_id, draft_hash, final_hash, abstract_body), encoding="utf-8")
    drawings_path.write_text(render_material("Drawings Materials Plan", case_id, draft_hash, final_hash, drawings_body), encoding="utf-8")
    write_json(request_path, build_request_metadata(packet))
    write_json(xml_path, build_xml_readiness(manifest, packet))
    write_json(plan_path, build_generation_plan(packet, manifest, provenance))
    copy_file(provenance_path, copied_provenance_path)
    copy_file(abnormal_path, copied_abnormal_path)

    official_docs = manifest.get("documents") if isinstance(manifest.get("documents"), list) else []
    document_materials = [
        build_document_entry("claims", claims_path, output_root),
        build_document_entry("specification", specification_path, output_root),
        build_document_entry("abstract", abstract_path, output_root),
        build_document_entry("drawings", drawings_path, output_root),
        build_document_entry("request_form_metadata", request_path, output_root, "json"),
        build_document_entry("xml_readiness_checklist", xml_path, output_root, "json"),
    ]
    evidence_provenance_summary = {
        "case_id": provenance.get("case_id"),
        "path": rel(copied_provenance_path, output_root),
        "artifact_hash": sha256_file(copied_provenance_path),
        "source_material_manifest_hash": provenance.get("source_material_manifest_hash"),
        "patent_application_draft_hash": provenance.get("patent_application_draft_hash"),
        "claim_support_map_hash": provenance.get("claim_support_map_hash"),
        "own_support_hashes": provenance.get("own_support_hashes") or [],
        "prohibited_reference_hashes": provenance.get("prohibited_reference_hashes") or [],
        "claim_support_rows_count": len(provenance.get("claim_support_rows") or []),
        "no_reference_or_prior_art_used_as_claim_support": True,
    }
    if provenance.get("reference_patent_delta_hash"):
        evidence_provenance_summary.update(
            {
                "reference_patent_delta_hash": provenance.get("reference_patent_delta_hash"),
                "reference_delta_rows_count": provenance.get("reference_delta_rows_count"),
                "reference_delta_claim_elements_count": provenance.get("reference_delta_claim_elements_count"),
            }
        )

    abnormal_summary = {
        "case_id": abnormal.get("case_id"),
        "path": rel(copied_abnormal_path, output_root),
        "artifact_hash": sha256_file(copied_abnormal_path),
        "gate": abnormal.get("gate"),
        "risk_level": abnormal.get("risk_level"),
        "status": abnormal.get("status"),
    }
    if abnormal.get("reference_patent_delta_hash"):
        checks = abnormal.get("checks") if isinstance(abnormal.get("checks"), list) else []
        boundary = next(
            (
                check
                for check in checks
                if isinstance(check, dict) and check.get("check_id") == "reference_delta_boundary_preserved"
            ),
            {},
        )
        abnormal_summary.update(
            {
                "reference_patent_delta_hash": abnormal.get("reference_patent_delta_hash"),
                "reference_delta_rows_count": abnormal.get("reference_delta_rows_count"),
                "reference_delta_claim_elements_count": abnormal.get("reference_delta_claim_elements_count"),
                "reference_delta_boundary_preserved": boundary.get("result") == "pass",
            }
        )

    generated_status = {
        "case_id": case_id,
        "status": "package_valid_official_preflight_pending",
        "legal_gate": "passed",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "ai_self_filing_gate": "passed",
        "package_validation": "passed",
        "application_materials_generation": "passed",
        "official_channel_preflight": "pending",
        "failed_gates": [
            "official_channel_preflight_pending",
            "receipt_capture_pending",
        ],
        "decision": "materials_generated_official_preflight_required",
        "final_package_hash": final_hash,
        "reviewed_package_hash": final_hash,
        "official_receipt_hash": "",
        "application_number": "",
        "official_submission_performed": False,
        "official_system_touched": False,
        "external_lawyer_involved": False,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    write_json(status_path, generated_status)

    materials = {
        "case_id": case_id,
        "status": "application_materials_generated_official_preflight_pending",
        "decision": "materials_generated_official_preflight_required",
        "jurisdiction": packet.get("jurisdiction"),
        "filing_type": packet.get("filing_type"),
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "final_package_hash": final_hash,
        "filing_allowed": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
        "source_package": {
            "package_dir": rel(package_root, output_root),
            "package_status": manifest.get("package_status"),
            "authorization_packet_hash": sha256_file(packet_path),
            "filing_package_manifest_hash": sha256_file(manifest_path),
            "filing_status_hash": sha256_file(package_status_path),
            "source_draft_hash": draft_hash,
            "final_package_hash": final_hash,
        },
        "evidence_provenance": evidence_provenance_summary,
        "abnormal_filing_risk_assessment": abnormal_summary,
        "request_form_metadata": {
            "path": rel(request_path, output_root),
            "hash": sha256_file(request_path),
            **build_request_metadata(packet),
        },
        "document_generation_plan": {
            "path": rel(plan_path, output_root),
            "hash": sha256_file(plan_path),
        },
        "document_materials": document_materials,
        "official_material_inventory": official_docs,
        "xml_readiness": {
            "path": rel(xml_path, output_root),
            "hash": sha256_file(xml_path),
            **build_xml_readiness(manifest, packet),
        },
        "filing_status": {
            "path": rel(status_path, output_root),
            "hash": sha256_file(status_path),
        },
        "cnipa_material_baseline": {
            "basis": "CN invention application materials require request metadata plus application text and package-format readiness before official submission.",
            "generated_for": [
                "request form metadata",
                "claims",
                "specification",
                "abstract",
                "drawings",
                "xml package readiness",
            ],
            "official_reference_urls": CNIPA_BASELINE_URLS,
        },
        "safeguards": {
            "no_legal_advice_claimed": True,
            "no_lawyer_or_agent_review_claimed": True,
            "no_official_submission_claimed": True,
            "no_receipt_claimed": True,
            "no_application_number_claimed": True,
            "external_lawyer_absent": True,
            "official_system_touched": False,
            "official_submission_performed": False,
        },
    }
    write_json(materials_path, materials)
    materials_ok, materials_errors, materials_warnings = validate_patent_application_materials.validate(materials, output_root)

    report_path.write_text(render_report(materials), encoding="utf-8")
    files = [
        claims_path,
        specification_path,
        abstract_path,
        drawings_path,
        request_path,
        xml_path,
        plan_path,
        copied_provenance_path,
        copied_abnormal_path,
        materials_path,
        status_path,
        report_path,
    ]
    write_json(hashes_path, artifact_manifest(output_root, case_id, files))
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)

    ok = materials_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "application_materials": str(materials_path),
            "request_form_metadata": str(request_path),
            "document_generation_plan": str(plan_path),
            "xml_readiness_checklist": str(xml_path),
            "filing_status": str(status_path),
            "application_materials_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "package_warnings": package_warnings,
        "provenance_warnings": provenance_warnings,
        "abnormal_warnings": abnormal_warnings,
        "status_warnings": status_warnings,
        "materials_errors": materials_errors,
        "materials_warnings": materials_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--draft-package-dir", required=True, type=Path)
    parser.add_argument("--provenance-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(
            package_dir=args.package_dir,
            draft_package_dir=args.draft_package_dir,
            provenance_dir=args.provenance_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
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
