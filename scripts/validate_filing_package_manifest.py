#!/usr/bin/env python3
"""Validate a filing package manifest before official-channel preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = [
    "case_id",
    "jurisdiction",
    "filing_type",
    "package_status",
    "source_draft",
    "source_draft_hash",
    "authorization_packet",
    "authorization_packet_hash",
    "reviewed_package_hash",
    "final_package_hash",
    "documents",
    "xml_validation",
    "cross_checks",
    "next_gate",
]

REQUIRED_DOCUMENT_TYPES = {
    "claims",
    "specification",
    "abstract",
    "drawings",
    "request_metadata",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_packet(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("YAML input requires PyYAML. Use JSON or install PyYAML.") from exc
        loaded = yaml.safe_load(text)
        return loaded or {}
    raise RuntimeError("Unsupported input format. Use .json, .yaml, or .yml")


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
    if base_dir is None or is_blank(raw_path):
        return
    path = resolve_reference(raw_path, base_dir)
    if not path.exists():
        errors.append(f"{label}_file_not_found")
        return
    if expected_hash and sha256_file(path) != expected_hash:
        errors.append(f"{label}_hash_mismatch")


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    package_status = str(data.get("package_status") or "")
    if package_status not in {
        "ready_for_package_validation",
        "package_valid_official_preflight_pending",
    }:
        errors.append("package_status_must_be_ready_or_package_valid_pending_official_preflight")

    require_hash(data.get("source_draft_hash"), "source_draft_hash", errors)
    require_hash(data.get("authorization_packet_hash"), "authorization_packet_hash", errors)
    require_hash(data.get("reviewed_package_hash"), "reviewed_package_hash", errors)
    require_hash(data.get("final_package_hash"), "final_package_hash", errors)
    validate_file_hash_reference(data.get("source_draft"), data.get("source_draft_hash"), "source_draft", base_dir, errors)
    validate_file_hash_reference(data.get("authorization_packet"), data.get("authorization_packet_hash"), "authorization_packet", base_dir, errors)

    if data.get("reviewed_package_hash") and data.get("final_package_hash"):
        if data["reviewed_package_hash"] != data["final_package_hash"]:
            errors.append("hash_mismatch: reviewed_package_hash != final_package_hash")

    if data.get("official_submission_performed") is not False:
        errors.append("official_submission_performed_must_be_false")

    documents = data.get("documents")
    found_types: set[str] = set()
    if not isinstance(documents, list) or not documents:
        errors.append("missing_required_field: documents")
    else:
        for index, doc in enumerate(documents, start=1):
            if not isinstance(doc, dict):
                errors.append(f"document_{index}_must_be_object")
                continue
            doc_type = str(doc.get("type") or "")
            found_types.add(doc_type)
            for key in ["document_id", "type", "filename", "format", "hash", "validation_status"]:
                if is_blank(doc.get(key)):
                    errors.append(f"document_{index}_missing_required_field: {key}")
            require_hash(doc.get("hash"), f"document_{index}.hash", errors)
            validate_file_hash_reference(doc.get("filename"), doc.get("hash"), f"document_{index}", base_dir, errors)
            if doc.get("required") is not True:
                errors.append(f"document_{index}_must_be_required")
            if str(doc.get("validation_status") or "").lower() != "passed":
                errors.append(f"document_{index}_validation_status_must_be_passed")

    missing_doc_types = sorted(REQUIRED_DOCUMENT_TYPES - found_types)
    for doc_type in missing_doc_types:
        errors.append(f"missing_required_document_type: {doc_type}")

    xml_validation = data.get("xml_validation") if isinstance(data.get("xml_validation"), dict) else {}
    require_hash(xml_validation.get("final_xml_hash"), "xml_validation.final_xml_hash", errors)
    validate_file_hash_reference(
        xml_validation.get("final_xml_file"),
        xml_validation.get("final_xml_hash"),
        "xml_validation.final_xml",
        base_dir,
        errors,
    )
    if str(xml_validation.get("validation_result") or "").lower() != "passed":
        errors.append("xml_validation_result_must_be_passed")
    require_hash(xml_validation.get("validation_report_hash"), "xml_validation.validation_report_hash", errors)
    validate_file_hash_reference(
        xml_validation.get("validation_report"),
        xml_validation.get("validation_report_hash"),
        "xml_validation.validation_report",
        base_dir,
        errors,
    )

    cross_checks = data.get("cross_checks") if isinstance(data.get("cross_checks"), dict) else {}
    for key in [
        "final_package_hash_matches_reviewed_hash",
        "claims_hash_matches_authorization",
        "specification_hash_matches_authorization",
        "drawings_present",
        "request_metadata_present",
    ]:
        if cross_checks.get(key) is not True:
            errors.append(f"cross_check_failed: {key}")

    next_gate = data.get("next_gate") if isinstance(data.get("next_gate"), dict) else {}
    if next_gate.get("official_channel_preflight_required") is not True:
        errors.append("next_gate_official_channel_preflight_required_must_be_true")
    if next_gate.get("receipt_capture_required") is not True:
        errors.append("next_gate_receipt_capture_required_must_be_true")
    if next_gate.get("status_after_package_validation") != "package_valid_official_preflight_pending":
        errors.append("next_gate_status_after_package_validation_invalid")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_packet(args.manifest), base_dir=args.manifest.parent)
    except Exception as exc:
        ok, errors, warnings = False, [str(exc)], []

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
