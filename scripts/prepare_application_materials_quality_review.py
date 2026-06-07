#!/usr/bin/env python3
"""Prepare an application materials quality review gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import build_case_queue
import validate_application_materials_quality_review
import validate_artifact_hash_manifest
import validate_patent_application_materials


DIMENSION_WEIGHTS = {
    "claim_architecture": 18,
    "specification_enablement": 18,
    "abstract_and_drawings": 10,
    "evidence_binding": 18,
    "filing_readiness": 14,
    "legal_safety": 12,
    "auditability": 10,
}

MIN_OFFICIAL_PREFLIGHT_SCORE = 85.0
MIN_DIMENSION_SCORE = 7
ENTERPRISE_READY_SCORE = 90.0
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def find_document(materials: dict[str, Any], doc_type: str) -> dict[str, Any]:
    docs = materials.get("document_materials")
    if not isinstance(docs, list):
        return {}
    for doc in docs:
        if isinstance(doc, dict) and doc.get("type") == doc_type:
            return doc
    return {}


def read_document(materials_dir: Path, materials: dict[str, Any], doc_type: str) -> str:
    doc = find_document(materials, doc_type)
    raw_path = doc.get("path")
    if is_blank(raw_path):
        return ""
    path = (materials_dir / str(raw_path)).resolve()
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def check(check_id: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"id": check_id, "passed": bool(passed), "evidence": evidence}


def score_from_checks(checks: list[dict[str, Any]]) -> int:
    if not checks:
        return 0
    passed = sum(1 for item in checks if item.get("passed") is True)
    return int(round((passed / len(checks)) * 10))


def dimension(name: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    score = score_from_checks(checks)
    return {
        "name": name,
        "score": score,
        "weight": DIMENSION_WEIGHTS[name],
        "passed": score >= MIN_DIMENSION_SCORE,
        "checks": checks,
    }


def weighted_score(dimensions: dict[str, dict[str, Any]]) -> float:
    weighted = 0.0
    total_weight = 0
    for name, weight in DIMENSION_WEIGHTS.items():
        dim = dimensions.get(name, {})
        weighted += float(dim.get("score") or 0) * weight
        total_weight += weight
    return round((weighted / total_weight) * 10, 2)


def exact_hash(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def official_types(materials: dict[str, Any]) -> set[str]:
    docs = materials.get("official_material_inventory")
    if not isinstance(docs, list):
        return set()
    return {str(doc.get("type") or "") for doc in docs if isinstance(doc, dict)}


def build_dimensions(materials_dir: Path, materials: dict[str, Any], materials_valid: bool) -> dict[str, dict[str, Any]]:
    claims_text = read_document(materials_dir, materials, "claims")
    spec_text = read_document(materials_dir, materials, "specification")
    abstract_text = read_document(materials_dir, materials, "abstract")
    drawings_text = read_document(materials_dir, materials, "drawings")
    evidence = materials.get("evidence_provenance") if isinstance(materials.get("evidence_provenance"), dict) else {}
    abnormal = (
        materials.get("abnormal_filing_risk_assessment")
        if isinstance(materials.get("abnormal_filing_risk_assessment"), dict)
        else {}
    )
    request = materials.get("request_form_metadata") if isinstance(materials.get("request_form_metadata"), dict) else {}
    xml = materials.get("xml_readiness") if isinstance(materials.get("xml_readiness"), dict) else {}
    safeguards = materials.get("safeguards") if isinstance(materials.get("safeguards"), dict) else {}
    source = materials.get("source_package") if isinstance(materials.get("source_package"), dict) else {}
    generated_docs = materials.get("document_materials") if isinstance(materials.get("document_materials"), list) else []

    dims = {
        "claim_architecture": dimension(
            "claim_architecture",
            [
                check("claims_section_present", "## Claims Draft" in claims_text, "claims material contains Claims Draft"),
                check("independent_claim_candidates_present", "Independent Claim Candidates" in claims_text, "independent claim candidates marker"),
                check("dependent_claim_ladder_present", "Dependent Claim Ladder" in claims_text, "dependent claim ladder marker"),
                check("numbered_independent_claim_present", re.search(r"(?m)^\s*1\.", claims_text) is not None, "claim 1 numbering"),
                check("claim_support_rows_present", int(evidence.get("claim_support_rows_count") or 0) > 0, "claim support rows count"),
            ],
        ),
        "specification_enablement": dimension(
            "specification_enablement",
            [
                check("technical_problem_present", "## Technical Problem" in spec_text, "technical problem section"),
                check("technical_solution_present", "## Technical Solution" in spec_text, "technical solution section"),
                check("beneficial_effects_present", "## Beneficial Technical Effects" in spec_text, "technical effects section"),
                check("drawings_description_present", "## Brief Description Of Drawings" in spec_text, "drawing description section"),
                check("embodiments_present", "## Detailed Embodiments" in spec_text, "detailed embodiments section"),
            ],
        ),
        "abstract_and_drawings": dimension(
            "abstract_and_drawings",
            [
                check("abstract_section_present", "## Abstract" in abstract_text, "abstract marker"),
                check("abstract_solution_language_present", "solution includes" in abstract_text.lower(), "abstract solution language"),
                check("drawings_section_present", "## Brief Description Of Drawings" in drawings_text, "drawings marker"),
                check("figure_reference_present", "Fig." in drawings_text, "figure reference"),
            ],
        ),
        "evidence_binding": dimension(
            "evidence_binding",
            [
                check("materials_schema_valid", materials_valid, "validate_patent_application_materials passed"),
                check("own_support_hashes_present", bool(evidence.get("own_support_hashes")), "own support hashes"),
                check("prohibited_reference_hashes_recorded", isinstance(evidence.get("prohibited_reference_hashes"), list), "prohibited reference hash list"),
                check("reference_not_used_as_support", evidence.get("no_reference_or_prior_art_used_as_claim_support") is True, "reference boundary"),
                check("abnormal_risk_low", abnormal.get("risk_level") == "low", "same-case low abnormal filing risk"),
            ],
        ),
        "filing_readiness": dimension(
            "filing_readiness",
            [
                check("applicant_name_present", not is_blank(request.get("applicant_name")), "request metadata applicant"),
                check("inventors_present", bool(request.get("inventors")), "request metadata inventors"),
                check("official_inventory_complete", {"claims", "specification", "abstract", "drawings", "request_metadata"}.issubset(official_types(materials)), "official inventory"),
                check("xml_validation_passed", xml.get("validation_result") == "passed", "XML readiness validation"),
                check("official_preflight_required", xml.get("official_channel_preflight_required") is True, "official-channel preflight required"),
            ],
        ),
        "legal_safety": dimension(
            "legal_safety",
            [
                check("ai_only_legal_gate_mode", materials.get("legal_gate_mode") == "ai_self_filing_no_external_lawyer", "AI self-filing mode"),
                check("external_lawyer_false", materials.get("external_lawyer_involved") is False, "external lawyer absent"),
                check("no_legal_advice_claimed", safeguards.get("no_legal_advice_claimed") is True, "no legal advice claim"),
                check("no_lawyer_or_agent_review_claimed", safeguards.get("no_lawyer_or_agent_review_claimed") is True, "no lawyer or agent review claim"),
                check("no_official_action_claimed", materials.get("official_system_touched") is False and materials.get("official_submission_performed") is False, "official flags false"),
            ],
        ),
        "auditability": dimension(
            "auditability",
            [
                check("final_package_hash_exact", exact_hash(materials.get("final_package_hash")), "final package hash exact"),
                check("source_draft_hash_exact", exact_hash(source.get("source_draft_hash")), "source draft hash exact"),
                check("evidence_artifact_hash_exact", exact_hash(evidence.get("artifact_hash")), "evidence artifact hash exact"),
                check("abnormal_artifact_hash_exact", exact_hash(abnormal.get("artifact_hash")), "abnormal risk artifact hash exact"),
                check("all_generated_doc_hashes_exact", all(exact_hash(doc.get("hash")) for doc in generated_docs if isinstance(doc, dict)), "generated document hashes exact"),
            ],
        ),
    }
    return dims


def render_report(review: dict[str, Any]) -> str:
    gate = review.get("quality_gate") if isinstance(review.get("quality_gate"), dict) else {}
    lines = [
        "# Application Materials Quality Review",
        "",
        f"Case ID: {review.get('case_id')}",
        f"Gate status: {gate.get('status')}",
        f"Weighted score: {gate.get('weighted_score')}",
        f"Minimum official preflight score: {gate.get('minimum_score_for_official_preflight')}",
        f"Enterprise ready score: {gate.get('enterprise_ready_score')}",
        "Official system touched: no",
        "Official submission performed: no",
        "External lawyer involved: no",
        "",
        "## Dimensions",
        "",
        "| Dimension | Score | Weight | Result |",
        "| --- | ---: | ---: | --- |",
    ]
    dimensions = review.get("dimensions") if isinstance(review.get("dimensions"), dict) else {}
    for name, dim in dimensions.items():
        if isinstance(dim, dict):
            lines.append(f"| {name} | {dim.get('score')} | {dim.get('weight')} | {'pass' if dim.get('passed') else 'fail'} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This quality review is a local preflight gate. It does not provide legal advice, does not claim lawyer or patent-agent review, and does not perform any official filing action.",
        ]
    )
    return "\n".join(lines) + "\n"


def artifact_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [
            {"path": rel(path, output_dir), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in files
        ],
    }


def prepare(materials_dir: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    materials_root = materials_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    materials_path = materials_root / "application-materials.json"
    if not materials_path.exists():
        return {
            "ok": False,
            "errors": [f"missing_application_materials: {materials_path}"],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1

    materials = load_json(materials_path)
    materials_ok, materials_errors, materials_warnings = validate_patent_application_materials.validate(
        materials,
        materials_root,
    )
    dimensions = build_dimensions(materials_root, materials, materials_ok)
    score = weighted_score(dimensions)
    min_dimension_score = min((int(item.get("score") or 0) for item in dimensions.values()), default=0)
    gate_passed = materials_ok and score >= MIN_OFFICIAL_PREFLIGHT_SCORE and min_dimension_score >= MIN_DIMENSION_SCORE

    report_path = output_root / "application-materials-quality-report.md"
    review_path = output_root / "application-materials-quality-review.json"
    hashes_path = output_root / "artifact-hashes.json"

    review = {
        "case_id": materials.get("case_id"),
        "reviewed_at": build_case_queue.utc_plus_8_now(),
        "review_type": "application_materials_quality_gate",
        "source_rubric": "references/quality-rubric.md",
        "application_materials": {
            "path": rel(materials_path, output_root),
            "hash": sha256_file(materials_path),
        },
        "quality_gate": {
            "status": "passed" if gate_passed else "failed",
            "weighted_score": score,
            "minimum_score_for_official_preflight": MIN_OFFICIAL_PREFLIGHT_SCORE,
            "minimum_dimension_score": MIN_DIMENSION_SCORE,
            "enterprise_ready_score": ENTERPRISE_READY_SCORE,
            "enterprise_ready": score >= ENTERPRISE_READY_SCORE and min_dimension_score >= 8,
            "official_preflight_allowed": gate_passed,
        },
        "dimensions": dimensions,
        "materials_validation": {
            "ok": materials_ok,
            "errors": materials_errors,
            "warnings": materials_warnings,
        },
        "next_action": (
            "Run official-channel preflight next; do not upload, sign, pay, submit, or claim receipt from quality review alone."
            if gate_passed
            else "Cure failed quality dimensions before official-channel preflight."
        ),
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }
    write_json(review_path, review)
    report_path.write_text(render_report(review), encoding="utf-8")
    write_json(hashes_path, artifact_manifest(output_root, str(materials.get("case_id") or ""), [review_path, report_path]))

    review_ok, review_errors, review_warnings = validate_application_materials_quality_review.validate(review, output_root)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
    ok = review_ok and hash_ok
    return {
        "ok": ok,
        "case_id": materials.get("case_id"),
        "output_dir": str(output_root),
        "artifacts": {
            "quality_review": str(review_path),
            "quality_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "review_errors": review_errors,
        "review_warnings": review_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("materials_dir", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.materials_dir, args.output_dir)
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1
    if args.json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print("PASS" if response.get("ok") else "FAIL")
        print(json.dumps(response, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
