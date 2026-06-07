#!/usr/bin/env python3
"""Revalidate an AI self-filing packet after a legal-gate cure."""

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
import validate_ai_self_filing_deficiency_report_benchmark
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


def apply_cure_source(source_path: Path) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    source = load_json(source_path)
    packet_ref = source.get("cured_packet") or source.get("base_packet")
    if not packet_ref:
        return source, source_path.parent, {"source_type": "direct_packet", "cure_notes": []}

    packet_path = Path(str(packet_ref))
    if not packet_path.is_absolute():
        packet_path = (source_path.parent / packet_path).resolve()
    packet = copy.deepcopy(load_json(packet_path))
    for dotted in source.get("remove_paths", []):
        remove_path(packet, str(dotted))
    mutations = source.get("mutations") if isinstance(source.get("mutations"), dict) else {}
    for dotted, value in mutations.items():
        set_path(packet, str(dotted), value)
    if source.get("case_id"):
        packet["case_id"] = source["case_id"]
    return packet, packet_path.parent, {
        "source_type": "cure_source",
        "cured_packet_source": str(packet_path),
        "cure_notes": source.get("cure_notes", []),
        "mutated_paths": sorted(str(key) for key in mutations),
        "removed_paths": [str(item) for item in source.get("remove_paths", [])],
    }


def copy_json_file(source: Path, target: Path) -> None:
    target.write_bytes(source.read_bytes())


def render_report(revalidation: dict[str, Any]) -> str:
    prior_errors = revalidation.get("prior_validator_errors") or []
    lines = [
        "# AI Self-Filing Cure Revalidation Report",
        "",
        f"Case ID: {revalidation.get('case_id')}",
        f"Source case ID: {revalidation.get('source_case_id')}",
        "Previous status: legal_gate_failed",
        "New status: ready_for_package_validation",
        "Decision: package_validation_required_before_official_preflight",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        f"Source deficiency hash: {revalidation.get('source_deficiency_hash')}",
        f"Source failed packet hash: {revalidation.get('source_failed_packet_hash')}",
        f"Cured packet hash: {revalidation.get('cured_packet_hash')}",
        "Official system touched: no",
        "Official submission performed: no",
        "",
        "## Cured Prior Errors",
        "",
        "| Prior validator error | Cure status |",
        "| --- | --- |",
    ]
    if prior_errors:
        lines.extend(f"| {str(error).replace('|', '/')} | cured |" for error in prior_errors)
    else:
        lines.append("| None recorded | not applicable |")
    lines.extend(
        [
            "",
            "## Next Allowed Step",
            "",
            "Run AI self-filing package validation before official-channel preflight. Do not file, pay, sign, submit, upload, capture a receipt, or claim an application number from this revalidation alone.",
            "",
            "## Boundary",
            "",
            "This report is AI-generated gate evidence, not legal advice, not lawyer review, not patent-agent review, not an official submission, not a receipt, and not an application number.",
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


def prepare(deficiency_dir: Path, cured_packet_source: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    deficiency_root = deficiency_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    deficiency_ok, deficiency_errors, deficiency_warnings = validate_ai_self_filing_deficiency_report_benchmark.validate(deficiency_root)
    if not deficiency_ok:
        return {
            "ok": False,
            "errors": [f"source_deficiency: {item}" for item in deficiency_errors],
            "warnings": [f"source_deficiency: {item}" for item in deficiency_warnings],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    source_packet_path = deficiency_root / "ai-self-filing-authorization-packet.json"
    source_deficiency_path = deficiency_root / "deficiency-report.json"
    source_packet = load_json(source_packet_path)
    source_deficiency = load_json(source_deficiency_path)
    source_ok, source_errors, source_warnings = validate_ai_self_filing_authorization.validate(source_packet, base_dir=deficiency_root)
    if source_ok:
        return {
            "ok": False,
            "case_id": source_packet.get("case_id"),
            "errors": ["source_packet_unexpectedly_passed"],
            "warnings": source_warnings,
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    cured_packet, cured_packet_base_dir, cure_source_meta = apply_cure_source(cured_packet_source.resolve())
    cured_ok, cured_errors, cured_warnings = validate_ai_self_filing_authorization.validate(cured_packet, base_dir=cured_packet_base_dir)
    if not cured_ok:
        return {
            "ok": False,
            "case_id": cured_packet.get("case_id"),
            "source_case_id": source_deficiency.get("case_id"),
            "errors": [f"cured_packet: {item}" for item in cured_errors],
            "warnings": [f"source_packet: {item}" for item in source_warnings] + [f"cured_packet: {item}" for item in cured_warnings],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    source_deficiency_out = output_root / "source-deficiency-report.json"
    source_packet_out = output_root / "source-failed-authorization-packet.json"
    cured_packet_out = output_root / "cured-ai-self-filing-authorization-packet.json"
    copy_json_file(source_deficiency_path, source_deficiency_out)
    copy_json_file(source_packet_path, source_packet_out)
    write_json(cured_packet_out, cured_packet)

    prior_errors = source_deficiency.get("validator_errors")
    if not isinstance(prior_errors, list):
        prior_errors = source_errors
    unresolved = [str(error) for error in prior_errors if str(error) in cured_errors]
    case_id = str(cured_packet.get("case_id") or source_deficiency.get("case_id") or "unknown-case")

    revalidation = {
        "case_id": case_id,
        "source_case_id": source_deficiency.get("case_id"),
        "status": "ready_for_package_validation",
        "decision": "package_validation_required_before_official_preflight",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "source_deficiency_hash": sha256_file(source_deficiency_out),
        "source_failed_packet_hash": sha256_file(source_packet_out),
        "cured_packet_hash": sha256_file(cured_packet_out),
        "prior_validator_errors": [str(item) for item in prior_errors],
        "source_validation_errors": source_errors,
        "source_validation_warnings": source_warnings,
        "post_validation_errors": cured_errors,
        "post_validation_warnings": cured_warnings,
        "unresolved_prior_errors": unresolved,
        "cure_source": cure_source_meta,
        "filing_allowed": False,
        "package_validation_required": True,
        "official_channel_preflight_required": True,
        "next_allowed_step": "run_ai_self_filing_package_validation_before_official_preflight",
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }
    revalidation_path = output_root / "cure-revalidation.json"
    write_json(revalidation_path, revalidation)

    status = {
        "case_id": case_id,
        "previous_status": "legal_gate_failed",
        "status": "ready_for_package_validation",
        "legal_gate": "passed",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "ai_self_filing_gate": "passed",
        "package_validation": "pending",
        "failed_gates": [
            "package_validation_pending",
            "official_channel_preflight_pending",
            "receipt_capture_pending",
        ],
        "decision": "package_validation_required_before_official_preflight",
        "final_package_hash": str(cured_packet.get("final_package_hash") or ""),
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

    report_path = output_root / "cure-revalidation-report.md"
    report_path.write_text(render_report(revalidation), encoding="utf-8")

    hashes_path = output_root / "artifact-hashes.json"
    files = [source_deficiency_out, source_packet_out, cured_packet_out, revalidation_path, status_path, report_path]
    write_json(hashes_path, artifact_manifest(output_root, case_id, files))

    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
    ok = status_ok and hash_ok and not unresolved
    return {
        "ok": ok,
        "case_id": case_id,
        "source_case_id": source_deficiency.get("case_id"),
        "output_dir": str(output_root),
        "artifacts": {
            "source_deficiency_report": str(source_deficiency_out),
            "source_failed_authorization_packet": str(source_packet_out),
            "cured_ai_self_filing_authorization_packet": str(cured_packet_out),
            "cure_revalidation": str(revalidation_path),
            "filing_status": str(status_path),
            "cure_revalidation_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "prior_validator_errors": [str(item) for item in prior_errors],
        "unresolved_prior_errors": unresolved,
        "post_validation_warnings": cured_warnings,
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
    parser.add_argument("deficiency_dir", type=Path)
    parser.add_argument("cured_packet_source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.deficiency_dir, args.cured_packet_source, args.output_dir)
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
