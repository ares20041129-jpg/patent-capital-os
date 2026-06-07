#!/usr/bin/env python3
"""Build a dry-run patent case queue from case folders."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

import validate_case_queue


FOLDER_VALIDATORS = {
    "abnormal-filing-risk-gate": "validate_abnormal_filing_risk_benchmark",
    "abnormal-filing-risk-reference-delta": "validate_abnormal_filing_risk_benchmark",
    "abnormal-filing-risk-rejection": "validate_abnormal_filing_risk_rejection_benchmark",
    "ai-self-filing-abnormal-risk-gate": "validate_abnormal_filing_risk_benchmark",
    "ai-self-filing-abnormal-risk-binding-rejection": "validate_ai_self_filing_abnormal_risk_binding_rejection_benchmark",
    "ai-self-filing-application-materials-binding-rejection": "validate_ai_self_filing_application_materials_binding_rejection_benchmark",
    "ai-self-filing-approved-adapter-preflight": "validate_generated_approved_adapter_preflight_benchmark",
    "ai-self-filing-adapter-to-submitted-pending-receipt": "validate_generated_adapter_execution_result_benchmark",
    "ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta": "validate_generated_adapter_execution_result_benchmark",
    "ai-self-filing-cure-revalidation": "validate_ai_self_filing_cure_revalidation_benchmark",
    "ai-self-filing-deficiency-report": "validate_ai_self_filing_deficiency_report_benchmark",
    "ai-self-filing-draft-evidence-provenance": "validate_draft_evidence_provenance_benchmark",
    "ai-self-filing-legal-gate-rejection": "validate_ai_self_filing_legal_gate_rejection_benchmark",
    "ai-self-filing-lifecycle-trace": "validate_case_lifecycle_benchmark",
    "ai-self-filing-lifecycle-trace-reference-delta": "validate_case_lifecycle_benchmark",
    "ai-self-filing-official-receipt-to-application-number": "validate_generated_application_number_benchmark",
    "ai-self-filing-official-receipt-to-application-number-reference-delta": "validate_generated_application_number_benchmark",
    "ai-self-filing-official-ready": "validate_ready_for_authorized_filing_benchmark",
    "ai-self-filing-official-ready-reference-delta": "validate_ready_for_authorized_filing_benchmark",
    "ai-self-filing-package-validation": "validate_ai_self_filing_package_benchmark",
    "ai-self-filing-package-reference-delta": "validate_ai_self_filing_package_benchmark",
    "ai-self-filing-application-materials": "validate_patent_application_materials_benchmark",
    "ai-self-filing-application-materials-reference-delta": "validate_patent_application_materials_benchmark",
    "ai-self-filing-submitted-pending-receipt-to-official-receipt": "validate_generated_receipt_capture_benchmark",
    "ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta": "validate_generated_receipt_capture_benchmark",
    "adapter-execution-mock-submitted": "validate_adapter_execution_benchmark",
    "ai-self-filing-approved-adapter-preflight-reference-delta": "validate_generated_approved_adapter_preflight_benchmark",
    "application-materials-pipeline": "validate_application_materials_pipeline_benchmark",
    "application-materials-pipeline-reference-delta": "validate_application_materials_pipeline_benchmark",
    "application-materials-quality-gate": "validate_application_materials_quality_benchmark",
    "approved-adapter-evidence-queue": "validate_approved_adapter_evidence_queue_benchmark",
    "approved-adapter-to-submitted-pending-receipt": "validate_generated_adapter_execution_result_benchmark",
    "application-number-acceptance-mock": "validate_application_number_benchmark",
    "official-receipt-to-application-number": "validate_generated_application_number_benchmark",
    "official-session-authorization-gate": "validate_official_session_authorization_benchmark",
    "patent-application-materials-rejection": "validate_patent_application_materials_rejection_benchmark",
    "pre-submission-handoff-package": "validate_pre_submission_handoff_package",
    "pre-submission-handoff-package-reference-delta": "validate_pre_submission_handoff_package",
    "pre-submission-handoff-rejection": "validate_pre_submission_handoff_rejection_benchmark",
    "pre-submission-pipeline": "validate_pre_submission_pipeline_benchmark",
    "pre-submission-pipeline-reference-delta": "validate_pre_submission_pipeline_benchmark",
    "pre-submission-to-handoff": "validate_pre_submission_to_handoff_benchmark",
    "pre-submission-to-handoff-reference-delta": "validate_pre_submission_to_handoff_benchmark",
    "production-adapter-readiness-gate": "validate_production_adapter_readiness_benchmark",
    "production-official-evidence-gate": "validate_production_official_evidence_gate_benchmark",
    "reference-patent-delta": "validate_reference_patent_delta_benchmark",
    "approved-adapter-preflight-ready": "validate_approved_adapter_benchmark",
    "authorized-cn-ready-for-filing": "validate_authorized_ready_benchmark",
    "case-processor-dry-run": "validate_case_processor_benchmark",
    "case-lifecycle-rejection-gate": "validate_case_lifecycle_rejection_benchmark",
    "case-lifecycle-trace-mock": "validate_case_lifecycle_benchmark",
    "generated-case-lifecycle-trace": "validate_case_lifecycle_benchmark",
    "case-package-orchestration-dry-run": "validate_case_intake_orchestration_benchmark",
    "case-package-intake-dry-run": "validate_case_package_benchmark",
    "disclosure-confirmation-rejection": "validate_disclosure_confirmation_rejection_benchmark",
    "disclosure-normalization-scaffold": "validate_disclosure_normalization_benchmark",
    "draft-evidence-provenance-gate": "validate_draft_evidence_provenance_benchmark",
    "draft-reference-delta-evidence-provenance": "validate_draft_evidence_provenance_benchmark",
    "draft-package-generation": "validate_draft_package_generation_benchmark",
    "draft-package-reference-delta": "validate_draft_package_generation_benchmark",
    "draft-package-to-filing-validation": "validate_validated_filing_package_benchmark",
    "draft-to-filing-package-validation": "validate_draft_to_package_benchmark",
    "inbox-handoff-index": "validate_inbox_handoff_index_benchmark",
    "inbox-to-handoff": "validate_inbox_to_handoff_benchmark",
    "inbox-to-handoff-rejection": "validate_inbox_to_handoff_rejection_benchmark",
    "incoming-disclosure-to-application": "validate_incoming_application_benchmark",
    "official-channel-preflight-to-ready": "validate_official_ready_benchmark",
    "official-ready-to-approved-adapter-preflight": "validate_generated_approved_adapter_preflight_benchmark",
    "receipt-capture-mock": "validate_receipt_capture_benchmark",
    "submitted-pending-receipt-to-official-receipt": "validate_generated_receipt_capture_benchmark",
    "scaffold-confirmation-to-disclosure": "validate_scaffold_confirmation_benchmark",
    "smart-appliance-cn13": "validate_benchmark_gate",
    "source-material-file-binding-rejection": "validate_source_material_file_binding_rejection_benchmark",
    "skill-completion-audit": "validate_skill_completion_audit_benchmark",
    "validated-package-to-official-ready": "validate_ready_for_authorized_filing_benchmark",
    "workflow-orchestration-dry-run": "validate_workflow_orchestration_benchmark",
}


def utc_plus_8_now() -> str:
    tz = dt.timezone(dt.timedelta(hours=8))
    return dt.datetime.now(tz=tz).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relpath(path: Path, base: Path) -> str:
    resolved = path.resolve()
    try:
        return os.path.relpath(resolved, base.resolve()).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def find_case_record(case_folder: Path) -> tuple[Path | None, dict[str, Any], str]:
    inbox_handoff_index = case_folder / "inbox-handoff-index.json"
    inbox_handoff_index_report = case_folder / "inbox-handoff-index.md"
    if inbox_handoff_index.exists() and inbox_handoff_index_report.exists():
        packet = load_json(inbox_handoff_index)
        return inbox_handoff_index, {
            "case_id": packet.get("index_id") or packet.get("inbox_id"),
            "status": packet.get("status") or "approved_for_adapter_execution",
            "target_status": packet.get("status") or "approved_for_adapter_execution",
            "legal_gate_mode": packet.get("legal_gate_mode"),
            "external_lawyer_involved": packet.get("external_lawyer_involved") is True,
            "case_owner": "Inbox handoff index operator",
        }, "inbox-handoff-index.json"

    skill_completion_audit = case_folder / "skill-completion-audit.json"
    skill_completion_audit_report = case_folder / "skill-completion-audit.md"
    if skill_completion_audit.exists() and skill_completion_audit_report.exists():
        packet = load_json(skill_completion_audit)
        return skill_completion_audit, {
            "case_id": packet.get("audit_id") or case_folder.name,
            "status": packet.get("status") or "approved_for_adapter_execution",
            "target_status": packet.get("status") or "approved_for_adapter_execution",
            "legal_gate_mode": packet.get("legal_gate_mode"),
            "external_lawyer_involved": packet.get("external_lawyer_involved") is True,
            "case_owner": "Skill completion audit operator",
        }, "skill-completion-audit.json"

    inbox_to_handoff = case_folder / "inbox-to-handoff-result.json"
    inbox_to_handoff_report = case_folder / "inbox-to-handoff-report.md"
    if inbox_to_handoff.exists() and inbox_to_handoff_report.exists():
        packet = load_json(inbox_to_handoff)
        return inbox_to_handoff, {
            "case_id": packet.get("inbox_id"),
            "status": packet.get("status") or "approved_for_adapter_execution",
            "target_status": packet.get("status") or "approved_for_adapter_execution",
            "legal_gate_mode": packet.get("legal_gate_mode"),
            "external_lawyer_involved": packet.get("external_lawyer_involved") is True,
            "case_owner": "Inbox to handoff orchestrator",
        }, "inbox-to-handoff-result.json"

    workflow_queue = case_folder / "case-queue.json"
    workflow_result = case_folder / "batch-processor-result.json"
    if workflow_queue.exists() and workflow_result.exists():
        queue = load_json(workflow_queue)
        owner = (
            "Case intake orchestration operator"
            if (case_folder / "intake-orchestration-report.md").exists()
            else "Workflow orchestration operator"
        )
        return workflow_queue, {
            "case_id": queue.get("queue_id"),
            "status": "intake_received",
            "target_status": "intake_received",
            "case_owner": owner,
        }, "case-queue.json"

    package_manifest = case_folder / "case-package-manifest.json"
    if package_manifest.exists():
        manifest = load_json(package_manifest)
        return package_manifest, {
            "case_id": manifest.get("case_id"),
            "status": manifest.get("package_status") or "intake_received",
            "target_status": manifest.get("package_status") or "intake_received",
            "case_owner": "Case package intake operator",
        }, "case-package-manifest.json"

    abnormal_rejection_cases = case_folder / "rejection-cases.json"
    if abnormal_rejection_cases.exists() and case_folder.name == "abnormal-filing-risk-rejection":
        packet = load_json(abnormal_rejection_cases)
        return abnormal_rejection_cases, {
            "case_id": packet.get("case_id") or case_folder.name,
            "status": "draft_only",
            "target_status": "draft_only",
            "case_owner": "Abnormal filing risk rejection tester",
        }, "rejection-cases.json"

    ai_binding_rejection_cases = case_folder / "rejection-cases.json"
    if ai_binding_rejection_cases.exists() and case_folder.name == "ai-self-filing-abnormal-risk-binding-rejection":
        packet = load_json(ai_binding_rejection_cases)
        return ai_binding_rejection_cases, {
            "case_id": packet.get("case_id") or case_folder.name,
            "status": "draft_only",
            "target_status": "draft_only",
            "case_owner": "AI self-filing abnormal risk binding rejection tester",
        }, "rejection-cases.json"

    ai_materials_rejection_cases = case_folder / "rejection-cases.json"
    if ai_materials_rejection_cases.exists() and case_folder.name == "ai-self-filing-application-materials-binding-rejection":
        packet = load_json(ai_materials_rejection_cases)
        return ai_materials_rejection_cases, {
            "case_id": packet.get("case_id") or case_folder.name,
            "status": "package_valid_official_preflight_pending",
            "target_status": "package_valid_official_preflight_pending",
            "case_owner": "AI self-filing application materials binding rejection tester",
        }, "rejection-cases.json"

    materials_rejection_cases = case_folder / "rejection-cases.json"
    if materials_rejection_cases.exists() and case_folder.name == "patent-application-materials-rejection":
        packet = load_json(materials_rejection_cases)
        return materials_rejection_cases, {
            "case_id": packet.get("case_id") or case_folder.name,
            "status": "package_valid_official_preflight_pending",
            "target_status": "package_valid_official_preflight_pending",
            "case_owner": "Patent application materials rejection tester",
        }, "rejection-cases.json"

    handoff_rejection_cases = case_folder / "rejection-cases.json"
    if handoff_rejection_cases.exists() and case_folder.name == "pre-submission-handoff-rejection":
        packet = load_json(handoff_rejection_cases)
        return handoff_rejection_cases, {
            "case_id": packet.get("case_id") or case_folder.name,
            "status": "approved_for_adapter_execution",
            "target_status": "approved_for_adapter_execution",
            "case_owner": "Pre-submission handoff rejection tester",
        }, "rejection-cases.json"

    inbox_rejection_cases = case_folder / "rejection-cases.json"
    if inbox_rejection_cases.exists() and case_folder.name == "inbox-to-handoff-rejection":
        packet = load_json(inbox_rejection_cases)
        return inbox_rejection_cases, {
            "case_id": packet.get("case_id") or case_folder.name,
            "status": "approved_for_adapter_execution",
            "target_status": "approved_for_adapter_execution",
            "case_owner": "Inbox to handoff rejection tester",
        }, "rejection-cases.json"

    disclosure_rejection_cases = case_folder / "rejection-cases.json"
    if disclosure_rejection_cases.exists() and case_folder.name == "disclosure-confirmation-rejection":
        packet = load_json(disclosure_rejection_cases)
        return disclosure_rejection_cases, {
            "case_id": packet.get("case_id") or case_folder.name,
            "status": "intake_received",
            "target_status": "intake_received",
            "case_owner": "Disclosure confirmation rejection tester",
        }, "rejection-cases.json"

    lifecycle_trace = case_folder / "case-lifecycle-trace.json"
    if lifecycle_trace.exists():
        trace = load_json(lifecycle_trace)
        return lifecycle_trace, {
            "case_id": trace.get("case_id"),
            "status": trace.get("final_status"),
            "case_owner": "Lifecycle audit operator",
        }, "case-lifecycle-trace.json"

    production_evidence_report = case_folder / "production-official-evidence-gate-report.md"
    production_shape_packet = case_folder / "production-shape" / "production-official-evidence-packet.json"
    if production_evidence_report.exists() and production_shape_packet.exists():
        packet = load_json(production_shape_packet)
        return production_evidence_report, {
            "case_id": packet.get("case_id"),
            "status": "accepted_or_application_number_received",
            "target_status": "accepted_or_application_number_received",
            "case_owner": "Production official evidence gate operator",
        }, "production-official-evidence-gate-report.md"

    production_adapter_report = case_folder / "production-adapter-readiness-report.md"
    production_adapter_packet = case_folder / "production-shape" / "production-adapter-readiness-packet.json"
    if production_adapter_report.exists() and production_adapter_packet.exists():
        packet = load_json(production_adapter_packet)
        return production_adapter_report, {
            "case_id": packet.get("adapter", {}).get("name") or packet.get("official_system"),
            "status": "ready_for_authorized_filing",
            "target_status": "ready_for_authorized_filing",
            "case_owner": "Production adapter readiness gate operator",
        }, "production-adapter-readiness-report.md"

    official_session_report = case_folder / "official-session-authorization-report.md"
    official_session_packet = case_folder / "production-shape" / "official-session-authorization-packet.json"
    if official_session_report.exists() and official_session_packet.exists():
        packet = load_json(official_session_packet)
        return official_session_report, {
            "case_id": packet.get("official_system") or case_folder.name,
            "status": "ready_for_authorized_filing",
            "target_status": "ready_for_authorized_filing",
            "case_owner": "Official session authorization gate operator",
        }, "official-session-authorization-report.md"

    abnormal_risk = case_folder / "abnormal-filing-risk-assessment.json"
    abnormal_risk_report = case_folder / "abnormal-filing-risk-report.md"
    if abnormal_risk.exists() and abnormal_risk_report.exists():
        packet = load_json(abnormal_risk)
        return abnormal_risk, {
            "case_id": packet.get("case_id"),
            "status": "draft_only",
            "target_status": "draft_only",
            "case_owner": "Abnormal filing risk gate operator",
        }, "abnormal-filing-risk-assessment.json"

    cure_revalidation = case_folder / "cure-revalidation.json"
    cure_revalidation_report = case_folder / "cure-revalidation-report.md"
    if cure_revalidation.exists() and cure_revalidation_report.exists():
        packet = load_json(cure_revalidation)
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return cure_revalidation, {
            "case_id": packet.get("case_id"),
            "status": status.get("status") or packet.get("status") or "ready_for_package_validation",
            "target_status": status.get("status") or packet.get("status") or "ready_for_package_validation",
            "case_owner": "AI self-filing cure revalidation operator",
        }, "cure-revalidation.json"

    draft_provenance = case_folder / "draft-evidence-provenance.json"
    draft_provenance_report = case_folder / "draft-evidence-provenance-report.md"
    if draft_provenance.exists() and draft_provenance_report.exists():
        packet = load_json(draft_provenance)
        return draft_provenance, {
            "case_id": packet.get("case_id"),
            "status": "draft_only",
            "target_status": "draft_only",
            "case_owner": "Draft evidence provenance operator",
        }, "draft-evidence-provenance.json"

    application_materials = case_folder / "application-materials.json"
    application_materials_report = case_folder / "application-materials-report.md"
    if application_materials.exists() and application_materials_report.exists():
        packet = load_json(application_materials)
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return application_materials, {
            "case_id": packet.get("case_id"),
            "status": status.get("status") or "package_valid_official_preflight_pending",
            "target_status": status.get("status") or "package_valid_official_preflight_pending",
            "case_owner": "Patent application materials generator",
        }, "application-materials.json"

    application_materials_quality = case_folder / "application-materials-quality-review.json"
    application_materials_quality_report = case_folder / "application-materials-quality-report.md"
    if application_materials_quality.exists() and application_materials_quality_report.exists():
        packet = load_json(application_materials_quality)
        return application_materials_quality, {
            "case_id": packet.get("case_id"),
            "status": "package_valid_official_preflight_pending",
            "target_status": "package_valid_official_preflight_pending",
            "case_owner": "Application materials quality gate operator",
        }, "application-materials-quality-review.json"

    application_materials_pipeline = case_folder / "application-materials-pipeline-result.json"
    application_materials_pipeline_report = case_folder / "application-materials-pipeline-report.md"
    if application_materials_pipeline.exists() and application_materials_pipeline_report.exists():
        packet = load_json(application_materials_pipeline)
        return application_materials_pipeline, {
            "case_id": packet.get("case_id"),
            "status": "package_valid_official_preflight_pending",
            "target_status": "package_valid_official_preflight_pending",
            "case_owner": "Application materials pipeline operator",
        }, "application-materials-pipeline-result.json"

    pre_submission_to_handoff = case_folder / "pre-submission-to-handoff-result.json"
    pre_submission_to_handoff_report = case_folder / "pre-submission-to-handoff-report.md"
    if pre_submission_to_handoff.exists() and pre_submission_to_handoff_report.exists():
        packet = load_json(pre_submission_to_handoff)
        return pre_submission_to_handoff, {
            "case_id": packet.get("case_id"),
            "status": packet.get("status") or "approved_for_adapter_execution",
            "target_status": packet.get("status") or "approved_for_adapter_execution",
            "legal_gate_mode": packet.get("legal_gate_mode"),
            "external_lawyer_involved": packet.get("external_lawyer_involved") is True,
            "case_owner": "Pre-submission to handoff orchestrator",
        }, "pre-submission-to-handoff-result.json"

    pre_submission_handoff = case_folder / "pre-submission-handoff-package.json"
    pre_submission_handoff_report = case_folder / "pre-submission-handoff-report.md"
    if pre_submission_handoff.exists() and pre_submission_handoff_report.exists():
        packet = load_json(pre_submission_handoff)
        return pre_submission_handoff, {
            "case_id": packet.get("case_id"),
            "status": packet.get("status") or "approved_for_adapter_execution",
            "target_status": packet.get("status") or "approved_for_adapter_execution",
            "legal_gate_mode": packet.get("legal_gate_mode"),
            "external_lawyer_involved": packet.get("external_lawyer_involved") is True,
            "case_owner": "Pre-submission handoff package operator",
        }, "pre-submission-handoff-package.json"

    pre_submission_pipeline = case_folder / "pre-submission-pipeline-result.json"
    pre_submission_pipeline_report = case_folder / "pre-submission-pipeline-report.md"
    if pre_submission_pipeline.exists() and pre_submission_pipeline_report.exists():
        packet = load_json(pre_submission_pipeline)
        return pre_submission_pipeline, {
            "case_id": packet.get("case_id"),
            "status": packet.get("status") or "package_valid_official_preflight_pending",
            "target_status": packet.get("status") or "package_valid_official_preflight_pending",
            "case_owner": "Pre-submission pipeline operator",
        }, "pre-submission-pipeline-result.json"

    case_record = case_folder / "case-record.json"
    if case_record.exists():
        return case_record, load_json(case_record), "case-record.json"

    draft_package = case_folder / "patent-application-draft.md"
    claim_support_map = case_folder / "claim-support-map.md"
    draft_package_report = case_folder / "draft-package-report.md"
    if draft_package.exists() and claim_support_map.exists() and draft_package_report.exists():
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return draft_package, {
            "case_id": status.get("case_id") or case_folder.name,
            "status": "draft_only",
            "target_status": "draft_only",
            "case_owner": "Draft package generator",
        }, "patent-application-draft.md"

    filing_manifest = case_folder / "filing-package-manifest.yaml"
    package_report = case_folder / "package-validation-report.md"
    ai_self_filing_report = case_folder / "ai-self-filing-package-report.md"
    if filing_manifest.exists() and (package_report.exists() or ai_self_filing_report.exists()):
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return filing_manifest, {
            "case_id": status.get("case_id") or case_folder.name,
            "status": status.get("status") or "package_valid_official_preflight_pending",
            "target_status": status.get("status") or "package_valid_official_preflight_pending",
            "case_owner": "AI self-filing package validation operator"
            if ai_self_filing_report.exists()
            else "Filing package validation operator",
        }, "filing-package-manifest.yaml"

    official_preflight = case_folder / "official-channel-preflight.yaml"
    readiness_report = case_folder / "readiness-report.md"
    if official_preflight.exists() and readiness_report.exists():
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return official_preflight, {
            "case_id": status.get("case_id") or case_folder.name,
            "status": status.get("status") or "ready_for_authorized_filing",
            "target_status": status.get("status") or "ready_for_authorized_filing",
            "case_owner": "Official channel preflight operator",
        }, "official-channel-preflight.yaml"

    approved_adapter_preflight = case_folder / "approved-adapter-preflight.json"
    adapter_report = case_folder / "adapter-boundary-report.md"
    if approved_adapter_preflight.exists() and adapter_report.exists():
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return approved_adapter_preflight, {
            "case_id": status.get("case_id") or case_folder.name,
            "status": status.get("status") or "approved_for_adapter_execution",
            "target_status": status.get("status") or "approved_for_adapter_execution",
            "case_owner": "Approved adapter preflight operator",
        }, "approved-adapter-preflight.json"

    adapter_execution = case_folder / "adapter-execution-result.json"
    adapter_execution_report = case_folder / "adapter-execution-report.md"
    if adapter_execution.exists() and adapter_execution_report.exists():
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return adapter_execution, {
            "case_id": status.get("case_id") or case_folder.name,
            "status": status.get("status") or "submitted_pending_receipt",
            "target_status": status.get("status") or "submitted_pending_receipt",
            "case_owner": "Adapter execution result operator",
        }, "adapter-execution-result.json"

    receipt_capture = case_folder / "receipt-capture.yaml"
    receipt_report = case_folder / "receipt-report.md"
    if receipt_capture.exists() and receipt_report.exists():
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return receipt_capture, {
            "case_id": status.get("case_id") or case_folder.name,
            "status": status.get("status") or "official_receipt_received",
            "target_status": status.get("status") or "official_receipt_received",
            "case_owner": "Receipt capture operator",
        }, "receipt-capture.yaml"

    application_evidence = case_folder / "application-number-evidence.json"
    application_report = case_folder / "application-number-report.md"
    if application_evidence.exists() and application_report.exists():
        status = load_json(case_folder / "filing-status.json") if (case_folder / "filing-status.json").exists() else {}
        return application_evidence, {
            "case_id": status.get("case_id") or case_folder.name,
            "status": status.get("status") or "accepted_or_application_number_received",
            "target_status": status.get("status") or "accepted_or_application_number_received",
            "case_owner": "Application number evidence operator",
        }, "application-number-evidence.json"

    confirmed_disclosure = case_folder / "invention-disclosure.json"
    confirmation_report = case_folder / "confirmation-report.md"
    if confirmed_disclosure.exists() and confirmation_report.exists():
        disclosure = load_json(confirmed_disclosure)
        return confirmed_disclosure, {
            "case_id": disclosure.get("case_id"),
            "status": "draft_only",
            "target_status": "draft_only",
            "case_owner": "Disclosure confirmation operator",
        }, "invention-disclosure.json"

    disclosure_scaffold = case_folder / "invention-disclosure-scaffold.json"
    if disclosure_scaffold.exists():
        scaffold = load_json(disclosure_scaffold)
        return disclosure_scaffold, {
            "case_id": scaffold.get("case_id"),
            "status": "intake_received",
            "target_status": "intake_received",
            "case_owner": "Disclosure normalization operator",
        }, "invention-disclosure-scaffold.json"

    filing_status = case_folder / "filing-status.json"
    if filing_status.exists():
        return filing_status, load_json(filing_status), "filing-status.json"

    return None, {}, ""


def infer_status(record: dict[str, Any]) -> str:
    return str(record.get("current_status") or record.get("status") or "intake_received")


def infer_target_status(record: dict[str, Any], current_status: str) -> str:
    return str(record.get("target_status") or current_status)


def infer_case_id(case_folder: Path, record: dict[str, Any]) -> str:
    return str(record.get("case_id") or case_folder.name)


def infer_owner(record: dict[str, Any], default_owner: str) -> str:
    return str(
        record.get("case_owner")
        or record.get("filing_owner")
        or record.get("owner")
        or default_owner
    )


def infer_legal_gate_mode(case_folder: Path, record: dict[str, Any]) -> str:
    explicit = record.get("legal_gate_mode")
    if explicit:
        return str(explicit)
    if (
        (case_folder / "ai-self-filing-package-report.md").exists()
        or (case_folder / "ai-self-filing-authorization-packet.json").exists()
        or "ai-self-filing" in case_folder.name
    ):
        return "ai_self_filing_no_external_lawyer"
    if (
        (case_folder / "submission-authorization-packet.json").exists()
        or (case_folder / "submission-packet.json").exists()
        or (case_folder / "package-validation-report.md").exists()
    ):
        return "counsel_or_agent_review"
    return "ai_self_filing_no_external_lawyer"


def infer_external_lawyer_involved(record: dict[str, Any]) -> bool:
    return bool(record.get("external_lawyer_involved") is True)


def infer_expected_outcome(record: dict[str, Any], current_status: str, target_status: str) -> str:
    legal_gate = str(record.get("legal_gate") or "")
    decision = str(record.get("decision") or "")

    if record.get("case_owner") == "Draft evidence provenance operator":
        return "draft_evidence_provenance"
    if record.get("case_owner") == "Abnormal filing risk gate operator":
        return "abnormal_filing_risk"
    if record.get("case_owner") == "Abnormal filing risk rejection tester":
        return "abnormal_filing_risk_rejection"
    if record.get("case_owner") == "AI self-filing abnormal risk binding rejection tester":
        return "ai_self_filing_abnormal_risk_binding_rejection"
    if record.get("case_owner") == "AI self-filing application materials binding rejection tester":
        return "ai_self_filing_application_materials_binding_rejection"
    if record.get("case_owner") == "Patent application materials rejection tester":
        return "patent_application_materials_rejection"
    if record.get("case_owner") == "Inbox handoff index operator":
        return "inbox_handoff_index"
    if record.get("case_owner") == "Skill completion audit operator":
        return "skill_completion_audit"
    if record.get("case_owner") == "Pre-submission handoff rejection tester":
        return "pre_submission_handoff_rejection"
    if record.get("case_owner") == "Inbox to handoff rejection tester":
        return "inbox_to_handoff_rejection"
    if record.get("case_owner") == "Disclosure confirmation rejection tester":
        return "disclosure_confirmation_rejection"
    if legal_gate == "failed" or decision in {"do_not_file", "legal_gate_failed"}:
        return "deficiency"
    if record.get("case_owner") == "Case package intake operator":
        return "case_package_intake"
    if record.get("case_owner") == "Disclosure normalization operator":
        return "disclosure_scaffold"
    if record.get("case_owner") == "Disclosure confirmation operator":
        return "confirmed_disclosure"
    if record.get("case_owner") == "Draft package generator":
        return "draft_package"
    if record.get("case_owner") == "Filing package validation operator":
        return "package_validation"
    if record.get("case_owner") == "AI self-filing package validation operator":
        return "ai_self_filing_package_validation"
    if record.get("case_owner") == "Patent application materials generator":
        return "patent_application_materials"
    if record.get("case_owner") == "Application materials quality gate operator":
        return "application_materials_quality"
    if record.get("case_owner") == "Application materials pipeline operator":
        return "application_materials_pipeline"
    if record.get("case_owner") == "Inbox to handoff orchestrator":
        return "inbox_to_handoff"
    if record.get("case_owner") == "Pre-submission to handoff orchestrator":
        return "pre_submission_to_handoff"
    if record.get("case_owner") == "Pre-submission handoff package operator":
        return "pre_submission_handoff_package"
    if record.get("case_owner") == "Pre-submission pipeline operator":
        return "pre_submission_pipeline"
    if record.get("case_owner") == "Approved adapter preflight operator":
        return "approved_adapter_preflight"
    if record.get("case_owner") == "Adapter execution result operator":
        return "adapter_execution"
    if record.get("case_owner") == "Receipt capture operator":
        return "receipt_capture"
    if record.get("case_owner") == "Application number evidence operator":
        return "application_number"
    if record.get("case_owner") == "Production official evidence gate operator":
        return "production_official_evidence"
    if record.get("case_owner") == "Production adapter readiness gate operator":
        return "production_adapter_readiness"
    if record.get("case_owner") == "Official session authorization gate operator":
        return "official_session_authorization"
    if record.get("case_owner") == "AI self-filing cure revalidation operator":
        return "ai_self_filing_cure_revalidation"
    if target_status == "draft_only" or current_status == "draft_only":
        return "deficiency"
    if target_status == "package_valid_official_preflight_pending":
        return "official_preflight"
    if target_status == "ready_for_authorized_filing":
        return "handoff"
    if target_status == "approved_for_adapter_execution":
        return "approved_adapter_preflight"
    if target_status == "submitted_pending_receipt":
        return "adapter_execution"
    if record.get("case_owner") == "Workflow orchestration operator":
        return "workflow_orchestration"
    if record.get("case_owner") == "Case intake orchestration operator":
        return "case_intake_orchestration"
    if record.get("case_owner") == "Lifecycle audit operator":
        return "lifecycle_audit"
    if current_status in {"official_receipt_received", "accepted_or_application_number_received"}:
        return "application_number" if current_status == "accepted_or_application_number_received" else "blocked"
    return "package_validation"


def infer_validators(case_folder: Path) -> list[str]:
    if case_folder.name in FOLDER_VALIDATORS:
        return [FOLDER_VALIDATORS[case_folder.name]]
    if (case_folder / "case-queue.json").exists() and (case_folder / "batch-processor-result.json").exists():
        return ["validate_workflow_orchestration_benchmark"]
    if (case_folder / "case-lifecycle-trace.json").exists() and (case_folder / "lifecycle-report.md").exists():
        return ["validate_case_lifecycle_benchmark"]
    if (case_folder / "draft-package-report.md").exists():
        return ["validate_draft_package_generation_benchmark"]
    if (case_folder / "filing-package-manifest.yaml").exists() and (case_folder / "package-validation-report.md").exists():
        return ["validate_validated_filing_package_benchmark"]
    if (case_folder / "filing-package-manifest.yaml").exists() and (case_folder / "ai-self-filing-package-report.md").exists():
        return ["validate_ai_self_filing_package_benchmark"]
    if (case_folder / "application-materials.json").exists() and (case_folder / "application-materials-report.md").exists():
        return ["validate_patent_application_materials_benchmark"]
    if (case_folder / "application-materials-quality-review.json").exists() and (case_folder / "application-materials-quality-report.md").exists():
        return ["validate_application_materials_quality_benchmark"]
    if (case_folder / "application-materials-pipeline-result.json").exists() and (case_folder / "application-materials-pipeline-report.md").exists():
        return ["validate_application_materials_pipeline_benchmark"]
    if (case_folder / "inbox-handoff-index.json").exists() and (case_folder / "inbox-handoff-index.md").exists():
        return ["validate_inbox_handoff_index_benchmark"]
    if (case_folder / "skill-completion-audit.json").exists() and (case_folder / "skill-completion-audit.md").exists():
        return ["validate_skill_completion_audit_benchmark"]
    if (case_folder / "inbox-to-handoff-result.json").exists() and (case_folder / "inbox-to-handoff-report.md").exists():
        return ["validate_inbox_to_handoff_benchmark"]
    if (case_folder / "pre-submission-to-handoff-result.json").exists() and (case_folder / "pre-submission-to-handoff-report.md").exists():
        return ["validate_pre_submission_to_handoff_benchmark"]
    if (case_folder / "pre-submission-handoff-package.json").exists() and (case_folder / "pre-submission-handoff-report.md").exists():
        return ["validate_pre_submission_handoff_package"]
    if (case_folder / "pre-submission-pipeline-result.json").exists() and (case_folder / "pre-submission-pipeline-report.md").exists():
        return ["validate_pre_submission_pipeline_benchmark"]
    if (case_folder / "official-channel-preflight.yaml").exists() and (case_folder / "readiness-report.md").exists():
        return ["validate_ready_for_authorized_filing_benchmark"]
    if (case_folder / "approved-adapter-preflight.json").exists() and (case_folder / "adapter-boundary-report.md").exists():
        return ["validate_generated_approved_adapter_preflight_benchmark"]
    if (case_folder / "adapter-execution-result.json").exists() and (case_folder / "adapter-execution-report.md").exists():
        if (case_folder / "adapter-execution-source.json").exists():
            return ["validate_generated_adapter_execution_result_benchmark"]
        return ["validate_adapter_execution_benchmark"]
    if (case_folder / "receipt-capture.yaml").exists() and (case_folder / "receipt-report.md").exists():
        if (case_folder / "receipt-capture-source.json").exists():
            return ["validate_generated_receipt_capture_benchmark"]
        return ["validate_receipt_capture_benchmark"]
    if (case_folder / "application-number-evidence.json").exists() and (case_folder / "application-number-report.md").exists():
        if (case_folder / "application-number-source.json").exists():
            return ["validate_generated_application_number_benchmark"]
        return ["validate_application_number_benchmark"]
    if (case_folder / "production-official-evidence-gate-report.md").exists():
        return ["validate_production_official_evidence_gate_benchmark"]
    if (case_folder / "production-adapter-readiness-report.md").exists():
        return ["validate_production_adapter_readiness_benchmark"]
    if (case_folder / "official-session-authorization-report.md").exists():
        return ["validate_official_session_authorization_benchmark"]
    if (case_folder / "invention-disclosure.json").exists() and (case_folder / "confirmation-report.md").exists():
        return ["validate_invention_disclosure"]
    if (case_folder / "patent-application-draft.md").exists() and (case_folder / "claim-support-map.md").exists():
        return ["validate_patent_application_draft", "validate_claim_support_map"]
    if (case_folder / "invention-disclosure-scaffold.json").exists():
        return ["validate_invention_disclosure_scaffold"]
    if (case_folder / "case-package-manifest.json").exists():
        return ["validate_case_package_manifest"]
    if (case_folder / "case-record.json").exists():
        return ["validate_case_record"]
    if (case_folder / "source-material-manifest.yaml").exists():
        return ["validate_source_material_manifest"]
    if (case_folder / "submission-packet.json").exists():
        return ["validate_submission_packet"]
    return ["validate_case_queue"]


def build_queue(
    case_folders: list[Path],
    output_base: Path,
    queue_id: str,
    queue_owner: str,
    execution_mode: str,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for index, folder in enumerate(case_folders, start=1):
        case_folder = folder.resolve()
        record_path, record, record_name = find_case_record(case_folder)
        current_status = infer_status(record)
        target_status = infer_target_status(record, current_status)
        legal_gate_mode = infer_legal_gate_mode(case_folder, record)

        items.append(
            {
                "case_id": infer_case_id(case_folder, record),
                "priority": index,
                "current_status": current_status,
                "target_status": target_status,
                "legal_gate_mode": legal_gate_mode,
                "external_lawyer_involved": infer_external_lawyer_involved(record),
                "case_record": relpath(record_path, output_base) if record_path else "",
                "case_folder": relpath(case_folder, output_base),
                "expected_outcome": infer_expected_outcome(record, current_status, target_status),
                "owner": infer_owner(record, queue_owner),
                "required_validators": infer_validators(case_folder),
                "notes": f"Generated from {record_name or 'case folder'} by build_case_queue.py.",
            }
        )

    queue = {
        "queue_id": queue_id,
        "created_at": utc_plus_8_now(),
        "execution_mode": execution_mode,
        "official_submission_allowed": False,
        "official_system_touch_allowed": False,
        "queue_owner": queue_owner,
        "items": items,
    }
    if execution_mode == "approved_adapter":
        queue["approved_adapter_evidence_mode"] = True
    return queue


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_folders", nargs="+", type=Path)
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--queue-owner", default="Patent Capital OS")
    parser.add_argument("--execution-mode", choices=["dry_run", "handoff", "approved_adapter"], default="dry_run")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output_base = args.output.resolve().parent if args.output else Path.cwd()
    queue = build_queue(
        case_folders=args.case_folders,
        output_base=output_base,
        queue_id=args.queue_id,
        queue_owner=args.queue_owner,
        execution_mode=args.execution_mode,
    )
    ok, errors, warnings = validate_case_queue.validate(queue)
    rendered = json.dumps(queue, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(rendered)
    if warnings:
        print(json.dumps({"warnings": warnings}, ensure_ascii=False), file=sys.stderr)
    if errors:
        print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
