#!/usr/bin/env python3
"""Validate receipt capture artifacts for filing workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


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


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


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
    data: dict[str, Any],
    path_key: str,
    hash_key: str,
    label: str,
    base_dir: Path | None,
    errors: list[str],
) -> None:
    raw_path = get_path(data, path_key)
    if base_dir is None or is_blank(raw_path):
        return
    path = resolve_reference(raw_path, base_dir)
    if not path.exists():
        errors.append(f"{label}_file_not_found")
        return
    if get_path(data, hash_key) and sha256_file(path) != get_path(data, hash_key):
        errors.append(f"{label}_hash_mismatch")


def validate(data: dict[str, Any], allow_plan_only: bool = False, base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ["case_id", "filing_action_id", "status", "official_system"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    status = str(data.get("status") or "").lower()
    if status not in {"planned", "submitted_pending_receipt", "official_receipt_received"}:
        errors.append("receipt_status_invalid")

    if allow_plan_only and status == "planned":
        if not get_path(data, "docket.next_deadlines"):
            warnings.append("planned_receipt_capture_has_no_next_deadlines")
        return len(errors) == 0, errors, warnings

    if status in {"submitted_pending_receipt", "official_receipt_received"}:
        if is_blank(data.get("submitted_at")):
            errors.append("missing_required_field: submitted_at")
        for path in ["official_session_authorization_hash", "official_session_reference_hash"]:
            if not is_blank(data.get(path)):
                require_hash(data.get(path), path, errors)

    if status == "submitted_pending_receipt":
        if not get_path(data, "docket.docket_entry_id"):
            warnings.append("docket_entry_id_missing_while_receipt_pending")
        return len(errors) == 0, errors, warnings

    if status == "official_receipt_received":
        for path in [
            "official_receipt.receipt_id",
            "official_receipt.receipt_file",
            "official_session_authorization_hash",
            "official_session_reference_hash",
            "application.filing_date",
            "application.official_file_list_hash",
            "fees.payment_status",
            "docket.docket_entry_id",
        ]:
            if is_blank(get_path(data, path)):
                errors.append(f"missing_required_field: {path}")
        require_hash(get_path(data, "official_receipt.receipt_hash"), "official_receipt.receipt_hash", errors)
        require_hash(data.get("official_session_authorization_hash"), "official_session_authorization_hash", errors)
        require_hash(data.get("official_session_reference_hash"), "official_session_reference_hash", errors)
        require_hash(get_path(data, "application.official_file_list_hash"), "application.official_file_list_hash", errors)
        validate_file_hash_reference(
            data,
            "official_receipt.receipt_file",
            "official_receipt.receipt_hash",
            "official_receipt",
            base_dir,
            errors,
        )
        payment_status = str(get_path(data, "fees.payment_status") or "").lower()
        if payment_status not in {"paid", "pending", "not_due", "deferred"}:
            errors.append("fees.payment_status_invalid")
        payment_hash = get_path(data, "fees.payment_receipt_hash")
        if payment_status == "paid":
            require_hash(payment_hash, "fees.payment_receipt_hash", errors)
            validate_file_hash_reference(
                data,
                "fees.payment_receipt_file",
                "fees.payment_receipt_hash",
                "fees.payment_receipt",
                base_dir,
                errors,
            )
        if is_blank(get_path(data, "application.application_number")):
            warnings.append("application_number_missing_even_though_receipt_received")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt_capture", type=Path)
    parser.add_argument("--allow-plan-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_packet(args.receipt_capture), allow_plan_only=args.allow_plan_only, base_dir=args.receipt_capture.parent)
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
