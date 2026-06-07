#!/usr/bin/env python3
"""Prepare application-number acceptance artifacts from official evidence."""

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
import validate_application_number_evidence
import validate_artifact_hash_manifest
import validate_filing_status_transition
import validate_receipt_capture


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


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


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur: dict[str, Any] = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        child = cur.get(part)
        if not isinstance(child, dict):
            child = {}
            cur[part] = child
        cur = child
    cur[parts[-1]] = value


def copy_evidence_file(raw_path: Any, source_dir: Path, output_dir: Path) -> tuple[str, str]:
    if is_blank(raw_path):
        return "", ""
    src = Path(str(raw_path))
    if not src.is_absolute():
        src = (source_dir / src).resolve()
    if not src.exists():
        return str(raw_path), ""
    dst = output_dir / src.name
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return dst.name, sha256_file(dst)


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


def reference_delta_metadata(*packets: dict[str, Any]) -> dict[str, Any]:
    for packet in packets:
        if not isinstance(packet, dict):
            continue
        reference_hash = packet.get("reference_patent_delta_hash")
        if reference_hash:
            return {
                "application_materials_hash": packet.get("application_materials_hash"),
                "reference_patent_delta_hash": reference_hash,
                "reference_delta_rows_count": packet.get("reference_delta_rows_count"),
                "reference_delta_claim_elements_count": packet.get("reference_delta_claim_elements_count"),
                "reference_delta_boundary_preserved": packet.get("reference_delta_boundary_preserved") is True,
            }
    return {}


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


def validate_source_against_receipt(
    source: dict[str, Any],
    receipt_capture: dict[str, Any],
    receipt_status: dict[str, Any],
    source_base_dir: Path | None = None,
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    source_ok, source_errors, source_warnings = validate_application_number_evidence.validate(source, base_dir=source_base_dir)
    if not source_ok:
        errors.extend(source_errors)
    warnings.extend(source_warnings)

    if source.get("case_id") != receipt_status.get("case_id") or source.get("case_id") != receipt_capture.get("case_id"):
        errors.append("case_id_mismatch")
    if receipt_status.get("status") != "official_receipt_received":
        errors.append("input_status_must_be_official_receipt_received")
    if source.get("previous_status") != "official_receipt_received":
        errors.append("source_previous_status_must_be_official_receipt_received")
    if get_path(source, "official_receipt.receipt_hash") != receipt_status.get("official_receipt_hash"):
        errors.append("receipt_hash_mismatch")
    if get_path(source, "official_receipt.receipt_hash") != get_path(receipt_capture, "official_receipt.receipt_hash"):
        errors.append("receipt_capture_hash_mismatch")
    if get_path(source, "package.final_package_hash") != receipt_status.get("final_package_hash"):
        errors.append("final_package_hash_mismatch")
    if get_path(source, "package.reviewed_package_hash") != receipt_status.get("reviewed_package_hash"):
        errors.append("reviewed_package_hash_mismatch")
    if get_path(source, "package.submitted_package_hash") != receipt_status.get("final_package_hash"):
        errors.append("submitted_package_hash_mismatch")
    for value, label in [
        (source.get("official_session_authorization_hash"), "source.official_session_authorization_hash"),
        (source.get("official_session_reference_hash"), "source.official_session_reference_hash"),
        (receipt_capture.get("official_session_authorization_hash"), "receipt_capture.official_session_authorization_hash"),
        (receipt_capture.get("official_session_reference_hash"), "receipt_capture.official_session_reference_hash"),
        (receipt_status.get("official_session_authorization_hash"), "receipt_status.official_session_authorization_hash"),
        (receipt_status.get("official_session_reference_hash"), "receipt_status.official_session_reference_hash"),
    ]:
        require_hash(value, label, errors)
    if source.get("official_session_authorization_hash") != receipt_capture.get("official_session_authorization_hash"):
        errors.append("source_receipt_session_authorization_hash_mismatch")
    if source.get("official_session_authorization_hash") != receipt_status.get("official_session_authorization_hash"):
        errors.append("source_status_session_authorization_hash_mismatch")
    if source.get("official_session_reference_hash") != receipt_capture.get("official_session_reference_hash"):
        errors.append("source_receipt_session_reference_hash_mismatch")
    if source.get("official_session_reference_hash") != receipt_status.get("official_session_reference_hash"):
        errors.append("source_status_session_reference_hash_mismatch")
    reference_hash = source.get("reference_patent_delta_hash") or receipt_capture.get("reference_patent_delta_hash") or receipt_status.get("reference_patent_delta_hash")
    if reference_hash:
        for field in [
            "application_materials_hash",
            "reference_patent_delta_hash",
            "reference_delta_rows_count",
            "reference_delta_claim_elements_count",
        ]:
            if source.get(field) != receipt_capture.get(field):
                errors.append(f"source_receipt_{field}_mismatch")
            if source.get(field) != receipt_status.get(field):
                errors.append(f"source_status_{field}_mismatch")
        if source.get("reference_delta_boundary_preserved") is not True:
            errors.append("source_reference_delta_boundary_must_be_true")
        if receipt_capture.get("reference_delta_boundary_preserved") is not True:
            errors.append("receipt_reference_delta_boundary_must_be_true")
        if receipt_status.get("reference_delta_boundary_preserved") is not True:
            errors.append("receipt_status_reference_delta_boundary_must_be_true")
    return len(errors) == 0, errors, warnings


def render_report(case_id: str, source: dict[str, Any], reference_delta_hash: str = "") -> str:
    benchmark = "yes" if source.get("benchmark_mock") is True else "no"
    lines = [
        "# Application Number Report",
        "",
        f"Case ID: {case_id}",
        "Status: accepted_or_application_number_received",
        f"Benchmark mock: {benchmark}",
        "",
        "## Boundary",
        "",
        "This is not a real CNIPA application number when benchmark mock is yes.",
        "This is not a real acceptance notice when benchmark mock is yes.",
        "Production use requires official-system evidence, receipt consistency, package-hash consistency, docket update, and portfolio update.",
        "",
        "## Required Production Evidence",
        "",
        "- Official receipt ID, file, and hash.",
        "- Application number and official status snapshot hash.",
        "- Official file-list hash.",
        "- Final, reviewed, and submitted package hashes.",
        "- Fee/payment status and payment receipt hash when paid.",
        "- Docket entry and portfolio update.",
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


def prepare(receipt_dir: Path, source_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    receipt_root = receipt_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    receipt_path = receipt_root / "receipt-capture.yaml"
    receipt_status_path = receipt_root / "filing-status.json"
    if not all(path.exists() for path in [receipt_path, receipt_status_path]):
        raise RuntimeError("official_receipt_dir_missing_required_artifacts")

    receipt_capture = validate_receipt_capture.load_packet(receipt_path)
    receipt_status = load_json(receipt_status_path)
    source = load_json(source_path)
    reference_metadata = reference_delta_metadata(receipt_capture, receipt_status)
    if reference_metadata:
        source.update(reference_metadata)

    receipt_ok, receipt_errors, receipt_warnings = validate_receipt_capture.validate(receipt_capture, base_dir=receipt_root)
    receipt_status_ok, receipt_status_errors, receipt_status_warnings = validate_filing_status_transition.validate(receipt_status)
    source_ok, source_errors, source_warnings = validate_source_against_receipt(source, receipt_capture, receipt_status, source_base_dir=source_path.parent.resolve())

    if not all([receipt_ok, receipt_status_ok, source_ok]):
        return {
            "ok": False,
            "case_id": receipt_status.get("case_id"),
            "receipt_errors": receipt_errors,
            "receipt_status_errors": receipt_status_errors,
            "source_errors": source_errors,
            "receipt_warnings": receipt_warnings,
            "receipt_status_warnings": receipt_status_warnings,
            "source_warnings": source_warnings,
            "generator_official_system_touched": False,
            "generator_official_submission_performed": False,
        }, 1

    case_id = str(source["case_id"])
    legal_gate_mode = str(receipt_status.get("legal_gate_mode") or "")
    ai_self_filing = legal_gate_mode == "ai_self_filing_no_external_lawyer"
    source_copy_path = output_root / "application-number-source.json"
    evidence_path = output_root / "application-number-evidence.json"
    status_path = output_root / "filing-status.json"
    docket_path = output_root / "docket-entry.yaml"
    portfolio_path = output_root / "portfolio-update.json"
    report_path = output_root / "application-number-report.md"
    hashes_path = output_root / "artifact-hashes.json"

    evidence = json.loads(json.dumps(source))
    for path_key, hash_key in [
        ("official_receipt.receipt_file", "official_receipt.receipt_hash"),
        ("application.official_status_snapshot", "application.official_status_snapshot_hash"),
        ("application.official_file_list_file", "application.official_file_list_hash"),
        ("fees.payment_receipt_file", "fees.payment_receipt_hash"),
    ]:
        file_name, file_hash = copy_evidence_file(get_path(evidence, path_key), source_path.parent.resolve(), output_root)
        if file_name and file_hash:
            set_path(evidence, path_key, file_name)
            set_path(evidence, hash_key, file_hash)
    write_json(source_copy_path, evidence)
    write_json(evidence_path, evidence)

    docket = {
        "case_id": case_id,
        "docket_entry_id": get_path(source, "docket.docket_entry_id"),
        "event_type": "accepted_or_application_number_received",
        "event_date": source.get("checked_at"),
        "application_number": get_path(evidence, "application.application_number"),
        "source_evidence": "application-number-evidence.json",
        "source_hash": "see artifact-hashes.json",
        "next_deadlines": get_path(source, "docket.next_deadlines"),
    }
    render_yaml(docket_path, docket)
    portfolio = {
        "case_id": case_id,
        "family_id": get_path(source, "portfolio.family_id"),
        "application_number": get_path(source, "application.application_number"),
        "portfolio_tags": get_path(source, "portfolio.portfolio_tags"),
        "maintenance_owner": get_path(source, "portfolio.maintenance_owner"),
        "status": "pending_application",
        "benchmark_mock": source.get("benchmark_mock") is True,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    write_json(portfolio_path, portfolio)

    status = {
        "case_id": case_id,
        "previous_status": "official_receipt_received",
        "status": "accepted_or_application_number_received",
        "legal_gate": "passed",
        "official_channel_preflight": "passed",
        "approved_adapter_preflight": "passed",
        "receipt_capture": receipt_status.get("receipt_capture") or "passed",
        "official_session_authorization": receipt_status.get("official_session_authorization") or "passed",
        "official_session_authorization_hash": evidence.get("official_session_authorization_hash"),
        "official_session_reference_hash": evidence.get("official_session_reference_hash"),
        "application_number_evidence": "passed_mock" if source.get("benchmark_mock") is True else "passed",
        "decision": "application_number_received_mock_for_benchmark_only"
        if source.get("benchmark_mock") is True
        else "application_number_received",
        "final_package_hash": get_path(evidence, "package.final_package_hash"),
        "reviewed_package_hash": get_path(evidence, "package.reviewed_package_hash"),
        "official_system_touched": True,
        "official_submission_performed": True,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_application_number_acceptance_performed": False,
        "evidence_claims_application_number_received": True,
        "official_receipt_hash": get_path(evidence, "official_receipt.receipt_hash"),
        "application_number": get_path(evidence, "application.application_number"),
        "benchmark_mock": evidence.get("benchmark_mock") is True,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    if ai_self_filing:
        status["legal_gate_mode"] = legal_gate_mode
        status["ai_self_filing_gate"] = "passed"
        status["external_lawyer_involved"] = False
    if reference_metadata:
        status.update(reference_metadata)
    write_json(status_path, status)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
    report_path.write_text(render_report(case_id, source, str(reference_metadata.get("reference_patent_delta_hash") or "")), encoding="utf-8")

    write_json(
        hashes_path,
        artifact_manifest(
            output_root,
            case_id,
            [source_copy_path, evidence_path, status_path, docket_path, portfolio_path, report_path],
        ),
    )
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)

    ok = status_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "application_number_source": str(source_copy_path),
            "application_number_evidence": str(evidence_path),
            "filing_status": str(status_path),
            "docket_entry": str(docket_path),
            "portfolio_update": str(portfolio_path),
            "application_number_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "source_warnings": source_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "status": "accepted_or_application_number_received",
        "official_session_authorization_hash": evidence.get("official_session_authorization_hash"),
        "official_session_reference_hash": evidence.get("official_session_reference_hash"),
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "evidence_claims_application_number_received": True,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("official_receipt_dir", type=Path)
    parser.add_argument("application_number_source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(
            args.official_receipt_dir,
            args.application_number_source,
            args.output_dir,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "generator_official_system_touched": False,
            "generator_official_submission_performed": False,
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
