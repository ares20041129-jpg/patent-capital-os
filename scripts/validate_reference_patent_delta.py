#!/usr/bin/env python3
"""Validate a reference-patent delta and claim strategy package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CN_PUBLICATION_RE = re.compile(r"^CN[0-9]{8,12}[A-Z]?$")
RISK_VALUES = {"low", "medium", "high", "unknown"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def exact_hash(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def resolve_reference(base_dir: Path, raw_path: Any) -> Path:
    path = Path(str(raw_path or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def stays_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def require_false(data: dict[str, Any], key: str, errors: list[str]) -> None:
    if data.get(key) is not False:
        errors.append(f"{key}_must_be_false")


def validate_support_file(base: Path, item: dict[str, Any], label: str, errors: list[str]) -> None:
    raw_path = item.get("support_path")
    if is_blank(raw_path):
        errors.append(f"{label}_support_path_missing")
        return
    path_text = str(raw_path).replace("\\", "/").lower()
    if "prior-art" in path_text or "reference" in path_text or "patent" in path_text:
        errors.append(f"{label}_support_must_not_be_reference_material")
    path = resolve_reference(base, raw_path)
    if not stays_inside(path, base):
        errors.append(f"{label}_support_path_must_stay_inside_package")
        return
    if not path.exists() or not path.is_file():
        errors.append(f"{label}_support_file_missing: {path}")
        return
    if not exact_hash(item.get("support_hash")):
        errors.append(f"{label}_support_hash_must_be_sha256_64_hex")
    elif sha256_file(path) != item.get("support_hash"):
        errors.append(f"{label}_support_hash_mismatch")


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    base = base_dir.resolve() if base_dir else Path.cwd()

    for key in ["case_id", "created_at", "delta_type", "status", "decision", "reference_patents", "claim_elements", "delta_rows", "controls", "next_action"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("delta_type") != "reference_patent_delta_claim_strategy":
        errors.append("delta_type_must_be_reference_patent_delta_claim_strategy")
    if data.get("status") != "reference_delta_ready_for_draft_strategy":
        errors.append("status_must_be_reference_delta_ready_for_draft_strategy")
    if data.get("decision") != "use_references_as_boundary_not_claim_support":
        errors.append("decision_must_use_references_as_boundary")
    if data.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("legal_gate_mode_must_be_ai_self_filing_no_external_lawyer")
    require_false(data, "official_system_touched", errors)
    require_false(data, "official_submission_performed", errors)
    require_false(data, "external_lawyer_involved", errors)

    controls = data.get("controls") if isinstance(data.get("controls"), dict) else {}
    if controls.get("reference_patents_used_as_boundary_only") is not True:
        errors.append("reference_patents_used_as_boundary_only_must_be_true")
    for key in [
        "reference_patents_used_as_applicant_claim_support",
        "novelty_guarantee_claimed",
        "patentability_guarantee_claimed",
        "legal_advice_claimed",
        "lawyer_or_agent_review_claimed",
        "filing_authorized",
    ]:
        if controls.get(key) is not False:
            errors.append(f"control_{key}_must_be_false")

    source = data.get("source_input") if isinstance(data.get("source_input"), dict) else {}
    if source:
        source_path = resolve_reference(base, source.get("path"))
        if not source_path.exists():
            errors.append(f"source_input_file_missing: {source_path}")
        elif not exact_hash(source.get("hash")):
            errors.append("source_input_hash_must_be_sha256_64_hex")
        elif sha256_file(source_path) != source.get("hash"):
            errors.append("source_input_hash_mismatch")

    references = data.get("reference_patents") if isinstance(data.get("reference_patents"), list) else []
    if len(references) < 3:
        errors.append("reference_patents_must_include_at_least_3_items")
    seen_refs: set[str] = set()
    for index, ref in enumerate(references, start=1):
        if not isinstance(ref, dict):
            errors.append(f"reference_{index}_must_be_object")
            continue
        publication = str(ref.get("publication") or "")
        if not CN_PUBLICATION_RE.fullmatch(publication):
            errors.append(f"reference_{index}_publication_must_be_cn_publication")
        if publication in seen_refs:
            errors.append(f"duplicate_reference_publication: {publication}")
        seen_refs.add(publication)
        if is_blank(ref.get("title")):
            errors.append(f"reference_{index}_title_missing")
        if str(ref.get("role") or "") not in {"closest_prior_art", "background_reference", "risk_reference"}:
            errors.append(f"reference_{index}_role_invalid")

    claim_elements = data.get("claim_elements") if isinstance(data.get("claim_elements"), list) else []
    element_ids: set[str] = set()
    for index, element in enumerate(claim_elements, start=1):
        if not isinstance(element, dict):
            errors.append(f"claim_element_{index}_must_be_object")
            continue
        element_id = str(element.get("element_id") or "")
        if is_blank(element_id):
            errors.append(f"claim_element_{index}_element_id_missing")
        if element_id in element_ids:
            errors.append(f"duplicate_claim_element_id: {element_id}")
        element_ids.add(element_id)
        if is_blank(element.get("text")):
            errors.append(f"claim_element_{index}_text_missing")
        validate_support_file(base, element, f"claim_element_{element_id or index}", errors)

    delta_rows = data.get("delta_rows") if isinstance(data.get("delta_rows"), list) else []
    row_element_ids: set[str] = set()
    for index, row in enumerate(delta_rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"delta_row_{index}_must_be_object")
            continue
        element_id = str(row.get("element_id") or "")
        row_element_ids.add(element_id)
        if element_id not in element_ids:
            errors.append(f"delta_row_{index}_unknown_element_id: {element_id}")
        refs = row.get("closest_references")
        if not isinstance(refs, list) or not refs:
            errors.append(f"delta_row_{index}_closest_references_required")
        else:
            for publication in refs:
                if str(publication) not in seen_refs:
                    errors.append(f"delta_row_{index}_unknown_reference: {publication}")
        for key in [
            "known_in_prior_art",
            "applicant_distinguishing_feature",
            "technical_effect_evidence",
            "claim_strategy",
            "fallback_position",
        ]:
            if is_blank(row.get(key)):
                errors.append(f"delta_row_{index}_{key}_missing")
        if str(row.get("known_in_prior_art") or "") not in {"yes", "partial", "no", "unknown"}:
            errors.append(f"delta_row_{index}_known_in_prior_art_invalid")
        if str(row.get("novelty_risk") or "") not in RISK_VALUES:
            errors.append(f"delta_row_{index}_novelty_risk_invalid")
        if str(row.get("inventive_step_risk") or "") not in RISK_VALUES:
            errors.append(f"delta_row_{index}_inventive_step_risk_invalid")

    missing_rows = sorted(element_ids.difference(row_element_ids))
    for element_id in missing_rows:
        errors.append(f"missing_delta_row_for_claim_element: {element_id}")
    if any(str(row.get("known_in_prior_art") or "") in {"partial", "no"} for row in delta_rows if isinstance(row, dict)) is False:
        warnings.append("no_distinguishing_delta_marked_partial_or_no")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("delta", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        path = args.delta.resolve()
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
