#!/usr/bin/env python3
"""Validate official-channel preflight before any filing action."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED_PATHS = [
    "case_id",
    "jurisdiction",
    "official_system",
    "checked_at",
    "checked_by",
    "account.owner",
    "account.role",
    "account.authorization_evidence",
    "signature.authority_holder",
    "signature.authority_evidence",
    "automation.automation_allowed",
    "automation.bypasses_access_controls",
    "package.final_package_hash",
    "package.reviewed_package_hash",
    "package.xml_validation_result",
    "package.attachment_list_hash",
    "fees.payer",
    "fees.auto_pay_authorized",
    "receipt_capture.destination",
    "receipt_capture.responsible_owner",
    "decision.status",
]


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


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")

    final_hash = get_path(data, "package.final_package_hash")
    reviewed_hash = get_path(data, "package.reviewed_package_hash")
    attachment_hash = get_path(data, "package.attachment_list_hash")
    for value, label in [
        (final_hash, "package.final_package_hash"),
        (reviewed_hash, "package.reviewed_package_hash"),
        (attachment_hash, "package.attachment_list_hash"),
    ]:
        if not is_blank(value) and not SHA256_RE.fullmatch(str(value)):
            errors.append(f"{label}_must_be_exact_sha256")
    if final_hash and reviewed_hash and final_hash != reviewed_hash:
        errors.append("hash_mismatch: package.final_package_hash != package.reviewed_package_hash")

    if get_path(data, "automation.bypasses_access_controls") is not False:
        errors.append("automation_must_not_bypass_access_controls")

    if get_path(data, "automation.automation_allowed") is not True:
        errors.append("automation_not_authorized")

    if get_path(data, "signature.human_only") is True:
        errors.append("human_only_signature_step_requires_handoff")

    if get_path(data, "fees.auto_pay_authorized") is not True:
        errors.append("fee_payment_not_authorized")

    decision = str(get_path(data, "decision.status") or "").lower()
    if decision not in {"ready_for_authorized_filing", "handoff_required", "blocked"}:
        errors.append("decision_status_invalid")
    if decision == "ready_for_authorized_filing" and errors:
        warnings.append("decision_status_overstates_readiness")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("preflight", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_packet(args.preflight))
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
