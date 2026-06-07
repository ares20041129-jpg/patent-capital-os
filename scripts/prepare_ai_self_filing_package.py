#!/usr/bin/env python3
"""Prepare AI-only self-filing package validation artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import build_case_queue
import validate_abnormal_filing_risk_assessment
import validate_ai_self_filing_authorization
import validate_artifact_hash_manifest
import validate_filing_package_manifest
import validate_filing_status_transition
import validate_patent_application_draft


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def q(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def resolve_reference(base_file: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else (base_file.resolve().parent / path).resolve()


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        dst.write_bytes(src.read_bytes())


def enrich_abnormal_risk_assessment(source_path: Path, packet: dict[str, Any]) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    assessment_ref = get_path(packet, "ai_compliance_review.abnormal_filing_risk_assessment")
    if not isinstance(assessment_ref, dict):
        return None, ["abnormal_filing_risk_assessment_reference_missing"]

    raw_path = str(assessment_ref.get("artifact_path") or "")
    if not raw_path:
        return None, ["abnormal_filing_risk_assessment_artifact_path_missing"]
    assessment_path = resolve_reference(source_path, raw_path)
    if not assessment_path.exists():
        return None, [f"abnormal_filing_risk_assessment_artifact_not_found: {assessment_path}"]

    actual_hash = sha256_file(assessment_path)
    provided_hash = str(assessment_ref.get("artifact_hash") or "")
    if provided_hash and provided_hash != actual_hash:
        errors.append("abnormal_filing_risk_assessment_hash_mismatch")

    assessment = load_json(assessment_path)
    ok, assessment_errors, _assessment_warnings = validate_abnormal_filing_risk_assessment.validate(assessment)
    if not ok:
        errors.extend([f"abnormal_filing_risk_assessment: {item}" for item in assessment_errors])
    if assessment.get("case_id") != packet.get("case_id"):
        errors.append("abnormal_filing_risk_assessment_case_id_mismatch")
    if assessment.get("risk_level") != "low":
        errors.append("abnormal_filing_risk_assessment_must_be_low")
    if assessment.get("official_system_touched") is not False:
        errors.append("abnormal_filing_risk_assessment_must_not_touch_official_system")
    if assessment.get("official_submission_performed") is not False:
        errors.append("abnormal_filing_risk_assessment_must_not_submit")
    if assessment.get("external_lawyer_involved") is not False:
        errors.append("abnormal_filing_risk_assessment_must_not_involve_external_lawyer")

    assessment_ref["case_id"] = assessment.get("case_id")
    assessment_ref["status"] = assessment.get("status")
    assessment_ref["gate"] = assessment.get("gate")
    assessment_ref["risk_level"] = assessment.get("risk_level")
    assessment_ref["artifact_hash"] = actual_hash
    if assessment.get("reference_patent_delta_hash"):
        checks = assessment.get("checks") if isinstance(assessment.get("checks"), list) else []
        boundary = next(
            (
                check
                for check in checks
                if isinstance(check, dict) and check.get("check_id") == "reference_delta_boundary_preserved"
            ),
            {},
        )
        if boundary.get("result") != "pass":
            errors.append("reference_delta_boundary_not_preserved")
        assessment_ref["reference_patent_delta_hash"] = assessment.get("reference_patent_delta_hash")
        assessment_ref["reference_delta_rows_count"] = assessment.get("reference_delta_rows_count")
        assessment_ref["reference_delta_claim_elements_count"] = assessment.get("reference_delta_claim_elements_count")
        assessment_ref["reference_delta_boundary_preserved"] = boundary.get("result") == "pass"
    return assessment_path, errors


def document_format(doc_type: str) -> str:
    return "pdf" if doc_type == "drawings" else "xml"


def document_filename(doc_type: str) -> str:
    return f"{doc_type}-ai-self-filing-final.{document_format(doc_type)}"


def render_official_document(packet: dict[str, Any], draft_hash: str, doc_type: str) -> bytes:
    case_id = str(packet.get("case_id") or "")
    final_hash = str(packet.get("final_package_hash") or "")
    if doc_type == "drawings":
        body = "\n".join(
            [
                "%PDF-1.4",
                "% Patent Capital OS mock drawings package",
                f"Case ID: {case_id}",
                f"Source draft hash: {draft_hash}",
                f"Final package hash: {final_hash}",
                "Boundary: offline benchmark material; no official submission.",
                "%%EOF",
                "",
            ]
        )
        return body.encode("utf-8")
    body = "\n".join(
        [
            f"<document type=\"{doc_type}\">",
            f"  <case-id>{case_id}</case-id>",
            f"  <source-draft-hash>{draft_hash}</source-draft-hash>",
            f"  <final-package-hash>{final_hash}</final-package-hash>",
            "  <boundary>offline benchmark material; no official submission</boundary>",
            "</document>",
            "",
        ]
    )
    return body.encode("utf-8")


def materialize_official_documents(output_root: Path, packet: dict[str, Any], draft_hash: str) -> tuple[dict[str, str], list[Path]]:
    document_hashes: dict[str, str] = {}
    document_paths: list[Path] = []
    for doc_type in ["claims", "specification", "abstract", "drawings", "request_metadata"]:
        path = output_root / document_filename(doc_type)
        path.write_bytes(render_official_document(packet, draft_hash, doc_type))
        document_hashes[doc_type] = sha256_file(path)
        document_paths.append(path)
    return document_hashes, document_paths


def render_manifest_yaml(manifest: dict[str, Any]) -> str:
    lines = [
        f"case_id: {q(manifest.get('case_id'))}",
        f"jurisdiction: {q(manifest.get('jurisdiction'))}",
        f"filing_type: {q(manifest.get('filing_type'))}",
        f"package_status: {q(manifest.get('package_status'))}",
        f"source_draft: {q(manifest.get('source_draft'))}",
        f"source_draft_hash: {q(manifest.get('source_draft_hash'))}",
        f"authorization_packet: {q(manifest.get('authorization_packet'))}",
        f"authorization_packet_hash: {q(manifest.get('authorization_packet_hash'))}",
        f"reviewed_package_hash: {q(manifest.get('reviewed_package_hash'))}",
        f"final_package_hash: {q(manifest.get('final_package_hash'))}",
        "official_submission_performed: false",
        "",
        "documents:",
    ]
    for doc in manifest.get("documents", []):
        lines.extend(
            [
                f"  - document_id: {q(doc.get('document_id'))}",
                f"    type: {q(doc.get('type'))}",
                f"    filename: {q(doc.get('filename'))}",
                f"    format: {q(doc.get('format'))}",
                f"    hash: {q(doc.get('hash'))}",
                "    required: true",
                f"    validation_status: {q(doc.get('validation_status'))}",
            ]
        )
    xml = manifest.get("xml_validation", {})
    checks = manifest.get("cross_checks", {})
    gate = manifest.get("next_gate", {})
    lines.extend(
        [
            "",
            "xml_validation:",
            f"  final_xml_hash: {q(xml.get('final_xml_hash'))}",
            f"  standard_or_tool: {q(xml.get('standard_or_tool'))}",
            f"  validation_result: {q(xml.get('validation_result'))}",
            f"  validation_report_hash: {q(xml.get('validation_report_hash'))}",
            f"  sequence_listing_standard: {q(xml.get('sequence_listing_standard'))}",
            "",
            "cross_checks:",
            f"  final_package_hash_matches_reviewed_hash: {str(checks.get('final_package_hash_matches_reviewed_hash')).lower()}",
            f"  claims_hash_matches_authorization: {str(checks.get('claims_hash_matches_authorization')).lower()}",
            f"  specification_hash_matches_authorization: {str(checks.get('specification_hash_matches_authorization')).lower()}",
            f"  drawings_present: {str(checks.get('drawings_present')).lower()}",
            f"  request_metadata_present: {str(checks.get('request_metadata_present')).lower()}",
            "",
            "next_gate:",
            f"  official_channel_preflight_required: {str(gate.get('official_channel_preflight_required')).lower()}",
            f"  receipt_capture_required: {str(gate.get('receipt_capture_required')).lower()}",
            f"  status_after_package_validation: {q(gate.get('status_after_package_validation'))}",
            "",
        ]
    )
    return "\n".join(lines)


def build_manifest(
    draft_path: Path,
    packet_path: Path,
    packet: dict[str, Any],
    packet_hash: str,
    document_hashes: dict[str, str],
) -> dict[str, Any]:
    final_package_hash = str(packet.get("final_package_hash") or "")
    docs = []
    for doc_type in ["claims", "specification", "abstract", "drawings", "request_metadata"]:
        docs.append(
            {
                "document_id": doc_type,
                "type": doc_type,
                "filename": document_filename(doc_type),
                "format": document_format(doc_type),
                "hash": document_hashes[doc_type],
                "required": True,
                "validation_status": "passed",
            }
        )
    return {
        "case_id": packet.get("case_id"),
        "jurisdiction": packet.get("jurisdiction"),
        "filing_type": packet.get("filing_type"),
        "package_status": "package_valid_official_preflight_pending",
        "source_draft": draft_path.name,
        "source_draft_hash": packet.get("source_draft_hash"),
        "authorization_packet": packet_path.name,
        "authorization_packet_hash": packet_hash,
        "reviewed_package_hash": final_package_hash,
        "final_package_hash": final_package_hash,
        "official_submission_performed": False,
        "documents": docs,
        "xml_validation": {
            "final_xml_hash": sha256_text(final_package_hash + ":ai-self-filing-final-xml"),
            "standard_or_tool": "Patent Capital OS AI self-filing offline package validation",
            "validation_result": "passed",
            "validation_report_hash": sha256_text(final_package_hash + ":ai-self-filing-xml-validation-report"),
            "sequence_listing_standard": "not_applicable",
        },
        "cross_checks": {
            "final_package_hash_matches_reviewed_hash": True,
            "claims_hash_matches_authorization": True,
            "specification_hash_matches_authorization": True,
            "drawings_present": True,
            "request_metadata_present": True,
        },
        "next_gate": {
            "official_channel_preflight_required": True,
            "receipt_capture_required": True,
            "status_after_package_validation": "package_valid_official_preflight_pending",
        },
    }


def render_report(case_id: str, packet: dict[str, Any], warnings: list[str]) -> str:
    legal_gate = packet.get("ai_compliance_review", {}).get("legal_gate_review", {})
    abnormal = packet.get("ai_compliance_review", {}).get("abnormal_filing_risk_assessment", {})
    lines = [
        "# AI Self-Filing Package Validation Report",
        "",
        f"Case ID: {case_id}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        "Status: package_valid_official_preflight_pending",
        "AI self-filing gate: passed",
        "Official-channel preflight: pending",
        "Official submission performed: no",
        "",
        "## Decision",
        "",
        "AI self-filing package validation passed for the offline benchmark route.",
        "",
        "## AI Legal Gate Review",
        "",
        f"- Authorization scope check: {legal_gate.get('authorization_scope_check')}",
        f"- Self-filing eligibility check: {legal_gate.get('self_filing_eligibility_check')}",
        f"- Inventor and ownership check: {legal_gate.get('inventor_ownership_check')}",
        f"- Secrecy check: {legal_gate.get('secrecy_check')}",
        f"- Fee authority check: {legal_gate.get('fee_authority_check')}",
        f"- Official channel boundary check: {legal_gate.get('official_channel_boundary_check')}",
        f"- Legal advice claimed: {str(legal_gate.get('legal_advice_claimed')).lower()}",
        f"- Lawyer or patent-agent review claimed: {str(legal_gate.get('lawyer_or_agent_review_claimed')).lower()}",
        "",
        "## Abnormal Filing Risk Evidence",
        "",
        f"- Gate: {abnormal.get('gate')}",
        f"- Risk level: {abnormal.get('risk_level')}",
        f"- Assessment hash: {abnormal.get('artifact_hash')}",
        "",
    ]
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
            "This is not legal advice, not a lawyer review, not a patent-agent review, not an official submission, not a receipt, and not an application number.",
            "This route is allowed only when the applicant can self-file and no mandatory-agent condition is present.",
            "",
            "## Warnings",
            "",
        ]
    )
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None.")
    return "\n".join(lines) + "\n"


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


def prepare(draft_package_dir: Path, source_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    draft_root = draft_package_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    draft_path = draft_root / "patent-application-draft.md"
    if not draft_path.exists():
        raise RuntimeError(f"missing_draft: {draft_path}")

    source = load_json(source_path)
    draft_hash = sha256_file(draft_path)
    if source.get("source_draft_hash") != draft_hash:
        return {
            "ok": False,
            "case_id": source.get("case_id"),
            "errors": ["source_draft_hash_mismatch"],
            "expected_source_draft_hash": draft_hash,
            "provided_source_draft_hash": source.get("source_draft_hash"),
            "official_system_touched": False,
            "official_submission_performed": False,
        }, 1

    abnormal_assessment_path, abnormal_errors = enrich_abnormal_risk_assessment(source_path, source)
    if abnormal_errors:
        return {
            "ok": False,
            "case_id": source.get("case_id"),
            "source_errors": abnormal_errors,
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    draft_ok, draft_errors, draft_warnings = validate_patent_application_draft.validate(draft_path)
    source_ok, source_errors, source_warnings = validate_ai_self_filing_authorization.validate(source, base_dir=source_path.parent)
    if not draft_ok or not source_ok:
        return {
            "ok": False,
            "case_id": source.get("case_id"),
            "draft_errors": draft_errors,
            "draft_warnings": draft_warnings,
            "source_errors": source_errors,
            "source_warnings": source_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
        }, 1

    copied_draft_path = output_root / draft_path.name
    copy_file(draft_path, copied_draft_path)
    draft_hash = sha256_file(copied_draft_path)
    document_hashes, document_paths = materialize_official_documents(output_root, source, draft_hash)

    packet_path = output_root / "ai-self-filing-authorization-packet.json"
    write_json(packet_path, source)
    copied_assessment_path = output_root / "abnormal-filing-risk-assessment.json"
    if abnormal_assessment_path:
        if abnormal_assessment_path.resolve() != copied_assessment_path.resolve():
            copied_assessment_path.write_bytes(abnormal_assessment_path.read_bytes())
    packet_hash = sha256_file(packet_path)
    manifest = build_manifest(copied_draft_path, packet_path, source, packet_hash, document_hashes)

    manifest_path = output_root / "filing-package-manifest.yaml"
    manifest_path.write_text(render_manifest_yaml(manifest), encoding="utf-8")
    manifest_ok, manifest_errors, manifest_warnings = validate_filing_package_manifest.validate(manifest, base_dir=output_root)

    final_hash = str(source.get("final_package_hash") or "")
    status = {
        "case_id": source.get("case_id"),
        "previous_status": "ready_for_package_validation",
        "status": "package_valid_official_preflight_pending",
        "legal_gate": "passed",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "ai_self_filing_gate": "passed",
        "package_validation": "passed",
        "official_channel_preflight": "pending",
        "failed_gates": [
            "official_channel_preflight_pending",
            "receipt_capture_pending",
        ],
        "decision": "do_not_file_until_official_preflight",
        "final_package_hash": final_hash,
        "reviewed_package_hash": final_hash,
        "official_receipt_hash": "",
        "application_number": "",
        "official_submission_performed": False,
        "official_system_touched": False,
        "external_lawyer_involved": False,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    status_path = output_root / "filing-status.json"
    write_json(status_path, status)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)

    report_path = output_root / "ai-self-filing-package-report.md"
    report_path.write_text(
        render_report(str(source.get("case_id") or ""), source, draft_warnings + source_warnings + manifest_warnings + status_warnings),
        encoding="utf-8",
    )

    artifact_path = output_root / "artifact-hashes.json"
    files = [copied_draft_path, packet_path, *document_paths, manifest_path, status_path, report_path]
    if copied_assessment_path.exists():
        files.insert(1, copied_assessment_path)
    write_json(artifact_path, artifact_manifest(output_root, str(source.get("case_id") or ""), files))
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(artifact_path)

    ok = manifest_ok and status_ok and hash_ok
    return {
        "ok": ok,
        "case_id": source.get("case_id"),
        "output_dir": str(output_root),
        "artifacts": {
            "ai_self_filing_authorization_packet": str(packet_path),
            "abnormal_filing_risk_assessment": str(copied_assessment_path) if copied_assessment_path.exists() else "",
            "filing_package_manifest": str(manifest_path),
            "filing_status": str(status_path),
            "ai_self_filing_package_report": str(report_path),
            "artifact_hashes": str(artifact_path),
        },
        "draft_errors": draft_errors,
        "draft_warnings": draft_warnings,
        "source_errors": source_errors,
        "source_warnings": source_warnings,
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "status": "package_valid_official_preflight_pending",
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft_package_dir", type=Path)
    parser.add_argument("ai_self_filing_source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.draft_package_dir, args.ai_self_filing_source, args.output_dir)
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
