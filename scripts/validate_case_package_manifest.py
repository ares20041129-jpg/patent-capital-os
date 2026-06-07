#!/usr/bin/env python3
"""Validate a Patent Capital OS case package manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_source_material_manifest


REQUIRED_TOP_LEVEL = [
    "case_id",
    "package_id",
    "jurisdiction",
    "package_status",
    "received_at",
    "received_from",
    "intake_mode",
    "confidentiality_marker",
    "source_package_hash",
    "folders",
    "source_material_manifest",
    "source_material_manifest_hash",
    "source_files",
    "legal_gate",
    "official_actions",
    "next_action",
]

REQUIRED_FOLDERS = [
    "intake",
    "normalized",
    "draft",
    "legal",
    "filing_package",
    "official_preflight",
    "adapter",
    "receipts",
    "docket",
    "portfolio",
    "audit",
]

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, Any], root: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = root or Path.cwd()

    for key in REQUIRED_TOP_LEVEL:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("package_status") != "intake_received":
        errors.append("package_status_must_be_intake_received")

    if data.get("intake_mode") not in {"manual_upload", "email", "api", "batch_import"}:
        errors.append("intake_mode_invalid")

    require_hash(data.get("source_package_hash"), "source_package_hash", errors)
    require_hash(data.get("source_material_manifest_hash"), "source_material_manifest_hash", errors)

    folders = data.get("folders") if isinstance(data.get("folders"), dict) else {}
    for key in REQUIRED_FOLDERS:
        rel = folders.get(key)
        if is_blank(rel):
            errors.append(f"missing_required_folder: {key}")
            continue
        path = root / str(rel)
        if not path.exists() or not path.is_dir():
            errors.append(f"folder_missing_or_not_directory: {key}")

    source_manifest_rel = data.get("source_material_manifest")
    if not is_blank(source_manifest_rel):
        source_manifest_path = root / str(source_manifest_rel)
        if not source_manifest_path.exists():
            errors.append("source_material_manifest_file_missing")
        else:
            actual_hash = file_hash(source_manifest_path)
            if actual_hash != data.get("source_material_manifest_hash"):
                errors.append("source_material_manifest_hash_mismatch")
            ok, errs, warns = validate_source_material_manifest.validate(
                validate_source_material_manifest.load_packet(source_manifest_path),
                base_dir=root,
            )
            if not ok:
                errors.extend([f"source_material_manifest: {item}" for item in errs])
            warnings.extend([f"source_material_manifest: {item}" for item in warns])

    source_files = data.get("source_files")
    if not isinstance(source_files, list) or not source_files:
        errors.append("source_files_must_be_nonempty_list")
    else:
        seen_ids: set[str] = set()
        for index, item in enumerate(source_files, start=1):
            if not isinstance(item, dict):
                errors.append(f"source_file_{index}_must_be_object")
                continue
            for key in [
                "material_id",
                "relative_path",
                "filename",
                "type",
                "sha256",
                "bytes",
                "source_owner",
                "confidentiality",
            ]:
                if is_blank(item.get(key)):
                    errors.append(f"source_file_{index}_missing_required_field: {key}")
            material_id = str(item.get("material_id") or "")
            if material_id in seen_ids:
                errors.append(f"duplicate_material_id: {material_id}")
            seen_ids.add(material_id)
            require_hash(item.get("sha256"), f"source_file_{index}.sha256", errors)
            rel = item.get("relative_path")
            if rel:
                file_path = root / str(rel)
                if not file_path.exists():
                    errors.append(f"source_file_{index}_missing_file")
                else:
                    actual_hash = file_hash(file_path)
                    if actual_hash != item.get("sha256"):
                        errors.append(f"source_file_{index}_hash_mismatch")
                    if item.get("bytes") != file_path.stat().st_size:
                        errors.append(f"source_file_{index}_byte_count_mismatch")
            if item.get("usable_for_claim_support") is not True:
                warnings.append(f"source_file_{index}_not_marked_usable_for_claim_support")

    legal_gate = data.get("legal_gate") if isinstance(data.get("legal_gate"), dict) else {}
    if legal_gate.get("status") not in {"pending", "failed", "passed"}:
        errors.append("legal_gate.status_invalid")
    if legal_gate.get("filing_allowed") is not False:
        errors.append("intake_package_must_not_allow_filing")
    if legal_gate.get("status") == "passed":
        warnings.append("intake_package_legal_gate_passed_unusual")

    official_actions = data.get("official_actions") if isinstance(data.get("official_actions"), dict) else {}
    for key in [
        "official_system_touched",
        "official_submission_performed",
        "receipt_captured",
        "application_number_received",
    ]:
        if official_actions.get(key) is not False:
            errors.append(f"official_action_must_be_false_at_intake: {key}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        manifest_path = args.manifest.resolve()
        ok, errors, warnings = validate(load_json(manifest_path), root=manifest_path.parent)
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
