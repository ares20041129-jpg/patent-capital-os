#!/usr/bin/env python3
"""Prepare receipt-capture artifacts from independently supplied receipt evidence."""

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
    "previous_status",
    "filing_action_id",
    "submitted_at",
    "official_system",
    "official_session_authorization_hash",
    "official_session_reference_hash",
    "official_receipt.receipt_id",
    "official_receipt.receipt_file",
    "official_receipt.receipt_hash",
    "application.filing_date",
    "application.official_file_list_hash",
    "fees.payment_status",
    "docket.docket_entry_id",
    "docket.next_deadlines",
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


def validate_source(
    source: dict[str, Any],
    execution_result: dict[str, Any],
    submitted_status: dict[str, Any],
    pending_receipt: dict[str, Any],
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_SOURCE_PATHS:
        if is_blank(get_path(source, path)):
            errors.append(f"missing_required_field: {path}")

    forbidden = has_forbidden_key(source)
    if forbidden:
        errors.append(f"forbidden_field_present: {forbidden}")

    case_id = str(execution_result.get("case_id") or submitted_status.get("case_id") or "")
    if source.get("case_id") != case_id or pending_receipt.get("case_id") != case_id:
        errors.append("case_id_mismatch")
    if source.get("previous_status") != "submitted_pending_receipt":
        errors.append("previous_status_must_be_submitted_pending_receipt")
    if submitted_status.get("status") != "submitted_pending_receipt":
        errors.append("input_status_must_be_submitted_pending_receipt")
    if source.get("filing_action_id") != get_path(execution_result, "official_submission_evidence.submission_reference"):
        errors.append("filing_action_id_mismatch")
    if source.get("filing_action_id") != pending_receipt.get("filing_action_id"):
        errors.append("pending_receipt_filing_action_id_mismatch")
    if source.get("official_system") != execution_result.get("official_system"):
        errors.append("official_system_mismatch")
    execution_session_authorization_hash = execution_result.get("official_session_authorization_hash")
    status_session_authorization_hash = submitted_status.get("official_session_authorization_hash")
    pending_session_authorization_hash = pending_receipt.get("official_session_authorization_hash")
    source_session_authorization_hash = source.get("official_session_authorization_hash")
    execution_session_reference_hash = execution_result.get("official_session_reference_hash")
    status_session_reference_hash = submitted_status.get("official_session_reference_hash")
    pending_session_reference_hash = pending_receipt.get("official_session_reference_hash")
    source_session_reference_hash = source.get("official_session_reference_hash")
    for value, label in [
        (execution_session_authorization_hash, "execution_result.official_session_authorization_hash"),
        (status_session_authorization_hash, "submitted_status.official_session_authorization_hash"),
        (pending_session_authorization_hash, "pending_receipt.official_session_authorization_hash"),
        (source_session_authorization_hash, "source.official_session_authorization_hash"),
        (execution_session_reference_hash, "execution_result.official_session_reference_hash"),
        (status_session_reference_hash, "submitted_status.official_session_reference_hash"),
        (pending_session_reference_hash, "pending_receipt.official_session_reference_hash"),
        (source_session_reference_hash, "source.official_session_reference_hash"),
    ]:
        require_hash(value, label, errors)
    if source_session_authorization_hash and execution_session_authorization_hash and source_session_authorization_hash != execution_session_authorization_hash:
        errors.append("source_execution_session_authorization_hash_mismatch")
    if source_session_authorization_hash and status_session_authorization_hash and source_session_authorization_hash != status_session_authorization_hash:
        errors.append("source_status_session_authorization_hash_mismatch")
    if source_session_authorization_hash and pending_session_authorization_hash and source_session_authorization_hash != pending_session_authorization_hash:
        errors.append("source_pending_receipt_session_authorization_hash_mismatch")
    if source_session_reference_hash and execution_session_reference_hash and source_session_reference_hash != execution_session_reference_hash:
        errors.append("source_execution_session_reference_hash_mismatch")
    if source_session_reference_hash and status_session_reference_hash and source_session_reference_hash != status_session_reference_hash:
        errors.append("source_status_session_reference_hash_mismatch")
    if source_session_reference_hash and pending_session_reference_hash and source_session_reference_hash != pending_session_reference_hash:
        errors.append("source_pending_receipt_session_reference_hash_mismatch")
    if get_path(source, "decision.status") != "official_receipt_received":
        errors.append("decision_status_must_be_official_receipt_received")
    require_hash(get_path(source, "official_receipt.receipt_hash"), "official_receipt.receipt_hash", errors)
    require_hash(get_path(source, "application.official_file_list_hash"), "application.official_file_list_hash", errors)
    payment_status = str(get_path(source, "fees.payment_status") or "").lower()
    if payment_status not in {"paid", "pending", "not_due", "deferred"}:
        errors.append("fees.payment_status_invalid")
    if payment_status == "paid":
        require_hash(get_path(source, "fees.payment_receipt_hash"), "fees.payment_receipt_hash", errors)
    if source.get("benchmark_mock") is True:
        warnings.append("benchmark_mock_not_real_official_receipt")
    return len(errors) == 0, errors, warnings


def render_report(case_id: str, source: dict[str, Any], reference_delta_hash: str = "") -> str:
    benchmark = "yes" if source.get("benchmark_mock") is True else "no"
    app_number = get_path(source, "application.application_number") or ""
    lines = [
        "# Receipt Capture Report",
        "",
        f"Case ID: {case_id}",
        "Status: official_receipt_received",
        f"Benchmark mock: {benchmark}",
        f"Application number in receipt: {'yes' if app_number else 'no'}",
        "",
        "## Boundary",
        "",
        "This is not a real CNIPA receipt when benchmark mock is yes.",
        "It is not a real filing unless tied to a lawful official submission and official receipt evidence.",
        "It is not an accepted/application-number status until application-number evidence validates separately.",
        "",
        "## Evidence Required In Production",
        "",
        "- Official receipt file and hash.",
        "- Official file list hash.",
        "- Filing timestamp.",
        "- Fee/payment receipt when paid.",
        "- Docket entry and next deadlines.",
        "- Application number only if issued by the official system.",
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


def prepare(submitted_dir: Path, source_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    submitted_root = submitted_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    execution_path = submitted_root / "adapter-execution-result.json"
    submitted_status_path = submitted_root / "filing-status.json"
    pending_receipt_path = submitted_root / "receipt-capture-pending.yaml"
    if not all(path.exists() for path in [execution_path, submitted_status_path, pending_receipt_path]):
        raise RuntimeError("submitted_pending_receipt_dir_missing_required_artifacts")

    execution_result = load_json(execution_path)
    submitted_status = load_json(submitted_status_path)
    pending_receipt = validate_receipt_capture.load_packet(pending_receipt_path)
    source = load_json(source_path)

    execution_ok, execution_errors, execution_warnings = validate_adapter_execution_result.validate(execution_result, base_dir=submitted_root)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(submitted_status)
    pending_ok, pending_errors, pending_warnings = validate_receipt_capture.validate(pending_receipt, base_dir=submitted_root)
    source_ok, source_errors, source_warnings = validate_source(source, execution_result, submitted_status, pending_receipt)

    if not all([execution_ok, status_ok, pending_ok, source_ok]):
        return {
            "ok": False,
            "case_id": execution_result.get("case_id"),
            "execution_errors": execution_errors,
            "status_errors": status_errors,
            "pending_receipt_errors": pending_errors,
            "source_errors": source_errors,
            "execution_warnings": execution_warnings,
            "status_warnings": status_warnings,
            "pending_receipt_warnings": pending_warnings,
            "source_warnings": source_warnings,
            "generator_official_system_touched": False,
            "generator_official_submission_performed": False,
        }, 1

    case_id = str(execution_result["case_id"])
    legal_gate_mode = str(submitted_status.get("legal_gate_mode") or execution_result.get("legal_gate_mode") or "")
    ai_self_filing = legal_gate_mode == "ai_self_filing_no_external_lawyer"
    reference_metadata = reference_delta_metadata(execution_result, submitted_status)
    if reference_metadata:
        source.update(reference_metadata)
    source_copy_path = output_root / "receipt-capture-source.json"
    receipt_path = output_root / "receipt-capture.yaml"
    status_path = output_root / "filing-status.json"
    report_path = output_root / "receipt-report.md"
    hashes_path = output_root / "artifact-hashes.json"

    write_json(source_copy_path, source)
    receipt_file, receipt_hash = copy_evidence_file(
        get_path(source, "official_receipt.receipt_file"),
        source_path.parent.resolve(),
        output_root,
    )
    payment_file, payment_hash = copy_evidence_file(
        get_path(source, "fees.payment_receipt_file"),
        source_path.parent.resolve(),
        output_root,
    )
    source_receipt = dict(source.get("official_receipt") or {})
    if receipt_file and receipt_hash:
        source_receipt["receipt_file"] = receipt_file
        source_receipt["receipt_hash"] = receipt_hash
    source_fees = dict(source.get("fees") or {})
    if payment_file and payment_hash:
        source_fees["payment_receipt_file"] = payment_file
        source_fees["payment_receipt_hash"] = payment_hash
    receipt_capture = {
        "case_id": case_id,
        "filing_action_id": source.get("filing_action_id"),
        "status": "official_receipt_received",
        "submitted_at": source.get("submitted_at"),
        "official_system": source.get("official_system"),
        "official_session_authorization_hash": source.get("official_session_authorization_hash"),
        "official_session_reference_hash": source.get("official_session_reference_hash"),
        "official_receipt": source_receipt,
        "application": source.get("application"),
        "fees": source_fees,
        "docket": source.get("docket"),
        "evidence_notes": source.get("evidence_notes"),
    }
    if reference_metadata:
        receipt_capture.update(reference_metadata)
    render_yaml(receipt_path, receipt_capture)
    receipt_ok, receipt_errors, receipt_warnings = validate_receipt_capture.validate(
        validate_receipt_capture.load_packet(receipt_path),
        base_dir=output_root,
    )

    status = {
        "case_id": case_id,
        "previous_status": "submitted_pending_receipt",
        "status": "official_receipt_received",
        "legal_gate": "passed",
        "package_validation": "passed",
        "official_channel_preflight": "passed",
        "approved_adapter_preflight": "passed",
        "adapter_execution": submitted_status.get("adapter_execution") or "performed",
        "official_session_authorization": submitted_status.get("official_session_authorization") or "passed",
        "official_session_authorization_hash": source.get("official_session_authorization_hash"),
        "official_session_reference_hash": source.get("official_session_reference_hash"),
        "receipt_capture": "passed_mock" if source.get("benchmark_mock") is True else "passed",
        "failed_gates": [],
        "decision": "mock_receipt_captured_for_benchmark_only"
        if source.get("benchmark_mock") is True
        else "official_receipt_received",
        "final_package_hash": execution_result.get("final_package_hash"),
        "reviewed_package_hash": execution_result.get("reviewed_package_hash"),
        "official_receipt_hash": get_path(receipt_capture, "official_receipt.receipt_hash"),
        "application_number": get_path(source, "application.application_number") or "",
        "official_system_touched": True,
        "official_submission_performed": True,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_official_receipt_capture_performed": False,
        "evidence_claims_official_receipt_received": True,
        "benchmark_mock": source.get("benchmark_mock") is True,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    if ai_self_filing:
        status["legal_gate_mode"] = legal_gate_mode
        status["ai_self_filing_gate"] = "passed"
        status["external_lawyer_involved"] = False
    if reference_metadata:
        status.update(reference_metadata)
    write_json(status_path, status)
    status_out_ok, status_out_errors, status_out_warnings = validate_filing_status_transition.validate(status)
    report_path.write_text(render_report(case_id, source, str(reference_metadata.get("reference_patent_delta_hash") or "")), encoding="utf-8")

    evidence_files = [source_copy_path, receipt_path, status_path, report_path]
    if receipt_file:
        evidence_files.append(output_root / receipt_file)
    if payment_file:
        evidence_files.append(output_root / payment_file)
    write_json(
        hashes_path,
        artifact_manifest(
            output_root,
            case_id,
            [path for path in evidence_files if path.exists()],
        ),
    )
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)

    ok = receipt_ok and status_out_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "receipt_capture_source": str(source_copy_path),
            "receipt_capture": str(receipt_path),
            "filing_status": str(status_path),
            "receipt_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "source_warnings": source_warnings,
        "receipt_errors": receipt_errors,
        "receipt_warnings": receipt_warnings,
        "status_errors": status_out_errors,
        "status_warnings": status_out_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "status": "official_receipt_received",
        "official_session_authorization_hash": source.get("official_session_authorization_hash"),
        "official_session_reference_hash": source.get("official_session_reference_hash"),
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "evidence_claims_official_receipt_received": True,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("submitted_pending_receipt_dir", type=Path)
    parser.add_argument("receipt_capture_source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(
            args.submitted_pending_receipt_dir,
            args.receipt_capture_source,
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
