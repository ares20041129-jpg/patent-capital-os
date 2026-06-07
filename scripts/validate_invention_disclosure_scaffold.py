#!/usr/bin/env python3
"""Validate an invention disclosure scaffold before full disclosure confirmation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = [
    "case_id",
    "disclosure_status",
    "legal_gate_mode",
    "external_lawyer_involved",
    "normalized_at",
    "source_material_manifest",
    "source_package_hash",
    "invention_disclosure",
    "scaffold_controls",
]

REQUIRED_DISCLOSURE_PATHS = [
    "case_id",
    "title",
    "business_goal",
    "applicant_context.actual_r_and_d_basis",
    "technical_problem",
    "technical_solution.required_features",
    "data_and_evidence.source_hashes",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    elif not str(value).startswith("sha256:"):
        errors.append(f"{label}_must_start_with_sha256")


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("disclosure_status") != "scaffold_pending_confirmation":
        errors.append("disclosure_status_must_be_scaffold_pending_confirmation")

    if data.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("legal_gate_mode_must_be_ai_self_filing_no_external_lawyer")

    if data.get("external_lawyer_involved") is not False:
        errors.append("external_lawyer_involved_must_be_false")

    require_hash(data.get("source_package_hash"), "source_package_hash", errors)

    disclosure = data.get("invention_disclosure") if isinstance(data.get("invention_disclosure"), dict) else {}
    for path in REQUIRED_DISCLOSURE_PATHS:
        if is_blank(get_path(disclosure, path)):
            errors.append(f"invention_disclosure_missing_required_field: {path}")

    if is_blank(get_path(disclosure, "ai_legal_compliance_questions")):
        errors.append("invention_disclosure_missing_required_field: ai_legal_compliance_questions")
    if not is_blank(get_path(disclosure, "counsel_questions")):
        errors.append("scaffold_must_not_default_to_counsel_questions")

    source_hashes = get_path(disclosure, "data_and_evidence.source_hashes")
    if isinstance(source_hashes, list):
        for index, value in enumerate(source_hashes, start=1):
            require_hash(value, f"invention_disclosure.data_and_evidence.source_hashes[{index}]", errors)
    else:
        errors.append("source_hashes_must_be_list")

    if get_path(disclosure, "inventor_input.contribution_confirmed") is True:
        errors.append("scaffold_must_not_confirm_inventor_contribution")

    if get_path(disclosure, "similarity_control.no_copying_or_synonym_substitution_confirmed") is True:
        errors.append("scaffold_must_not_confirm_no_copying")

    controls = data.get("scaffold_controls") if isinstance(data.get("scaffold_controls"), dict) else {}
    for key in [
        "inventor_confirmation_pending",
        "legal_gate_pending",
        "no_copying_confirmation_pending",
    ]:
        if controls.get(key) is not True:
            errors.append(f"scaffold_control_must_be_true: {key}")
    if controls.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("scaffold_control_legal_gate_mode_must_be_ai_self_filing_no_external_lawyer")
    if controls.get("external_lawyer_involved") is not False:
        errors.append("scaffold_control_external_lawyer_involved_must_be_false")
    for key in ["filing_allowed", "draft_generation_allowed"]:
        if controls.get(key) is not False:
            errors.append(f"scaffold_control_must_be_false: {key}")

    if not get_path(disclosure, "known_prior_art"):
        warnings.append("known_prior_art_missing_or_not_extracted")

    if not get_path(disclosure, "technical_effects"):
        warnings.append("technical_effects_pending_confirmation")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scaffold", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.scaffold))
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
