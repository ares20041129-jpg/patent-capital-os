#!/usr/bin/env python3
"""Validate the full local pre-submission AI self-filing pipeline benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import validate_abnormal_filing_risk_benchmark
import validate_ai_self_filing_package_benchmark
import validate_application_materials_pipeline_benchmark
import validate_artifact_hash_manifest
import validate_case_lifecycle_benchmark
import validate_case_package_benchmark
import validate_draft_evidence_provenance_benchmark
import validate_draft_package_generation_benchmark
import validate_generated_approved_adapter_preflight_benchmark
import validate_reference_patent_delta_benchmark
import validate_ready_for_authorized_filing_benchmark
import validate_scaffold_confirmation_benchmark


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    folder_validators = [
        ("case_package", benchmark_dir, validate_case_package_benchmark.validate),
        ("disclosure_confirmation", benchmark_dir / "scaffold-confirmation-to-disclosure", validate_scaffold_confirmation_benchmark.validate),
        ("draft_package", benchmark_dir / "draft-package-generation", validate_draft_package_generation_benchmark.validate),
        ("draft_evidence_provenance", benchmark_dir / "draft-evidence-provenance-gate", validate_draft_evidence_provenance_benchmark.validate),
        ("abnormal_filing_risk", benchmark_dir / "abnormal-filing-risk-gate", validate_abnormal_filing_risk_benchmark.validate),
        ("ai_self_filing_package_validation", benchmark_dir / "ai-self-filing-package-validation", validate_ai_self_filing_package_benchmark.validate),
        ("application_materials_pipeline", benchmark_dir / "application-materials-pipeline", validate_application_materials_pipeline_benchmark.validate),
        ("ai_self_filing_official_ready", benchmark_dir / "ai-self-filing-official-ready", validate_ready_for_authorized_filing_benchmark.validate),
        ("ai_self_filing_approved_adapter_preflight", benchmark_dir / "ai-self-filing-approved-adapter-preflight", validate_generated_approved_adapter_preflight_benchmark.validate),
        ("case_lifecycle_trace", benchmark_dir / "case-lifecycle-trace", validate_case_lifecycle_benchmark.validate),
    ]
    reference_delta_dir = benchmark_dir / "reference-patent-delta"
    has_reference_delta = reference_delta_dir.exists()
    if has_reference_delta:
        folder_validators.insert(2, ("reference_patent_delta", reference_delta_dir, validate_reference_patent_delta_benchmark.validate))
    for label, folder, validator in folder_validators:
        if not folder.exists():
            errors.append(f"missing_dir: {folder}")
            continue
        ok, errs, warns = validator(folder)
        if not ok:
            errors.extend([f"{label}: {item}" for item in errs])
        warnings.extend([f"{label}: {item}" for item in warns])

    result_path = benchmark_dir / "pre-submission-pipeline-result.json"
    report_path = benchmark_dir / "pre-submission-pipeline-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    source_path = benchmark_dir / "ai-self-filing-package-validation" / "ai-self-filing-source.json"
    official_source_path = benchmark_dir / "ai-self-filing-official-ready" / "official-preflight-source.json"
    approved_adapter_source_path = benchmark_dir / "ai-self-filing-approved-adapter-preflight" / "approved-adapter-source.json"
    lifecycle_trace_path = benchmark_dir / "case-lifecycle-trace" / "case-lifecycle-trace.json"

    if result_path.exists():
        result = load_json(result_path)
        result_case_id = result.get("case_id")
        if result.get("ok") is not True:
            errors.append("pre_submission_result_ok_must_be_true")
        if result.get("pipeline_type") != "pre_submission_ai_self_filing_no_external_lawyer":
            errors.append("pre_submission_pipeline_type_invalid")
        if result.get("status") != "approved_for_adapter_execution":
            errors.append("pre_submission_status_must_stop_at_approved_for_adapter_execution")
        if result.get("decision") != "approved_for_adapter_execution_no_auto_submit":
            errors.append("pre_submission_decision_must_be_approved_adapter_without_auto_submit")
        if result.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("pre_submission_legal_gate_mode_invalid")
        if has_reference_delta and not str(result.get("reference_patent_delta_hash") or "").startswith("sha256:"):
            errors.append("pre_submission_reference_delta_hash_missing")
        if result.get("pre_submission_lifecycle_gate") != "passed":
            errors.append("pre_submission_lifecycle_gate_must_pass")
        if not str(result.get("lifecycle_trace_hash") or "").startswith("sha256:"):
            errors.append("pre_submission_lifecycle_trace_hash_missing")
        elif lifecycle_trace_path.exists() and result.get("lifecycle_trace_hash") != sha256_file(lifecycle_trace_path):
            errors.append("pre_submission_lifecycle_trace_hash_mismatch")
        for field in ["official_system_touched", "official_submission_performed", "adapter_execution_performed", "external_lawyer_involved", "automatic_submission_performed"]:
            if result.get(field) is not False:
                errors.append(f"pre_submission_{field}_must_be_false")
        stages = result.get("stages") if isinstance(result.get("stages"), dict) else {}
        for label, _folder, _validator in folder_validators:
            stage = stages.get(label) if isinstance(stages.get(label), dict) else {}
            if stage.get("ok") is not True:
                errors.append(f"pre_submission_stage_must_pass: {label}")
    else:
        errors.append(f"missing_file: {result_path}")
        result_case_id = None

    if source_path.exists():
        source = load_json(source_path)
        if source.get("external_lawyer_involved") is not False:
            errors.append("ai_self_filing_source_external_lawyer_must_be_false")
        assessment = source.get("ai_compliance_review", {}).get("abnormal_filing_risk_assessment", {})
        if assessment.get("artifact_path") != "../abnormal-filing-risk-gate/abnormal-filing-risk-assessment.json":
            errors.append("ai_self_filing_source_abnormal_artifact_path_must_point_to_pipeline_assessment")
        if has_reference_delta:
            if not str(assessment.get("reference_patent_delta_hash") or "").startswith("sha256:"):
                errors.append("ai_self_filing_source_reference_delta_hash_missing")
            if assessment.get("reference_delta_boundary_preserved") is not True:
                errors.append("ai_self_filing_source_reference_delta_boundary_must_be_preserved")
    else:
        errors.append(f"missing_file: {source_path}")

    if official_source_path.exists():
        official_source = load_json(official_source_path)
        materials = official_source.get("application_materials") if isinstance(official_source.get("application_materials"), dict) else {}
        if materials.get("path") != "../application-materials-pipeline/application-materials/application-materials.json":
            errors.append("official_preflight_source_application_materials_path_must_point_to_pipeline_materials")
        if not str(materials.get("hash") or "").startswith("sha256:"):
            errors.append("official_preflight_source_application_materials_hash_missing")
    else:
        errors.append(f"missing_file: {official_source_path}")

    if approved_adapter_source_path.exists():
        adapter_source = load_json(approved_adapter_source_path)
        if adapter_source.get("case_id") != result_case_id:
            errors.append("approved_adapter_source_case_id_must_match_pipeline_case")
        if adapter_source.get("decision", {}).get("status") != "approved_for_adapter_execution":
            errors.append("approved_adapter_source_decision_status_invalid")
    else:
        errors.append(f"missing_file: {approved_adapter_source_path}")

    if lifecycle_trace_path.exists():
        trace = load_json(lifecycle_trace_path)
        if trace.get("final_status") != "approved_for_adapter_execution":
            errors.append("pre_submission_lifecycle_final_status_invalid")
        if trace.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("pre_submission_lifecycle_legal_gate_mode_invalid")
        if trace.get("external_lawyer_involved") is not False:
            errors.append("pre_submission_lifecycle_external_lawyer_must_be_false")
        if has_reference_delta:
            if trace.get("reference_patent_delta_hash") != result.get("reference_patent_delta_hash"):
                errors.append("pre_submission_lifecycle_reference_delta_hash_mismatch")
            if trace.get("reference_delta_boundary_preserved") is not True:
                errors.append("pre_submission_lifecycle_reference_delta_boundary_must_be_preserved")
            if not trace.get("application_materials_hash"):
                errors.append("pre_submission_lifecycle_application_materials_hash_missing")
    else:
        errors.append(f"missing_file: {lifecycle_trace_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "pre-submission pipeline report",
            "pipeline status: pass",
            "official system touched: no",
            "official submission performed: no",
            "adapter execution performed: no",
            "external lawyer involved: no",
            "lifecycle gate",
            "pre-submission lifecycle gate: passed",
            "lifecycle trace hash",
            "official-channel preflight",
            "do not automatically submit",
            "adapter execution",
        ]:
            if needle not in text:
                errors.append(f"pre_submission_report_missing_text: {needle}")
        if has_reference_delta:
            for needle in [
                "reference patent delta",
                "reference-patent delta hash",
                "not applicant claim support",
            ]:
                if needle not in text:
                    errors.append(f"pre_submission_reference_delta_report_missing_text: {needle}")
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
