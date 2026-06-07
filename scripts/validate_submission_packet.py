#!/usr/bin/env python3
"""Validate a Patent Capital OS submission authorization packet.

Input can be JSON. YAML is supported when PyYAML is installed.
The script performs deterministic filing-readiness checks; it does not provide legal advice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_PATHS = [
    "case_id",
    "filing_type",
    "jurisdiction",
    "final_documents.claims",
    "final_documents.specification",
    "final_documents.abstract",
    "final_documents.drawings",
    "final_documents.request_metadata",
    "hashes.source_package",
    "hashes.final_claims",
    "hashes.final_specification",
    "hashes.final_xml",
    "counsel_review.reviewer_name",
    "counsel_review.reviewer_role",
    "counsel_review.organization",
    "counsel_review.approval_statement",
    "counsel_review.reviewed_hash",
    "counsel_review.timestamp",
    "applicant_authorization.applicant_name",
    "applicant_authorization.authorized_person",
    "applicant_authorization.authority_basis",
    "applicant_authorization.allowed_actions",
    "applicant_authorization.timestamp",
    "inventor_confirmation.inventors",
    "inventor_confirmation.contribution_confirmed",
    "ownership.basis",
    "ownership.evidence",
    "secrecy_review.status",
    "agency.agent_or_firm",
    "agency.appointment_evidence",
    "filing_channel.official_system",
    "filing_channel.account_owner",
    "filing_channel.signature_authority",
    "fees.payer",
    "fees.fee_reduction",
    "fees.auto_pay_authorized",
]

HASH_PATHS = [
    "hashes.source_package",
    "hashes.final_claims",
    "hashes.final_specification",
    "hashes.final_xml",
    "counsel_review.reviewed_hash",
]

OPTIONAL_DOCUMENT_HASHES = {
    "claims": "hashes.final_claims",
    "specification": "hashes.final_specification",
    "abstract": "hashes.final_abstract",
    "drawings": "hashes.final_drawings",
    "request_metadata": "hashes.request_metadata",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_packet(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)

    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "YAML input requires PyYAML. Re-run with JSON or install PyYAML."
            ) from exc
        loaded = yaml.safe_load(text)
        return loaded or {}

    raise RuntimeError("Unsupported input format. Use .json, .yaml, or .yml")


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


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_reference(reference: Any, base_dir: Path) -> Path:
    path = Path(str(reference or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def validate_file_hash_reference(
    raw_path: Any,
    expected_hash: Any,
    label: str,
    base_dir: Path | None,
    errors: list[str],
) -> None:
    if base_dir is None or is_blank(raw_path) or is_blank(expected_hash):
        return
    path = resolve_reference(raw_path, base_dir)
    if not path.exists():
        errors.append(f"{label}_file_not_found")
        return
    if sha256_file(path) != expected_hash:
        errors.append(f"{label}_hash_mismatch")


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")
    for path in HASH_PATHS:
        require_hash(get_path(data, path), path, errors)
    for doc_type, hash_path in OPTIONAL_DOCUMENT_HASHES.items():
        value = get_path(data, hash_path)
        if not is_blank(value):
            require_hash(value, hash_path, errors)
        validate_file_hash_reference(
            get_path(data, f"final_documents.{doc_type}"),
            value,
            f"final_documents.{doc_type}",
            base_dir,
            errors,
        )

    if get_path(data, "inventor_confirmation.contribution_confirmed") is not True:
        errors.append("inventor_contribution_not_confirmed")

    reviewed_hash = get_path(data, "counsel_review.reviewed_hash")
    source_hash = get_path(data, "hashes.source_package")
    if reviewed_hash and source_hash and reviewed_hash != source_hash:
        errors.append("hash_mismatch: counsel_review.reviewed_hash != hashes.source_package")

    allowed_actions = get_path(data, "applicant_authorization.allowed_actions")
    if isinstance(allowed_actions, str):
        normalized = allowed_actions.lower()
        if "file" not in normalized and "submit" not in normalized and "\u63d0\u4ea4" not in allowed_actions:
            errors.append("authorization_scope_missing_submit_or_file")
    elif isinstance(allowed_actions, list):
        joined = " ".join(str(item).lower() for item in allowed_actions)
        if "file" not in joined and "submit" not in joined and "\u63d0\u4ea4" not in joined:
            errors.append("authorization_scope_missing_submit_or_file")
    else:
        errors.append("authorization_scope_missing_submit_or_file")

    secrecy_status = str(get_path(data, "secrecy_review.status") or "").lower()
    foreign_planned = get_path(data, "secrecy_review.foreign_or_pct_planned")
    china_completed = get_path(data, "secrecy_review.china_completed")
    if foreign_planned is True and china_completed is True and secrecy_status not in {
        "completed",
        "not_required",
        "cleared",
        "\u5df2\u5b8c\u6210",
        "\u4e0d\u9700\u8981",
    }:
        errors.append("secrecy_review_unresolved_for_foreign_or_pct_plan")

    auto_pay = get_path(data, "fees.auto_pay_authorized")
    if auto_pay is not True:
        errors.append("fees_auto_pay_not_authorized_for_filing_mode")

    final_xml = get_path(data, "hashes.final_xml")
    if not final_xml and "missing_required_field: hashes.final_xml" not in errors:
        errors.append("missing_required_field: hashes.final_xml")

    jurisdiction = str(get_path(data, "jurisdiction") or "").upper()
    official_system = str(get_path(data, "filing_channel.official_system") or "").lower()
    if official_system and jurisdiction == "CN" and "cnipa" not in official_system and "\u56fd\u77e5\u5c40" not in official_system:
        errors.append("cn_filing_channel_must_identify_cnipa_system")

    automation_allowed = get_path(data, "filing_channel.automation_allowed")
    if automation_allowed is False:
        warnings.append("filing_channel.automation_allowed is false; produce human handoff")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path, help="Submission packet JSON/YAML file")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    try:
        data = load_packet(args.packet)
        ok, errors, warnings = validate(data, base_dir=args.packet.parent)
    except Exception as exc:
        if args.json:
            print(json.dumps({"ok": False, "errors": [str(exc)], "warnings": []}, ensure_ascii=False))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {"ok": ok, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if ok else "FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
