#!/usr/bin/env python3
"""Validate abnormal filing risk benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_abnormal_filing_risk_assessment
import validate_artifact_hash_manifest
import validate_claim_support_map
import validate_draft_evidence_provenance
import validate_filing_status_transition
import validate_invention_disclosure
import validate_patent_application_draft
import validate_reference_patent_delta
import validate_source_material_manifest


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = benchmark_dir / "source-material-manifest.yaml"
    disclosure_path = benchmark_dir / "invention-disclosure.json"
    draft_path = benchmark_dir / "patent-application-draft.md"
    claim_map_path = benchmark_dir / "claim-support-map.md"
    status_path = benchmark_dir / "filing-status.json"
    provenance_path = benchmark_dir / "draft-evidence-provenance.json"
    reference_delta_path = benchmark_dir / "reference-patent-delta.json"
    assessment_path = benchmark_dir / "abnormal-filing-risk-assessment.json"
    report_path = benchmark_dir / "abnormal-filing-risk-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if manifest_path.exists():
        ok, errs, warns = validate_source_material_manifest.validate(
            validate_source_material_manifest.load_packet(manifest_path),
            base_dir=benchmark_dir,
        )
        if not ok:
            errors.extend([f"source_manifest: {item}" for item in errs])
        warnings.extend([f"source_manifest: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {manifest_path}")

    if disclosure_path.exists():
        ok, errs, warns = validate_invention_disclosure.validate(validate_invention_disclosure.load_packet(disclosure_path))
        if not ok:
            errors.extend([f"invention_disclosure: {item}" for item in errs])
        warnings.extend([f"invention_disclosure: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {disclosure_path}")

    ok, errs, warns = validate_patent_application_draft.validate(draft_path)
    if not ok:
        errors.extend([f"draft: {item}" for item in errs])
    warnings.extend([f"draft: {item}" for item in warns])

    ok, errs, warns = validate_claim_support_map.validate(claim_map_path, allow_draft=True)
    if not ok:
        errors.extend([f"claim_support_map: {item}" for item in errs])
    warnings.extend([f"claim_support_map: {item}" for item in warns])

    if status_path.exists():
        status = load_json(status_path)
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        if status.get("status") != "draft_only":
            errors.append("filing_status_must_be_draft_only")
        if status.get("official_submission_performed") is not False:
            errors.append("filing_status_must_not_submit")
    else:
        errors.append(f"missing_file: {status_path}")

    if provenance_path.exists():
        ok, errs, warns = validate_draft_evidence_provenance.validate(load_json(provenance_path))
        if not ok:
            errors.extend([f"draft_evidence_provenance: {item}" for item in errs])
        warnings.extend([f"draft_evidence_provenance: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {provenance_path}")

    if reference_delta_path.exists():
        ok, errs, warns = validate_reference_patent_delta.validate(load_json(reference_delta_path), benchmark_dir)
        if not ok:
            errors.extend([f"reference_patent_delta: {item}" for item in errs])
        warnings.extend([f"reference_patent_delta: {item}" for item in warns])

    assessment = {}
    if assessment_path.exists():
        assessment = load_json(assessment_path)
        ok, errs, warns = validate_abnormal_filing_risk_assessment.validate(assessment)
        if not ok:
            errors.extend([f"abnormal_filing_risk_assessment: {item}" for item in errs])
        warnings.extend([f"abnormal_filing_risk_assessment: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {assessment_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "abnormal filing risk assessment",
            "g8 non-abnormal filing check",
            "random computer generation",
            "copied or simply replaced prior art",
            "maliciously distributed batch filings",
            "draft-only",
            "not legal advice",
            "not lawyer review",
            "not patent-agent review",
            "not an official submission",
        ]:
            if needle not in text:
                errors.append(f"abnormal_filing_risk_report_missing_text: {needle}")
        if reference_delta_path.exists() and "reference delta boundary" not in text:
            errors.append("abnormal_filing_risk_report_missing_reference_delta_boundary")
        if reference_delta_path.exists() and "reference-patent delta evidence is present" not in text:
            errors.append("abnormal_filing_risk_report_missing_reference_delta_boundary")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {hashes_path}")

    if assessment and assessment.get("official_system_touched") is not False:
        errors.append("assessment_must_not_touch_official_system")
    if assessment and assessment.get("official_submission_performed") is not False:
        errors.append("assessment_must_not_submit")
    if assessment and assessment.get("external_lawyer_involved") is not False:
        errors.append("assessment_must_not_involve_external_lawyer")
    if reference_delta_path.exists() and assessment and not assessment.get("reference_patent_delta_hash"):
        errors.append("assessment_reference_patent_delta_hash_required")

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
