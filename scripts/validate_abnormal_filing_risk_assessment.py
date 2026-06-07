#!/usr/bin/env python3
"""Validate abnormal filing risk assessment JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_CHECK_FIELDS = [
    "check_id",
    "result",
    "evidence",
    "risk_if_ignored",
    "required_cure",
    "owner",
]
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ["case_id", "status", "decision", "gate", "risk_level", "checks"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("status") != "abnormal_filing_risk_assessed":
        errors.append("status_must_be_abnormal_filing_risk_assessed")
    if data.get("decision") != "draft_only_do_not_file_until_ai_self_filing_gate":
        errors.append("decision_must_be_draft_only_do_not_file_until_ai_self_filing_gate")
    if data.get("gate") != "G8 Non-abnormal filing check":
        errors.append("gate_must_be_g8_non_abnormal_filing_check")
    if data.get("risk_level") not in {"low", "medium", "high", "critical"}:
        errors.append("risk_level_invalid")
    if data.get("risk_level") != "low":
        errors.append("benchmark_risk_level_must_be_low")
    if data.get("filing_allowed") is not False:
        errors.append("filing_allowed_must_be_false")
    if data.get("draft_generation_allowed") is not True:
        errors.append("draft_generation_allowed_must_be_true")
    if data.get("official_system_touched") is not False:
        errors.append("official_system_touched_must_be_false")
    if data.get("official_submission_performed") is not False:
        errors.append("official_submission_performed_must_be_false")
    if data.get("external_lawyer_involved") is not False:
        errors.append("external_lawyer_involved_must_be_false")
    if data.get("errors") not in ([], None):
        errors.append("assessment_errors_must_be_empty")
    if data.get("reference_patent_delta_hash") is not None:
        if not SHA256_RE.fullmatch(str(data.get("reference_patent_delta_hash") or "")):
            errors.append("reference_patent_delta_hash_must_be_sha256_64_hex")
        if int(data.get("reference_delta_rows_count") or 0) <= 0:
            errors.append("reference_delta_rows_count_required")
        if int(data.get("reference_delta_claim_elements_count") or 0) <= 0:
            errors.append("reference_delta_claim_elements_count_required")

    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("checks_must_be_nonempty_list")
    else:
        seen: set[str] = set()
        for index, item in enumerate(checks, start=1):
            if not isinstance(item, dict):
                errors.append(f"check_{index}_must_be_object")
                continue
            for key in REQUIRED_CHECK_FIELDS:
                if is_blank(item.get(key)):
                    errors.append(f"check_{index}_missing_required_field: {key}")
            check_id = str(item.get("check_id") or "")
            if check_id in seen:
                errors.append(f"duplicate_check_id: {check_id}")
            seen.add(check_id)
            if item.get("result") not in {"pass", "warn", "fail"}:
                errors.append(f"check_{index}_result_invalid")
            if item.get("result") != "pass":
                errors.append(f"check_{index}_must_pass_for_benchmark")

    required_checks = {
        "real_inventive_activity",
        "no_random_generation",
        "no_reference_copy_or_simple_replacement",
        "technical_effects_supported",
        "not_obvious_patchwork",
        "not_unreasonable_degradation_or_nonessential_narrowing",
        "no_malicious_batch_or_duplicate_pattern",
        "inventor_applicant_consistency",
    }
    if data.get("reference_patent_delta_hash") is not None:
        required_checks.add("reference_delta_boundary_preserved")
    present = {str(item.get("check_id")) for item in checks if isinstance(item, dict)} if isinstance(checks, list) else set()
    for check_id in sorted(required_checks - present):
        errors.append(f"missing_required_check: {check_id}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("assessment", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.assessment))
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
