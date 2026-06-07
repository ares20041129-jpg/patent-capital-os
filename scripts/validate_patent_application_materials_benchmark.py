#!/usr/bin/env python3
"""Validate generated patent application materials benchmark artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import validate_abnormal_filing_risk_assessment
import validate_artifact_hash_manifest
import validate_draft_evidence_provenance
import validate_filing_status_transition
import validate_patent_application_materials


REQUIRED_FILES = [
    "application-materials.json",
    "request-form-metadata.json",
    "document-generation-plan.json",
    "claims-material.md",
    "specification-material.md",
    "abstract-material.md",
    "drawings-materials-plan.md",
    "xml-readiness-checklist.json",
    "draft-evidence-provenance.json",
    "abnormal-filing-risk-assessment.json",
    "filing-status.json",
    "application-materials-report.md",
    "artifact-hashes.json",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = benchmark_dir.resolve()

    for filename in REQUIRED_FILES:
        if not (root / filename).exists():
            errors.append(f"missing_file: {root / filename}")

    materials_path = root / "application-materials.json"
    materials = {}
    if materials_path.exists():
        materials = load_json(materials_path)
        ok, errs, warns = validate_patent_application_materials.validate(materials, root)
        if not ok:
            errors.extend([f"application_materials: {item}" for item in errs])
        warnings.extend([f"application_materials: {item}" for item in warns])

    provenance_path = root / "draft-evidence-provenance.json"
    if provenance_path.exists():
        provenance = load_json(provenance_path)
        ok, errs, warns = validate_draft_evidence_provenance.validate(provenance)
        if not ok:
            errors.extend([f"draft_evidence_provenance: {item}" for item in errs])
        warnings.extend([f"draft_evidence_provenance: {item}" for item in warns])
        if materials:
            evidence = materials.get("evidence_provenance", {})
            if evidence.get("artifact_hash") != sha256_file(provenance_path):
                errors.append("draft_evidence_provenance_hash_mismatch")
            if evidence.get("case_id") != materials.get("case_id"):
                errors.append("draft_evidence_provenance_case_id_mismatch")
            if provenance.get("reference_patent_delta_hash"):
                if evidence.get("reference_patent_delta_hash") != provenance.get("reference_patent_delta_hash"):
                    errors.append("evidence_reference_patent_delta_hash_mismatch")
                for key in ["reference_delta_rows_count", "reference_delta_claim_elements_count"]:
                    if evidence.get(key) != provenance.get(key):
                        errors.append(f"evidence_{key}_mismatch")

    abnormal_path = root / "abnormal-filing-risk-assessment.json"
    if abnormal_path.exists():
        abnormal = load_json(abnormal_path)
        ok, errs, warns = validate_abnormal_filing_risk_assessment.validate(abnormal)
        if not ok:
            errors.extend([f"abnormal_filing_risk_assessment: {item}" for item in errs])
        warnings.extend([f"abnormal_filing_risk_assessment: {item}" for item in warns])
        if materials:
            risk = materials.get("abnormal_filing_risk_assessment", {})
            if risk.get("artifact_hash") != sha256_file(abnormal_path):
                errors.append("abnormal_filing_risk_assessment_hash_mismatch")
            if risk.get("risk_level") != "low":
                errors.append("abnormal_filing_risk_assessment_must_be_low")
            if abnormal.get("reference_patent_delta_hash"):
                if risk.get("reference_patent_delta_hash") != abnormal.get("reference_patent_delta_hash"):
                    errors.append("abnormal_reference_patent_delta_hash_mismatch")
                for key in ["reference_delta_rows_count", "reference_delta_claim_elements_count"]:
                    if risk.get(key) != abnormal.get(key):
                        errors.append(f"abnormal_{key}_mismatch")
                if risk.get("reference_delta_boundary_preserved") is not True:
                    errors.append("abnormal_reference_delta_boundary_must_be_preserved")
                evidence = materials.get("evidence_provenance", {})
                if evidence.get("reference_patent_delta_hash") != risk.get("reference_patent_delta_hash"):
                    errors.append("materials_reference_delta_hash_mismatch_between_provenance_and_abnormal")

    status_path = root / "filing-status.json"
    if status_path.exists():
        status = load_json(status_path)
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        if status.get("decision") != "materials_generated_official_preflight_required":
            errors.append("filing_status_decision_must_require_official_preflight")
        if status.get("external_lawyer_involved") is not False:
            errors.append("filing_status_external_lawyer_involved_must_be_false")
        if status.get("official_system_touched") is not False:
            errors.append("filing_status_must_not_touch_official_system")
        if status.get("official_submission_performed") is not False:
            errors.append("filing_status_must_not_submit")

    report_path = root / "application-materials-report.md"
    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "patent application materials",
            "ai self-filing",
            "request form metadata",
            "claim-support provenance",
            "abnormal filing risk",
            "official-channel preflight",
            "no external lawyer",
            "not legal advice",
            "not lawyer review",
            "not patent-agent review",
            "not an official submission",
            "not a receipt",
            "not an application number",
        ]:
            if needle not in text:
                errors.append(f"application_materials_report_missing_text: {needle}")
        if (root / "abnormal-filing-risk-assessment.json").exists():
            abnormal = load_json(root / "abnormal-filing-risk-assessment.json")
            if abnormal.get("reference_patent_delta_hash"):
                for needle in [
                    "reference delta boundary",
                    "reference-patent delta hash",
                    "boundary preserved: true",
                    "not applicant claim support",
                ]:
                    if needle not in text:
                        errors.append(f"application_materials_reference_delta_report_missing_text: {needle}")

    hashes_path = root / "artifact-hashes.json"
    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
        manifest = load_json(hashes_path)
        listed = {str(item.get("path") or "") for item in manifest.get("files", []) if isinstance(item, dict)}
        for filename in REQUIRED_FILES:
            if filename != "artifact-hashes.json" and filename not in listed:
                errors.append(f"artifact_hashes_missing_required_file: {filename}")

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
