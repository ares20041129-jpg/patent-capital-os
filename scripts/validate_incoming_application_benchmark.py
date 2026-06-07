#!/usr/bin/env python3
"""Validate incoming-disclosure-to-application benchmark artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import validate_claim_support_map
import validate_artifact_hash_manifest
import validate_invention_disclosure
import validate_patent_application_draft
import validate_source_material_manifest


PROHIBITED_AI_ONLY_DEFAULT_TERMS = re.compile(
    r"\b(attorney|lawyer|counsel)\b|patent-agent|patent agent|counsel_review_needed",
    re.IGNORECASE,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_no_default_review_terms(text: str, label: str, errors: list[str]) -> None:
    if PROHIBITED_AI_ONLY_DEFAULT_TERMS.search(text):
        errors.append(f"{label}_must_not_default_to_lawyer_or_patent_agent_review")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = benchmark_dir / "source-material-manifest.yaml"
    disclosure_path = benchmark_dir / "invention-disclosure.json"
    draft_path = benchmark_dir / "patent-application-draft.md"
    claim_map_path = benchmark_dir / "claim-support-map.md"
    status_path = benchmark_dir / "filing-status.json"
    results_path = benchmark_dir / "results.tsv"
    artifact_hashes_path = benchmark_dir / "artifact-hashes.json"

    if manifest_path.exists():
        manifest = validate_source_material_manifest.load_packet(manifest_path)
        ok, errs, warns = validate_source_material_manifest.validate(
            manifest,
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"manifest: {item}" for item in errs])
        warnings.extend([f"manifest: {item}" for item in warns])
        missing_materials = manifest.get("missing_materials", [])
        if isinstance(missing_materials, list):
            for item in missing_materials:
                require_no_default_review_terms(str(item), "manifest_missing_materials", errors)
        if "AI self-filing legal/compliance authorization packet." not in missing_materials:
            errors.append("manifest_must_require_ai_self_filing_authorization_packet")
    else:
        errors.append(f"missing_file: {manifest_path}")

    if disclosure_path.exists():
        disclosure = validate_invention_disclosure.load_packet(disclosure_path)
        ok, errs, warns = validate_invention_disclosure.validate(disclosure)
        if not ok:
            errors.extend([f"disclosure: {item}" for item in errs])
        warnings.extend([f"disclosure: {item}" for item in warns])
        if "counsel_questions" in disclosure:
            errors.append("disclosure_must_not_use_counsel_questions")
        if not isinstance(disclosure.get("ai_legal_compliance_questions"), list) or not disclosure.get("ai_legal_compliance_questions"):
            errors.append("disclosure_must_include_ai_legal_compliance_questions")
        require_no_default_review_terms(str(disclosure.get("business_goal") or ""), "disclosure_business_goal", errors)
    else:
        errors.append(f"missing_file: {disclosure_path}")

    ok, errs, warns = validate_patent_application_draft.validate(draft_path)
    if not ok:
        errors.extend([f"draft: {item}" for item in errs])
    warnings.extend([f"draft: {item}" for item in warns])
    if draft_path.exists():
        draft_text = draft_path.read_text(encoding="utf-8", errors="replace")
        for needle in [
            "draft status: ai_self_filing_authorization_needed",
            "## AI Legal/Compliance Questions",
            "final AI self-filing legal/compliance authorization",
        ]:
            if needle.lower() not in draft_text.lower():
                errors.append(f"draft_missing_ai_self_filing_text: {needle}")
        require_no_default_review_terms(draft_text, "draft", errors)

    ok, errs, warns = validate_claim_support_map.validate(claim_map_path, allow_draft=True)
    if not ok:
        errors.extend([f"claim_map: {item}" for item in errs])
    warnings.extend([f"claim_map: {item}" for item in warns])
    if claim_map_path.exists():
        require_no_default_review_terms(claim_map_path.read_text(encoding="utf-8", errors="replace"), "claim_map", errors)

    if status_path.exists():
        status = load_json(status_path)
        if status.get("status") != "draft_only":
            errors.append("status_must_be_draft_only")
        if status.get("legal_gate") != "failed":
            errors.append("legal_gate_must_be_failed_without_ai_self_filing_authorization")
        if status.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("legal_gate_mode_must_be_ai_self_filing_no_external_lawyer")
        if status.get("decision") != "do_not_file":
            errors.append("decision_must_be_do_not_file")
        if status.get("draft_generation_allowed") is not True:
            errors.append("draft_generation_allowed_must_be_true")
        if status.get("filing_allowed") is not False:
            errors.append("filing_allowed_must_be_false")
        if status.get("external_lawyer_involved") is not False:
            errors.append("external_lawyer_involved_must_be_false")
        if status.get("official_system_touched") is not False:
            errors.append("official_system_touched_must_be_false")
        if status.get("official_submission_performed") is not False:
            errors.append("official_submission_performed_must_be_false")
    else:
        errors.append(f"missing_file: {status_path}")

    if not results_path.exists():
        errors.append(f"missing_file: {results_path}")

    if artifact_hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(artifact_hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {artifact_hashes_path}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.benchmark_dir)
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
