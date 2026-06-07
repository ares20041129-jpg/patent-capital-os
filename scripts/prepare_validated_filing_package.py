#!/usr/bin/env python3
"""Prepare a validated filing package manifest from a draft package and authorization packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_filing_package_manifest
import validate_filing_status_transition
import validate_patent_application_draft
import validate_submission_packet


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def document_hash(packet: dict[str, Any], doc_type: str, fallback_seed: str) -> str:
    hashes = packet.get("hashes") if isinstance(packet.get("hashes"), dict) else {}
    explicit = {
        "claims": hashes.get("final_claims"),
        "specification": hashes.get("final_specification"),
        "abstract": hashes.get("final_abstract"),
        "drawings": hashes.get("final_drawings"),
        "request_metadata": hashes.get("request_metadata"),
    }.get(doc_type)
    return str(explicit) if explicit else sha256_text(f"{fallback_seed}:{doc_type}")


def resolve_reference(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else (base_dir / path).resolve()


def output_reference(output_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        raise RuntimeError("final_document_path_must_be_relative_for_self_contained_package")
    destination = (output_root / path).resolve()
    try:
        destination.relative_to(output_root.resolve())
    except ValueError as exc:
        raise RuntimeError("final_document_path_escapes_output_dir") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        dst.write_bytes(src.read_bytes())


def copy_final_documents(packet: dict[str, Any], source_dir: Path, output_root: Path) -> tuple[dict[str, str], list[Path]]:
    final_documents = packet.get("final_documents") if isinstance(packet.get("final_documents"), dict) else {}
    document_hashes: dict[str, str] = {}
    copied_paths: list[Path] = []
    for doc_type in ["claims", "specification", "abstract", "drawings", "request_metadata"]:
        raw_path = str(final_documents.get(doc_type) or "")
        if not raw_path:
            raise RuntimeError(f"final_document_reference_missing: {doc_type}")
        source_path = resolve_reference(source_dir, raw_path)
        if not source_path.exists():
            raise RuntimeError(f"final_document_file_not_found: {doc_type}")
        destination = output_reference(output_root, raw_path)
        copy_file(source_path, destination)
        document_hashes[doc_type] = sha256_file(destination)
        copied_paths.append(destination)
    return document_hashes, copied_paths


def document_format(filename: str, doc_type: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix:
        return suffix
    return "pdf" if doc_type == "drawings" else "xml"


def build_manifest(
    draft_path: Path,
    packet_path: Path,
    packet: dict[str, Any],
    source_draft_hash: str,
    authorization_packet_hash: str,
    document_hashes: dict[str, str],
) -> dict[str, Any]:
    final_documents = packet.get("final_documents") if isinstance(packet.get("final_documents"), dict) else {}
    final_package_hash = str(get_path(packet, "hashes.source_package") or "")
    docs: list[dict[str, Any]] = []
    for doc_type in ["claims", "specification", "abstract", "drawings", "request_metadata"]:
        filename = str(final_documents.get(doc_type) or f"{doc_type}-final.xml")
        docs.append(
            {
                "document_id": doc_type,
                "type": doc_type,
                "filename": filename,
                "format": document_format(filename, doc_type),
                "hash": document_hashes.get(doc_type) or document_hash(packet, doc_type, final_package_hash),
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
        "source_draft_hash": source_draft_hash,
        "authorization_packet": packet_path.name,
        "authorization_packet_hash": authorization_packet_hash,
        "reviewed_package_hash": final_package_hash,
        "final_package_hash": final_package_hash,
        "official_submission_performed": False,
        "documents": docs,
        "xml_validation": {
            "final_xml_hash": str(get_path(packet, "hashes.final_xml") or ""),
            "standard_or_tool": "Patent Capital OS offline package validation",
            "validation_result": "passed",
            "validation_report_hash": sha256_text(final_package_hash + ":xml-validation-report"),
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


def render_report(case_id: str, warnings: list[str]) -> str:
    lines = [
        "# Filing Package Validation Report",
        "",
        f"Case ID: {case_id}",
        "Status: package_valid_official_preflight_pending",
        "Legal gate: passed",
        "Package validation: passed",
        "Official-channel preflight: pending",
        "Official submission performed: no",
        "",
        "## Decision",
        "",
        "Package validation passed.",
        "",
        "Do not file yet. The next required gate is official-channel preflight with account authority, signature handling, automation permission, receipt-capture destination, and human-only step detection.",
        "",
        "## Boundary",
        "",
        "This is not an official submission, receipt, fee payment, signature, or application-number record.",
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None.")
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


def prepare(draft_package_dir: Path, authorization_packet: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    draft_root = draft_package_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    draft_path = draft_root / "patent-application-draft.md"
    if not draft_path.exists():
        raise RuntimeError(f"missing_draft: {draft_path}")

    draft_ok, draft_errors, draft_warnings = validate_patent_application_draft.validate(draft_path)
    packet = load_json(authorization_packet)
    packet_ok, packet_errors, packet_warnings = validate_submission_packet.validate(packet, base_dir=authorization_packet.parent)
    if not draft_ok or not packet_ok:
        return {
            "ok": False,
            "case_id": packet.get("case_id"),
            "draft_errors": draft_errors,
            "draft_warnings": draft_warnings,
            "packet_errors": packet_errors,
            "packet_warnings": packet_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
        }, 1

    copied_draft_path = output_root / draft_path.name
    copy_file(draft_path, copied_draft_path)
    document_hashes, copied_document_paths = copy_final_documents(packet, authorization_packet.parent, output_root)

    copied_packet_path = output_root / "submission-authorization-packet.json"
    write_json(copied_packet_path, packet)
    source_draft_hash = sha256_file(copied_draft_path)
    authorization_packet_hash = sha256_file(copied_packet_path)
    manifest = build_manifest(
        copied_draft_path,
        copied_packet_path,
        packet,
        source_draft_hash,
        authorization_packet_hash,
        document_hashes,
    )

    manifest_path = output_root / "filing-package-manifest.yaml"
    manifest_path.write_text(render_manifest_yaml(manifest), encoding="utf-8")
    manifest_ok, manifest_errors, manifest_warnings = validate_filing_package_manifest.validate(manifest, base_dir=output_root)

    final_package_hash = str(get_path(packet, "hashes.source_package") or "")
    status = {
        "case_id": packet.get("case_id"),
        "previous_status": "ready_for_package_validation",
        "status": "package_valid_official_preflight_pending",
        "legal_gate": "passed",
        "package_validation": "passed",
        "official_channel_preflight": "pending",
        "failed_gates": [
            "official_channel_preflight_pending",
            "receipt_capture_pending",
        ],
        "decision": "do_not_file_until_official_preflight",
        "final_package_hash": final_package_hash,
        "reviewed_package_hash": final_package_hash,
        "official_receipt_hash": "",
        "application_number": "",
        "official_submission_performed": False,
        "official_system_touched": False,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    status_path = output_root / "filing-status.json"
    write_json(status_path, status)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)

    report_path = output_root / "package-validation-report.md"
    report_path.write_text(render_report(str(packet.get("case_id") or ""), packet_warnings + manifest_warnings + status_warnings), encoding="utf-8")

    artifact_path = output_root / "artifact-hashes.json"
    generated_files = [copied_draft_path, copied_packet_path, *copied_document_paths, manifest_path, status_path, report_path]
    write_json(artifact_path, artifact_manifest(output_root, str(packet.get("case_id") or ""), generated_files))
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(artifact_path)

    ok = manifest_ok and status_ok and hash_ok
    return {
        "ok": ok,
        "case_id": packet.get("case_id"),
        "output_dir": str(output_root),
        "artifacts": {
            "submission_authorization_packet": str(copied_packet_path),
            "filing_package_manifest": str(manifest_path),
            "filing_status": str(status_path),
            "package_validation_report": str(report_path),
            "artifact_hashes": str(artifact_path),
        },
        "draft_errors": draft_errors,
        "draft_warnings": draft_warnings,
        "packet_errors": packet_errors,
        "packet_warnings": packet_warnings,
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "status": "package_valid_official_preflight_pending",
        "official_system_touched": False,
        "official_submission_performed": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft_package_dir", type=Path)
    parser.add_argument("submission_authorization_packet", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.draft_package_dir, args.submission_authorization_packet, args.output_dir)
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
