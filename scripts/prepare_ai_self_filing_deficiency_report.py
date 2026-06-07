#!/usr/bin/env python3
"""Generate an AI self-filing legal gate deficiency report."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import build_case_queue
import validate_ai_self_filing_authorization
import validate_artifact_hash_manifest
import validate_filing_status_transition


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
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if not isinstance(cur, dict):
            raise ValueError(f"mutation_parent_not_object: {dotted}")
        cur = cur.setdefault(part, {})
    if not isinstance(cur, dict):
        raise ValueError(f"mutation_target_parent_not_object: {dotted}")
    cur[parts[-1]] = value


def remove_path(data: dict[str, Any], dotted: str) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if not isinstance(cur, dict) or part not in cur:
            return
        cur = cur[part]
    if isinstance(cur, dict):
        cur.pop(parts[-1], None)


def apply_case(base: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    packet = copy.deepcopy(base)
    for dotted in case.get("remove_paths", []):
        remove_path(packet, str(dotted))
    mutations = case.get("mutations") if isinstance(case.get("mutations"), dict) else {}
    for dotted, value in mutations.items():
        set_path(packet, str(dotted), value)
    return packet


def load_packet(packet_path: Path, rejection_case_id: str | None) -> tuple[dict[str, Any], Path]:
    if not rejection_case_id:
        return load_json(packet_path), packet_path.parent

    spec = load_json(packet_path)
    base_path = Path(str(spec.get("base_packet") or ""))
    if not base_path.is_absolute():
        base_path = (packet_path.parent / base_path).resolve()
    base = load_json(base_path)
    for case in spec.get("cases", []):
        if isinstance(case, dict) and case.get("id") == rejection_case_id:
            packet = apply_case(base, case)
            packet["case_id"] = f"{base.get('case_id')}-{rejection_case_id}"
            return packet, base_path.parent
    raise ValueError(f"rejection_case_not_found: {rejection_case_id}")


def classify_error(error: str) -> dict[str, Any]:
    lower = error.lower()
    if "source_draft_hash" in lower or "final_package_hash" in lower or "reviewed_artifacts_hash" in lower:
        return {
            "gate": "G0 Final version identity",
            "risk": "Package version identity is not provable.",
            "cure": "Provide sha256 hashes for the source draft, final package, and reviewed artifacts.",
            "owner": "Applicant filing operator",
        }
    if "legal_advice" in lower or "lawyer_or_agent" in lower or "legal_gate_review" in lower:
        return {
            "gate": "G1 AI legal/compliance review mode",
            "risk": "The AI-only route could falsely represent legal advice, lawyer review, or patent-agent review.",
            "cure": "Remove review misrepresentation and provide a complete AI legal gate review record.",
            "owner": "AI legal gate operator",
        }
    if "self_filing" in lower or "mandatory_agent" in lower or "foreign_or_hmt" in lower or "agency_bypass" in lower:
        return {
            "gate": "G1 AI self-filing eligibility",
            "risk": "The applicant may not be eligible for this self-filing route.",
            "cure": "Provide self-filing eligibility evidence or move the case out of the AI self-filing route.",
            "owner": "Applicant filing operator",
        }
    if "authorization_scope" in lower or "allowed_actions" in lower or "submit_or_file" in lower:
        return {
            "gate": "G2 Applicant authorization",
            "risk": "The requested filing action may exceed applicant authority.",
            "cure": "Provide explicit applicant authorization covering filing, submission, and fee actions.",
            "owner": "Applicant authorized person",
        }
    if "inventor" in lower:
        return {
            "gate": "G3 Inventor confirmation",
            "risk": "Inventorship or contribution evidence is incomplete.",
            "cure": "Confirm inventor names, order, and technical contribution.",
            "owner": "Inventor confirmation owner",
        }
    if "ownership" in lower:
        return {
            "gate": "G4 Ownership and chain of title",
            "risk": "Ownership or chain-of-title evidence is unresolved.",
            "cure": "Provide ownership basis, assignment, service invention, or collaboration evidence.",
            "owner": "Applicant ownership owner",
        }
    if "secrecy" in lower or "foreign_or_pct" in lower:
        return {
            "gate": "G5 Confidentiality and secrecy review",
            "risk": "Foreign/PCT or secrecy-review constraints may be unresolved.",
            "cure": "Resolve China completion, foreign/PCT plan, and secrecy-review status.",
            "owner": "Secrecy review owner",
        }
    if "fee" in lower or "pay" in lower:
        return {
            "gate": "G7 Fee authority",
            "risk": "Official fee payment could be unauthorized.",
            "cure": "Provide payer, fee-reduction status, payment reference, and automatic payment authority.",
            "owner": "Fee authority owner",
        }
    if "copying" in lower or "support" in lower or "abnormal" in lower or "format" in lower:
        return {
            "gate": "G8 AI technical and abnormal-filing checks",
            "risk": "The filing may be unsupported, copied, abnormal, or format-invalid.",
            "cure": "Resolve AI no-copying, claim support, abnormal filing risk, and official-format checks.",
            "owner": "AI compliance operator",
        }
    if "official" in lower or "automation" in lower or "bypass" in lower or "human_only" in lower:
        return {
            "gate": "G9 Official-channel compliance",
            "risk": "The filing path could bypass official controls or exceed allowed automation.",
            "cure": "Provide official account, signature authority, automation permission, and no-bypass evidence.",
            "owner": "Official channel owner",
        }
    return {
        "gate": "G10 Audit readiness",
        "risk": "The audit trail is incomplete.",
        "cure": "Provide missing evidence and rerun the AI self-filing legal gate.",
        "owner": "Case owner",
    }


def build_deficiencies(errors: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for error in errors:
        meta = classify_error(error)
        rows.append(
            {
                "gate": meta["gate"],
                "validator_error": error,
                "missing_or_contradictory_evidence": error,
                "filing_risk_if_ignored": meta["risk"],
                "required_cure": meta["cure"],
                "owner": meta["owner"],
                "draft_only_work_allowed": True,
            }
        )
    return rows


def render_report(case_id: str, packet_hash: str, deficiencies: list[dict[str, Any]]) -> str:
    lines = [
        "# AI Self-Filing Deficiency Report",
        "",
        f"Case ID: {case_id}",
        "Status: legal_gate_failed",
        "Decision: do_not_file",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        f"Packet hash: {packet_hash}",
        "Official system touched: no",
        "Official submission performed: no",
        "",
        "## Failed Gates",
        "",
        "| Gate | Missing or contradictory evidence | Filing risk if ignored | Required cure | Owner |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in deficiencies:
        lines.append(
            "| {gate} | {evidence} | {risk} | {cure} | {owner} |".format(
                gate=str(item["gate"]).replace("|", "/"),
                evidence=str(item["missing_or_contradictory_evidence"]).replace("|", "/"),
                risk=str(item["filing_risk_if_ignored"]).replace("|", "/"),
                cure=str(item["required_cure"]).replace("|", "/"),
                owner=str(item["owner"]).replace("|", "/"),
            )
        )
    lines.extend(
        [
            "",
            "## Draft-Only Work Allowed",
            "",
            "Draft-only analysis may continue. Filing package validation, official-channel preflight, signing, payment, submission, receipt capture, and application-number status are blocked until every failed gate is cured.",
            "",
            "## Boundary",
            "",
            "This report is AI-generated gate evidence, not legal advice, not lawyer review, not patent-agent review, not an official submission, not a receipt, and not an application number.",
            "",
            "## Filing Stop Rule",
            "",
            "Do not file, pay, sign, submit, or represent official submission status until every failed gate is cured and the final package hash is authorized.",
            "",
        ]
    )
    return "\n".join(lines)


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


def prepare(packet_path: Path, output_dir: Path, rejection_case_id: str | None = None) -> tuple[dict[str, Any], int]:
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    packet, packet_base_dir = load_packet(packet_path.resolve(), rejection_case_id)
    packet_out = output_root / "ai-self-filing-authorization-packet.json"
    write_json(packet_out, packet)
    packet_hash = sha256_file(packet_out)

    passed, errors, warnings = validate_ai_self_filing_authorization.validate(packet, base_dir=packet_base_dir)
    if passed:
        return {
            "ok": False,
            "case_id": packet.get("case_id"),
            "errors": ["packet_passed_no_deficiency_report_needed"],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    case_id = str(packet.get("case_id") or "unknown-case")
    deficiencies = build_deficiencies(errors)
    deficiency = {
        "case_id": case_id,
        "status": "legal_gate_failed",
        "decision": "do_not_file",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "filing_allowed": False,
        "draft_only_work_allowed": True,
        "source_packet_hash": packet_hash,
        "validator_errors": errors,
        "validator_warnings": warnings,
        "deficiencies": deficiencies,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }
    deficiency_path = output_root / "deficiency-report.json"
    write_json(deficiency_path, deficiency)

    status = {
        "case_id": case_id,
        "previous_status": "draft_only",
        "status": "legal_gate_failed",
        "legal_gate": "failed",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "ai_self_filing_gate": "failed",
        "failed_gates": sorted({item["gate"] for item in deficiencies}),
        "decision": "do_not_file",
        "final_package_hash": str(packet.get("final_package_hash") or ""),
        "reviewed_package_hash": "",
        "official_receipt_hash": "",
        "application_number": "",
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    status_path = output_root / "filing-status.json"
    write_json(status_path, status)

    report_path = output_root / "deficiency-report.md"
    report_path.write_text(render_report(case_id, packet_hash, deficiencies), encoding="utf-8")

    hashes_path = output_root / "artifact-hashes.json"
    write_json(hashes_path, artifact_manifest(output_root, case_id, [packet_out, deficiency_path, status_path, report_path]))

    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
    ok = status_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "ai_self_filing_authorization_packet": str(packet_out),
            "deficiency_report_json": str(deficiency_path),
            "filing_status": str(status_path),
            "deficiency_report_markdown": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "deficiency_count": len(deficiencies),
        "validator_errors": errors,
        "validator_warnings": warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet_or_rejection_cases", type=Path)
    parser.add_argument("--rejection-case-id")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.packet_or_rejection_cases, args.output_dir, args.rejection_case_id)
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
