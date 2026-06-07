#!/usr/bin/env python3
"""Validate an application materials quality review gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_patent_application_materials


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DIMENSION_WEIGHTS = {
    "claim_architecture": 18,
    "specification_enablement": 18,
    "abstract_and_drawings": 10,
    "evidence_binding": 18,
    "filing_readiness": 14,
    "legal_safety": 12,
    "auditability": 10,
}
EXPECTED_CHECK_IDS = {
    "claim_architecture": [
        "claims_section_present",
        "independent_claim_candidates_present",
        "dependent_claim_ladder_present",
        "numbered_independent_claim_present",
        "claim_support_rows_present",
    ],
    "specification_enablement": [
        "technical_problem_present",
        "technical_solution_present",
        "beneficial_effects_present",
        "drawings_description_present",
        "embodiments_present",
    ],
    "abstract_and_drawings": [
        "abstract_section_present",
        "abstract_solution_language_present",
        "drawings_section_present",
        "figure_reference_present",
    ],
    "evidence_binding": [
        "materials_schema_valid",
        "own_support_hashes_present",
        "prohibited_reference_hashes_recorded",
        "reference_not_used_as_support",
        "abnormal_risk_low",
    ],
    "filing_readiness": [
        "applicant_name_present",
        "inventors_present",
        "official_inventory_complete",
        "xml_validation_passed",
        "official_preflight_required",
    ],
    "legal_safety": [
        "ai_only_legal_gate_mode",
        "external_lawyer_false",
        "no_legal_advice_claimed",
        "no_lawyer_or_agent_review_claimed",
        "no_official_action_claimed",
    ],
    "auditability": [
        "final_package_hash_exact",
        "source_draft_hash_exact",
        "evidence_artifact_hash_exact",
        "abnormal_artifact_hash_exact",
        "all_generated_doc_hashes_exact",
    ],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"{label}_must_be_sha256_64_hex")


def resolve_reference(base_dir: Path, raw_path: Any) -> Path:
    path = Path(str(raw_path or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def calculated_weighted_score(dimensions: dict[str, Any]) -> float:
    total = 0.0
    total_weight = 0
    for name, weight in DIMENSION_WEIGHTS.items():
        dim = dimensions.get(name) if isinstance(dimensions.get(name), dict) else {}
        total += float(dim.get("score") or 0) * weight
        total_weight += weight
    return round((total / total_weight) * 10, 2)


def calculated_dimension_score(checks: list[Any]) -> int:
    if not checks:
        return 0
    passed = sum(1 for item in checks if isinstance(item, dict) and item.get("passed") is True)
    return int(round((passed / len(checks)) * 10))


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    base = base_dir.resolve() if base_dir else Path.cwd()

    for key in ["case_id", "reviewed_at", "review_type", "application_materials", "quality_gate", "dimensions", "next_action"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("review_type") != "application_materials_quality_gate":
        errors.append("review_type_must_be_application_materials_quality_gate")
    if data.get("official_system_touched") is not False:
        errors.append("quality_review_must_not_touch_official_system")
    if data.get("official_submission_performed") is not False:
        errors.append("quality_review_must_not_perform_official_submission")
    if data.get("external_lawyer_involved") is not False:
        errors.append("quality_review_external_lawyer_involved_must_be_false")

    app = data.get("application_materials") if isinstance(data.get("application_materials"), dict) else {}
    require_hash(app.get("hash"), "application_materials.hash", errors)
    app_path = resolve_reference(base, app.get("path"))
    if not app_path.exists():
        errors.append(f"application_materials_file_not_found: {app_path}")
    else:
        if app.get("hash") and sha256_file(app_path) != app.get("hash"):
            errors.append("application_materials_hash_mismatch")
        try:
            materials = load_json(app_path)
            ok, errs, warns = validate_patent_application_materials.validate(materials, app_path.parent)
            if not ok:
                errors.extend([f"application_materials: {item}" for item in errs])
            warnings.extend([f"application_materials: {item}" for item in warns])
            if data.get("case_id") != materials.get("case_id"):
                errors.append("quality_review_case_id_mismatch")
        except Exception as exc:
            errors.append(f"application_materials_read_failed: {exc}")

    gate = data.get("quality_gate") if isinstance(data.get("quality_gate"), dict) else {}
    if gate.get("status") != "passed":
        errors.append("quality_gate_status_must_be_passed")
    weighted_score = gate.get("weighted_score")
    minimum_score = float(gate.get("minimum_score_for_official_preflight") or 0)
    minimum_dimension_score = int(gate.get("minimum_dimension_score") or 0)
    if not isinstance(weighted_score, (int, float)):
        errors.append("quality_gate_weighted_score_must_be_number")
        weighted_score_value = 0.0
    else:
        weighted_score_value = float(weighted_score)
    if weighted_score_value < minimum_score:
        errors.append("quality_gate_score_below_official_preflight_threshold")
    if gate.get("official_preflight_allowed") is not True:
        errors.append("quality_gate_official_preflight_allowed_must_be_true")

    dimensions = data.get("dimensions") if isinstance(data.get("dimensions"), dict) else {}
    for name, weight in DIMENSION_WEIGHTS.items():
        dim = dimensions.get(name)
        if not isinstance(dim, dict):
            errors.append(f"missing_quality_dimension: {name}")
            continue
        score = dim.get("score")
        if not isinstance(score, int):
            errors.append(f"quality_dimension_{name}_score_must_be_integer")
            score_value = 0
        else:
            score_value = score
        if score_value < minimum_dimension_score:
            errors.append(f"quality_dimension_score_below_minimum: {name}")
        if dim.get("weight") != weight:
            errors.append(f"quality_dimension_weight_mismatch: {name}")
        if dim.get("passed") is not (score_value >= minimum_dimension_score):
            errors.append(f"quality_dimension_passed_flag_mismatch: {name}")
        checks = dim.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"quality_dimension_checks_missing: {name}")
        else:
            check_ids = [item.get("id") for item in checks if isinstance(item, dict)]
            expected_ids = EXPECTED_CHECK_IDS[name]
            if check_ids != expected_ids:
                errors.append(f"quality_dimension_check_ids_mismatch: {name}")
            if len(check_ids) != len(set(check_ids)):
                errors.append(f"quality_dimension_duplicate_check_id: {name}")
            if not all(isinstance(item, dict) and item.get("passed") is True for item in checks):
                errors.append(f"quality_dimension_has_failed_check: {name}")
            if score_value != calculated_dimension_score(checks):
                errors.append(f"quality_dimension_score_mismatch: {name}")

    expected_score = calculated_weighted_score(dimensions)
    if abs(weighted_score_value - expected_score) > 0.01:
        errors.append("quality_gate_weighted_score_mismatch")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("review", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        path = args.review.resolve()
        ok, errors, warnings = validate(load_json(path), path.parent)
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
