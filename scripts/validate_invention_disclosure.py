#!/usr/bin/env python3
"""Validate invention disclosure inputs before patent draft generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_PATHS = [
    "case_id",
    "title",
    "business_goal",
    "applicant_context.applicant_name",
    "applicant_context.actual_r_and_d_basis",
    "inventor_input.inventors",
    "inventor_input.contribution_confirmed",
    "technical_problem",
    "technical_solution.required_features",
    "technical_effects",
    "embodiments",
    "known_prior_art",
    "similarity_control.no_copying_or_synonym_substitution_confirmed",
    "similarity_control.real_technical_contribution_summary",
    "data_and_evidence.source_hashes",
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

    if get_path(data, "inventor_input.contribution_confirmed") is not True:
        errors.append("inventor_contribution_not_confirmed")

    if get_path(data, "similarity_control.no_copying_or_synonym_substitution_confirmed") is not True:
        errors.append("similarity_control_copying_risk_unresolved")

    effects = get_path(data, "technical_effects")
    if isinstance(effects, list):
        for index, effect in enumerate(effects):
            if not isinstance(effect, dict) or is_blank(effect.get("effect")) or is_blank(effect.get("evidence")):
                errors.append(f"technical_effect_missing_evidence: index={index}")

    basis = str(get_path(data, "applicant_context.actual_r_and_d_basis") or "").lower()
    contribution = str(get_path(data, "similarity_control.real_technical_contribution_summary") or "").lower()
    if "random" in basis or "generate many" in contribution or "synonym" in contribution:
        errors.append("anti_abnormal_risk: disclosure suggests random or synonym-substitution generation")

    foreign_planned = get_path(data, "secrecy.foreign_or_pct_planned")
    china_completed = get_path(data, "secrecy.invention_completed_in_china")
    secrecy_status = str(get_path(data, "secrecy.secrecy_review_status") or "").lower()
    if foreign_planned is True and china_completed is True and secrecy_status not in {
        "completed",
        "not_required",
        "cleared",
        "\u5df2\u5b8c\u6210",
        "\u4e0d\u9700\u8981",
    }:
        errors.append("secrecy_review_unresolved_for_foreign_or_pct_plan")

    prototypes = get_path(data, "data_and_evidence.prototypes")
    experiments = get_path(data, "data_and_evidence.experiments")
    logs = get_path(data, "data_and_evidence.logs_or_measurements")
    if is_blank(prototypes) and is_blank(experiments) and is_blank(logs):
        warnings.append("no prototype, experiment, or measurement evidence listed")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("disclosure", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    try:
        data = load_packet(args.disclosure)
        ok, errors, warnings = validate(data)
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
