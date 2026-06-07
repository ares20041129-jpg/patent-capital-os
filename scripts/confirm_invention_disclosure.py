#!/usr/bin/env python3
"""Promote a disclosure scaffold to a confirmed draft-generation disclosure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_disclosure_confirmation_packet
import validate_filing_status_transition
import validate_invention_disclosure
import validate_invention_disclosure_scaffold


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def merge_unique(base: list[Any], extra: list[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for item in base + extra:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            result.append(item)
            seen.add(key)
    return result


def build_disclosure(scaffold: dict[str, Any], packet: dict[str, Any], packet_hash: str) -> dict[str, Any]:
    disclosure = dict(scaffold.get("invention_disclosure", {}))
    disclosure["case_id"] = packet["case_id"]
    disclosure["business_goal"] = disclosure.get("business_goal") or "Generate draft-only patent artifacts for AI self-filing legal/compliance authorization."
    disclosure["applicant_context"] = packet["applicant_context"]
    disclosure["inventor_input"] = packet["inventor_input"]
    disclosure["technical_effects"] = packet["technical_effects"]
    disclosure["similarity_control"] = packet["similarity_control"]
    disclosure["secrecy"] = packet["secrecy"]

    evidence = dict(disclosure.get("data_and_evidence", {}))
    packet_evidence = packet.get("data_and_evidence", {})
    if isinstance(packet_evidence, dict):
        prohibited_reference_hashes = (
            packet_evidence.get("prohibited_reference_hashes", [])
            if isinstance(packet_evidence.get("prohibited_reference_hashes"), list)
            else []
        )
        for key in ["prototypes", "experiments", "logs_or_measurements", "prohibited_reference_hashes"]:
            evidence[key] = merge_unique(
                evidence.get(key, []) if isinstance(evidence.get(key), list) else [],
                packet_evidence.get(key, []) if isinstance(packet_evidence.get(key), list) else [],
            )
        source_hashes = packet_evidence.get("source_hashes", [])
        if isinstance(source_hashes, list):
            evidence["source_hashes"] = [
                item
                for item in merge_unique([], source_hashes)
                if item not in prohibited_reference_hashes
            ]
    disclosure["data_and_evidence"] = evidence

    packet_questions = packet.get("ai_legal_compliance_questions")
    if packet_questions:
        disclosure["ai_legal_compliance_questions"] = merge_unique(
            disclosure.get("ai_legal_compliance_questions", [])
            if isinstance(disclosure.get("ai_legal_compliance_questions"), list)
            else [],
            packet_questions if isinstance(packet_questions, list) else [],
        )
    disclosure.pop("counsel_questions", None)

    disclosure["confirmation_record"] = {
        "confirmed_at": packet.get("confirmed_at"),
        "scaffold_hash": packet.get("scaffold_hash"),
        "confirmation_packet_hash": packet_hash,
        "legal_drafting_review": packet.get("legal_drafting_review"),
        "draft_generation_allowed": True,
        "filing_allowed": False,
        "external_lawyer_involved": False,
    }
    return disclosure


def render_report(
    case_id: str,
    scaffold_hash: str,
    packet_hash: str,
    disclosure_ok: bool,
    packet_warnings: list[str],
) -> str:
    lines = [
        "# Disclosure Confirmation Report",
        "",
        f"Case ID: {case_id}",
        f"Scaffold hash: {scaffold_hash}",
        f"Confirmation packet hash: {packet_hash}",
        f"Disclosure validation: {'pass' if disclosure_ok else 'fail'}",
        "Draft generation allowed: yes",
        "Filing allowed: no",
        "Legal gate for filing: failed",
        "Official system touched: no",
        "Official submission performed: no",
        "",
        "## Confirmation Scope",
        "",
        "- Inventor contribution confirmed.",
        "- Applicant and ownership basis confirmed.",
        "- No-copying and no-synonym-substitution confirmed.",
        "- Technical effects have evidence references.",
        "- Secrecy status resolved for the stated jurisdiction plan.",
        "- AI legal/compliance draft review is limited to draft generation only.",
        "- No external lawyer or patent-agent review is claimed for this confirmation stage.",
        "",
        "## Filing Stop Rule",
        "",
        "Do not file until final AI self-filing legal/compliance authorization, applicant filing authorization, agency/signature authority, fee authority, official-channel preflight, and package hash match are validated.",
        "",
        "## Warnings",
        "",
    ]
    if packet_warnings:
        for warning in packet_warnings:
            lines.append(f"- {warning}")
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


def confirm(scaffold_path: Path, packet_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    scaffold = load_json(scaffold_path)
    packet = load_json(packet_path)
    scaffold_hash = sha256_file(scaffold_path)
    packet_hash = sha256_file(packet_path)

    scaffold_ok, scaffold_errors, scaffold_warnings = validate_invention_disclosure_scaffold.validate(scaffold)
    packet_ok, packet_errors, packet_warnings = validate_disclosure_confirmation_packet.validate(packet, scaffold_hash)
    case_id = str(packet.get("case_id") or "")
    if scaffold.get("case_id") != case_id:
        packet_ok = False
        packet_errors.append("case_id_mismatch_between_scaffold_and_confirmation_packet")

    if not scaffold_ok or not packet_ok:
        response = {
            "ok": False,
            "case_id": case_id,
            "output_dir": str(output_root),
            "scaffold_hash": scaffold_hash,
            "confirmation_packet_hash": packet_hash,
            "scaffold_errors": scaffold_errors,
            "scaffold_warnings": scaffold_warnings,
            "packet_errors": packet_errors,
            "packet_warnings": packet_warnings,
            "draft_generation_allowed": False,
            "filing_allowed": False,
            "external_lawyer_involved": False,
            "official_system_touched": False,
            "official_submission_performed": False,
        }
        return response, 1

    disclosure = build_disclosure(scaffold, packet, packet_hash)
    disclosure_ok, disclosure_errors, disclosure_warnings = validate_invention_disclosure.validate(disclosure)

    disclosure_path = output_root / "invention-disclosure.json"
    status_path = output_root / "filing-status.json"
    report_path = output_root / "confirmation-report.md"
    artifact_path = output_root / "artifact-hashes.json"

    write_json(disclosure_path, disclosure)
    filing_status = {
        "case_id": case_id,
        "previous_status": "intake_received",
        "status": "draft_only",
        "legal_gate": "failed",
        "failed_gates": [
            "G1 final_ai_self_filing_legal_compliance_authorization_absent",
            "G2 applicant_filing_authorization_absent",
            "G6 agency_and_signature_authority_absent",
            "G7 fee_authority_absent",
            "G9 official_channel_preflight_absent",
        ],
        "decision": "do_not_file",
        "draft_generation_allowed": True,
        "filing_allowed": False,
        "external_lawyer_involved": False,
        "final_package_hash": "",
        "reviewed_package_hash": "",
        "official_receipt_hash": "",
        "application_number": "",
        "official_system_touched": False,
        "official_submission_performed": False,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    write_json(status_path, filing_status)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(filing_status)

    report_path.write_text(
        render_report(case_id, scaffold_hash, packet_hash, disclosure_ok, packet_warnings),
        encoding="utf-8",
    )
    manifest = artifact_manifest(output_root, case_id, [disclosure_path, status_path, report_path])
    write_json(artifact_path, manifest)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(artifact_path)

    ok = scaffold_ok and packet_ok and disclosure_ok and status_ok and hash_ok
    response = {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "invention_disclosure": str(disclosure_path),
            "filing_status": str(status_path),
            "confirmation_report": str(report_path),
            "artifact_hashes": str(artifact_path),
        },
        "scaffold_hash": scaffold_hash,
        "confirmation_packet_hash": packet_hash,
        "scaffold_errors": scaffold_errors,
        "scaffold_warnings": scaffold_warnings,
        "packet_errors": packet_errors,
        "packet_warnings": packet_warnings,
        "disclosure_errors": disclosure_errors,
        "disclosure_warnings": disclosure_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "draft_generation_allowed": True,
        "filing_allowed": False,
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
    }
    return response, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scaffold", type=Path)
    parser.add_argument("confirmation_packet", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = confirm(args.scaffold, args.confirmation_packet, args.output_dir)
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "draft_generation_allowed": False,
            "filing_allowed": False,
            "external_lawyer_involved": False,
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
