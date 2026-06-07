#!/usr/bin/env python3
"""Validate confirmed-disclosure to draft-only package benchmark artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import validate_artifact_hash_manifest
import validate_claim_support_map
import validate_filing_status_transition
import validate_invention_disclosure
import validate_patent_application_draft
import validate_reference_patent_delta

PROHIBITED_AI_ONLY_DEFAULT_TERMS = re.compile(r"\b(attorney|lawyer|counsel)\b|patent-agent|patent agent", re.IGNORECASE)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_no_lawyer_default_terms(path: Path, label: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if PROHIBITED_AI_ONLY_DEFAULT_TERMS.search(line):
            errors.append(f"{label}_must_not_default_to_lawyer_or_patent_agent_terms: line={line_number}")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    disclosure_path = benchmark_dir / "invention-disclosure.json"
    draft_path = benchmark_dir / "patent-application-draft.md"
    claim_map_path = benchmark_dir / "claim-support-map.md"
    status_path = benchmark_dir / "filing-status.json"
    reference_delta_path = benchmark_dir / "reference-patent-delta.json"
    report_path = benchmark_dir / "draft-package-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if disclosure_path.exists():
        ok, errs, warns = validate_invention_disclosure.validate(load_json(disclosure_path))
        if not ok:
            errors.extend([f"invention_disclosure: {item}" for item in errs])
        warnings.extend([f"invention_disclosure: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {disclosure_path}")

    ok, errs, warns = validate_patent_application_draft.validate(draft_path)
    if not ok:
        errors.extend([f"patent_application_draft: {item}" for item in errs])
    warnings.extend([f"patent_application_draft: {item}" for item in warns])
    if draft_path.exists():
        require_no_lawyer_default_terms(draft_path, "patent_application_draft", errors)
        if reference_delta_path.exists():
            text = draft_path.read_text(encoding="utf-8", errors="replace").lower()
            for needle in [
                "reference patent delta strategy",
                "reference patents are boundary evidence only",
                "claim strategy",
                "fallback",
            ]:
                if needle not in text:
                    errors.append(f"reference_delta_draft_missing_text: {needle}")

    ok, errs, warns = validate_claim_support_map.validate(claim_map_path, allow_draft=True)
    if not ok:
        errors.extend([f"claim_support_map: {item}" for item in errs])
    warnings.extend([f"claim_support_map: {item}" for item in warns])
    if claim_map_path.exists():
        require_no_lawyer_default_terms(claim_map_path, "claim_support_map", errors)
        if reference_delta_path.exists():
            text = claim_map_path.read_text(encoding="utf-8", errors="replace").lower()
            if "requires full prior-art element comparison before filing" in text:
                errors.append("reference_delta_claim_map_must_use_specific_delta_rows")
            for needle in [
                "uses the three-signal comparison",
                "classifies hydration and elasticity state",
                "changes kneading torque and rest timing",
            ]:
                if needle not in text:
                    errors.append(f"reference_delta_claim_map_missing_text: {needle}")

    if reference_delta_path.exists():
        ok, errs, warns = validate_reference_patent_delta.validate(load_json(reference_delta_path), benchmark_dir)
        if not ok:
            errors.extend([f"reference_patent_delta: {item}" for item in errs])
        warnings.extend([f"reference_patent_delta: {item}" for item in warns])

    if status_path.exists():
        status = load_json(status_path)
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        if status.get("status") != "draft_only":
            errors.append("status_must_be_draft_only")
        if status.get("legal_gate") != "failed":
            errors.append("legal_gate_must_fail_for_filing")
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
        if status.get("official_receipt_hash") or status.get("application_number"):
            errors.append("draft_package_must_not_have_receipt_or_application_number")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "draft package generation report",
            "draft generation allowed: yes",
            "filing allowed: no",
            "legal gate for filing: failed",
            "ai self-filing legal/compliance",
            "official system touched: no",
            "official submission performed: no",
        ]:
            if needle not in text:
                errors.append(f"draft_package_report_missing_text: {needle}")
        if reference_delta_path.exists() and "reference patent delta used: yes" not in text:
            errors.append("draft_package_report_must_record_reference_delta_used")
        require_no_lawyer_default_terms(report_path, "draft_package_report", errors)
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {hashes_path}")

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
