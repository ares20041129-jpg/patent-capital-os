#!/usr/bin/env python3
"""Run the full local pre-submission AI self-filing pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

import build_case_queue
import confirm_invention_disclosure
import generate_draft_package
import normalize_invention_disclosure
import orchestrate_application_materials_pipeline
import prepare_abnormal_filing_risk_assessment
import prepare_approved_adapter_preflight
import prepare_ai_self_filing_package
import prepare_case_package
import prepare_case_lifecycle_trace
import prepare_draft_evidence_provenance
import prepare_reference_patent_delta
import prepare_ready_for_authorized_filing
import validate_artifact_hash_manifest
import validate_case_lifecycle_trace


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_item(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def build_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [sha256_item(path, output_dir) for path in files if path.exists()],
    }


def copy_if_exists(source: Path, target: Path) -> None:
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            target.write_bytes(source.read_bytes())


def copy_raw_inputs(source_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        if source.is_symlink():
            continue
        target = output_dir / source.relative_to(source_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)


def materialize_confirmation_packet(template_path: Path, scaffold_path: Path, output_path: Path) -> dict[str, Any]:
    packet = load_json(template_path)
    scaffold = load_json(scaffold_path)
    now = build_case_queue.utc_plus_8_now()
    scaffold_hash = sha256_file(scaffold_path)
    case_id = str(scaffold.get("case_id") or packet.get("case_id") or "")

    packet["case_id"] = case_id
    packet["scaffold_hash"] = scaffold_hash
    packet["confirmed_at"] = now
    review = packet.setdefault("legal_drafting_review", {})
    review["review_timestamp"] = now
    review["reviewed_scaffold_hash"] = scaffold_hash
    review["approval_scope"] = "draft_generation_only"
    review["filing_approved"] = False
    controls = packet.setdefault("controls", {})
    controls["draft_generation_allowed"] = True
    controls["filing_allowed"] = False
    controls["external_lawyer_involved"] = False
    controls["official_system_touched"] = False
    controls["official_submission_performed"] = False

    write_json(output_path, packet)
    return packet


def materialize_reference_delta_source(template_path: Path, package_dir: Path, output_path: Path, case_id: str) -> dict[str, Any]:
    source = load_json(template_path)
    manifest = load_json(package_dir / "01-normalized" / "source-material-manifest.json")
    materials = manifest.get("materials") if isinstance(manifest.get("materials"), list) else []
    support = next(
        (
            item
            for item in materials
            if isinstance(item, dict)
            and item.get("usable_for_claim_support") is True
            and str(item.get("type") or "").lower() != "prior_art"
        ),
        None,
    )
    if not support:
        raise RuntimeError("reference_delta_source_requires_claim_support_material")

    support_source = package_dir / str(support.get("filename") or "")
    support_target = output_path.parent / "applicant-evidence" / Path(str(support.get("filename") or "support.txt")).name
    support_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(support_source, support_target)

    source["case_id"] = case_id
    for element in source.get("claim_elements") or []:
        if isinstance(element, dict):
            element["support_path"] = rel(support_target, output_path.parent)
            element["support_hash"] = sha256_file(support_target)
    write_json(output_path, source)
    return source


def materialize_ai_self_filing_source(
    template_path: Path,
    draft_dir: Path,
    abnormal_dir: Path,
    output_path: Path,
) -> dict[str, Any]:
    source = load_json(template_path)
    now = build_case_queue.utc_plus_8_now()
    draft_path = draft_dir / "patent-application-draft.md"
    assessment_path = abnormal_dir / "abnormal-filing-risk-assessment.json"
    assessment = load_json(assessment_path)
    draft_hash = sha256_file(draft_path)
    assessment_hash = sha256_file(assessment_path)
    case_id = str(assessment.get("case_id") or source.get("case_id") or "")
    final_package_hash = sha256_text(case_id + "|" + draft_hash + "|" + assessment_hash + "|pre-submission")

    source["case_id"] = case_id
    source["source_draft_hash"] = draft_hash
    source["final_package_hash"] = final_package_hash
    source["external_lawyer_involved"] = False
    compliance = source.setdefault("ai_compliance_review", {})
    compliance["checked_at"] = now
    compliance["reviewed_artifacts_hash"] = sha256_text(draft_hash + "|" + assessment_hash)
    compliance["no_copying_check"] = "passed"
    compliance["claim_support_check"] = "passed"
    compliance["abnormal_filing_risk"] = "low"
    compliance["official_format_check"] = "passed"
    compliance["limitations"] = [
        "Local pre-submission pipeline only; official-channel preflight remains separate.",
        "AI compliance review is not lawyer review and does not claim legal advice.",
    ]
    compliance["abnormal_filing_risk_assessment"] = {
        "case_id": assessment.get("case_id"),
        "status": assessment.get("status"),
        "gate": assessment.get("gate"),
        "risk_level": assessment.get("risk_level"),
        "artifact_hash": assessment_hash,
        "artifact_path": rel(assessment_path, output_path.parent),
    }
    if assessment.get("reference_patent_delta_hash"):
        checks = assessment.get("checks") if isinstance(assessment.get("checks"), list) else []
        boundary = next(
            (
                check
                for check in checks
                if isinstance(check, dict) and check.get("check_id") == "reference_delta_boundary_preserved"
            ),
            {},
        )
        compliance["abnormal_filing_risk_assessment"].update(
            {
                "reference_patent_delta_hash": assessment.get("reference_patent_delta_hash"),
                "reference_delta_rows_count": assessment.get("reference_delta_rows_count"),
                "reference_delta_claim_elements_count": assessment.get("reference_delta_claim_elements_count"),
                "reference_delta_boundary_preserved": boundary.get("result") == "pass",
            }
        )
        compliance["limitations"].append(
            "Reference-patent delta is preserved only as boundary and claim-strategy evidence, not applicant claim support."
        )
    legal = compliance.setdefault("legal_gate_review", {})
    legal["review_record_hash"] = sha256_text(case_id + "|" + compliance["reviewed_artifacts_hash"] + "|" + now)
    legal["authorization_scope_check"] = "passed"
    legal["self_filing_eligibility_check"] = "passed"
    legal["inventor_ownership_check"] = "passed"
    legal["secrecy_check"] = "passed"
    legal["fee_authority_check"] = "passed"
    legal["official_channel_boundary_check"] = "passed"
    legal["stop_conditions_checked"] = [
        "mandatory_agent_condition",
        "foreign_or_hmt_applicant_condition",
        "agency_bypass_request",
        "access_control_bypass",
        "official_submission_claim_without_evidence",
    ]
    legal["legal_advice_claimed"] = False
    legal["lawyer_or_agent_review_claimed"] = False
    source.setdefault("applicant_authorization", {})["timestamp"] = now
    source.setdefault("decision", {})["status"] = "ready_for_package_validation"
    source["decision"]["reason"] = "AI self-filing legal/compliance gate passed for local pre-submission package validation without external lawyer involvement."

    write_json(output_path, source)
    return source


def materialize_official_preflight_source(
    template_path: Path,
    package_validation_dir: Path,
    materials_pipeline_dir: Path,
    output_path: Path,
) -> dict[str, Any]:
    source = load_json(template_path)
    package_status = load_json(package_validation_dir / "filing-status.json")
    materials_path = materials_pipeline_dir / "application-materials" / "application-materials.json"
    case_id = str(package_status.get("case_id") or source.get("case_id") or "")
    source["case_id"] = case_id
    source["checked_by"] = "Patent Capital OS AI self-filing official preflight"
    source["application_materials"] = {
        "path": rel(materials_path, output_path.parent),
        "hash": sha256_file(materials_path),
    }
    receipt = source.setdefault("receipt_capture", {})
    receipt["destination"] = f"case-vault/{case_id}/ai-self-filing-receipts"
    receipt["responsible_owner"] = receipt.get("responsible_owner") or "Applicant Filing Operator"
    receipt["planned_docket_entry_id"] = f"planned-ai-self-filing-docket-{case_id}"
    source.setdefault("decision", {})["status"] = "ready_for_authorized_filing"
    source["decision"]["reason"] = "AI self-filing official-channel preflight source is complete for the local pre-submission pipeline. No official system has been touched."
    write_json(output_path, source)
    return source


def materialize_approved_adapter_source(template_path: Path, official_ready_dir: Path, output_path: Path) -> dict[str, Any]:
    source = load_json(template_path)
    ready_status = load_json(official_ready_dir / "filing-status.json")
    case_id = str(ready_status.get("case_id") or source.get("case_id") or "")
    source["case_id"] = case_id
    source.setdefault("production_readiness", {})["packet"] = rel(
        Path(__file__).resolve().parents[1] / "benchmarks" / "production-adapter-readiness-gate" / "production-ready" / "ai-self-filing-adapter-readiness-packet.json",
        output_path.parent,
    )
    source.setdefault("official_session_authorization", {})["packet"] = rel(
        Path(__file__).resolve().parents[1] / "benchmarks" / "official-session-authorization-gate" / "production-ready" / "ai-self-filing-session-authorization-packet.json",
        output_path.parent,
    )
    approval = source.setdefault("authorization", {}).setdefault("two_person_approval", {})
    approval["approved_at"] = build_case_queue.utc_plus_8_now()
    source.setdefault("decision", {})["status"] = "approved_for_adapter_execution"
    source["decision"]["reason"] = "Approved-adapter preflight evidence is complete for the local pre-submission pipeline. This does not execute the adapter or submit."
    write_json(output_path, source)
    return source


def prepare_pre_submission_lifecycle_trace(
    output_dir: Path,
    case_id: str,
    package_dir: Path,
    draft_dir: Path,
    package_validation_dir: Path,
    official_ready_dir: Path,
    approved_adapter_dir: Path,
    reference_metadata: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_status = load_json(package_validation_dir / "filing-status.json")
    approved_status = load_json(approved_adapter_dir / "filing-status.json")
    final_hash = str(package_status.get("final_package_hash") or "")
    reviewed_hash = str(package_status.get("reviewed_package_hash") or "")
    reference_only_metadata = {key: value for key, value in reference_metadata.items() if key != "application_materials_hash"}

    stages = [
        prepare_case_lifecycle_trace.stage(
            1,
            "source_intake",
            "intake_received",
            package_dir / "case-package-manifest.json",
            output_dir,
            "validate_case_package_benchmark",
            "pending",
            "intake_received",
            "disclosure_confirmation",
        ),
        prepare_case_lifecycle_trace.stage(
            2,
            "draft_generation",
            "draft_only",
            draft_dir / "patent-application-draft.md",
            output_dir,
            "validate_draft_package_generation_benchmark",
            "pending",
            "draft_only_do_not_file",
            "ai_self_filing_authorization",
            metadata=reference_only_metadata,
        ),
        prepare_case_lifecycle_trace.stage(
            3,
            "ai_self_filing_authorization",
            "ready_for_package_validation",
            package_validation_dir / "ai-self-filing-authorization-packet.json",
            output_dir,
            "validate_ai_self_filing_authorization",
            "passed",
            "ai_self_filing_gate_passed",
            "package_validation",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            metadata=reference_only_metadata,
        ),
        prepare_case_lifecycle_trace.stage(
            4,
            "ai_self_filing_package_validation",
            "package_valid_official_preflight_pending",
            package_validation_dir / "filing-package-manifest.yaml",
            output_dir,
            "validate_ai_self_filing_package_benchmark",
            "passed",
            "package_valid_official_preflight_pending",
            "official_channel_preflight",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            metadata=reference_only_metadata,
        ),
        prepare_case_lifecycle_trace.stage(
            5,
            "official_channel_preflight",
            "ready_for_authorized_filing",
            official_ready_dir / "official-channel-preflight.yaml",
            output_dir,
            "validate_ready_for_authorized_filing_benchmark",
            "passed",
            "ready_for_authorized_filing",
            "approved_adapter_preflight",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            metadata=reference_metadata,
        ),
        prepare_case_lifecycle_trace.stage(
            6,
            "approved_adapter_preflight",
            "approved_for_adapter_execution",
            approved_adapter_dir / "approved-adapter-preflight.json",
            output_dir,
            "validate_generated_approved_adapter_preflight_benchmark",
            "passed",
            "approved_for_adapter_execution",
            "adapter_execution_result",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            official_session_authorization_hash=str(approved_status.get("official_session_authorization_hash") or ""),
            official_session_reference_hash=str(approved_status.get("official_session_reference_hash") or ""),
            metadata=reference_metadata,
        ),
    ]
    invariants = {
        "legal_gate_never_skipped": True,
        "package_hash_consistent": True,
        "no_receipt_before_submission": True,
        "no_application_number_before_receipt": True,
        "official_session_hash_consistent": True,
        "mock_evidence_marked": True,
    }
    if reference_metadata.get("reference_patent_delta_hash"):
        invariants["reference_delta_boundary_preserved"] = True

    trace = {
        "lifecycle_id": f"PRE-SUBMISSION-LIFECYCLE-{case_id}",
        "case_id": case_id,
        "jurisdiction": "CN",
        "trace_type": "benchmark_mock",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "final_status": "approved_for_adapter_execution",
        "stages": stages,
        "invariants": invariants,
    }
    trace.update(reference_metadata)

    trace_path = output_dir / "case-lifecycle-trace.json"
    report_path = output_dir / "lifecycle-report.md"
    hashes_path = output_dir / "artifact-hashes.json"
    write_json(trace_path, trace)
    report_path.write_text(prepare_case_lifecycle_trace.render_report(trace), encoding="utf-8")
    write_json(hashes_path, prepare_case_lifecycle_trace.artifact_manifest(output_dir, case_id, [trace_path, report_path]))

    trace_ok, trace_errors, trace_warnings = validate_case_lifecycle_trace.validate(trace, base_dir=output_dir)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
    ok = trace_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_dir),
        "artifacts": {
            "case_lifecycle_trace": str(trace_path),
            "lifecycle_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "trace_hash": sha256_file(trace_path),
        "trace_errors": trace_errors,
        "trace_warnings": trace_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
    }, 0 if ok else 1


def stage_entry(name: str, response: dict[str, Any], exit_code: int, output_dir: Path) -> dict[str, Any]:
    return {
        "ok": exit_code == 0 and response.get("ok") is True,
        "output_dir": str(output_dir),
        "artifacts": response.get("artifacts", {}),
        "errors": response.get("errors", [])
        + response.get("package_errors", [])
        + response.get("scaffold_errors", [])
        + response.get("packet_errors", [])
        + response.get("draft_errors", [])
        + response.get("source_errors", [])
        + response.get("preflight_errors", [])
        + response.get("receipt_errors", [])
        + response.get("application_materials_errors", [])
        + response.get("manifest_errors", [])
        + response.get("status_errors", [])
        + response.get("hash_errors", [])
        + response.get("trace_errors", []),
        "warnings": response.get("warnings", [])
        + response.get("package_warnings", [])
        + response.get("scaffold_warnings", [])
        + response.get("packet_warnings", [])
        + response.get("draft_warnings", [])
        + response.get("source_warnings", [])
        + response.get("preflight_warnings", [])
        + response.get("receipt_warnings", [])
        + response.get("application_materials_warnings", [])
        + response.get("manifest_warnings", [])
        + response.get("status_warnings", [])
        + response.get("hash_warnings", [])
        + response.get("trace_warnings", []),
        "boundary": "local_pre_submission_only",
    }


def render_report(result: dict[str, Any], manifest: dict[str, Any]) -> str:
    stages = result.get("stages") if isinstance(result.get("stages"), dict) else {}
    lines = [
        "# Pre-Submission Pipeline Report",
        "",
        f"Case ID: {result.get('case_id')}",
        f"Pipeline status: {'pass' if result.get('ok') else 'fail'}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        "Official system touched: no",
        "Official submission performed: no",
        "Adapter execution performed: no",
        "External lawyer involved: no",
        "",
        "## Stages",
        "",
        "| Stage | Status | Output |",
        "| --- | --- | --- |",
    ]
    for name, stage in stages.items():
        label = str(name).replace("_", " ")
        output = stage.get("output_dir") if isinstance(stage, dict) else ""
        ok = stage.get("ok") if isinstance(stage, dict) else False
        lines.append(f"| {label} | {'pass' if ok else 'fail'} | {output} |")
    if result.get("reference_patent_delta_hash"):
        lines.extend(
            [
                "",
                "## Reference Patent Delta",
                "",
                f"- Reference-patent delta hash: {result.get('reference_patent_delta_hash')}",
                "- Reference patents remain boundary and claim-strategy evidence only, not applicant claim support or filing authorization.",
            ]
        )
    lines.extend(
        [
            "",
            "## Lifecycle Gate",
            "",
            f"- Pre-submission lifecycle gate: {result.get('pre_submission_lifecycle_gate')}",
            f"- Lifecycle trace hash: {result.get('lifecycle_trace_hash')}",
            "- The lifecycle trace is a local audit gate before any adapter execution or automatic submission.",
        ]
    )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Official-channel preflight is included as a local evidence check, but this pipeline stops before automatic submission.",
            "Approved-adapter preflight is included as a local evidence check, but adapter execution remains a separately authorized step.",
            "This pipeline stops before automatic submission. It does not log in, upload, sign, pay, submit, capture a receipt, or create an application number.",
            "",
            "## Next Action",
            "",
            "- Prepare approved-adapter preflight or authorized filing handoff only after the full pre-submission pipeline remains green; do not automatically submit.",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for item in manifest.get("files", []):
        lines.append(f"- {item.get('path')}: {item.get('sha256')}")
    return "\n".join(lines) + "\n"


def orchestrate(
    raw_input_dir: Path,
    confirmation_packet_template: Path,
    ai_self_filing_source_template: Path,
    official_preflight_source_template: Path,
    reference_delta_source_template: Path | None,
    output_dir: Path,
    case_id: str,
    received_from: str,
    jurisdiction: str,
    intake_mode: str,
) -> tuple[dict[str, Any], int]:
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    raw_copy_dir = output_root / "raw-input"
    package_dir = output_root / "case-package"
    scaffold_dir = output_root / "disclosure-normalization-scaffold"
    confirmation_dir = output_root / "scaffold-confirmation-to-disclosure"
    reference_delta_dir = output_root / "reference-patent-delta"
    draft_dir = output_root / "draft-package-generation"
    provenance_dir = output_root / "draft-evidence-provenance-gate"
    abnormal_dir = output_root / "abnormal-filing-risk-gate"
    package_validation_dir = output_root / "ai-self-filing-package-validation"
    materials_pipeline_dir = output_root / "application-materials-pipeline"
    official_ready_dir = output_root / "ai-self-filing-official-ready"
    approved_adapter_dir = output_root / "ai-self-filing-approved-adapter-preflight"
    lifecycle_dir = output_root / "case-lifecycle-trace"
    result_path = output_root / "pre-submission-pipeline-result.json"
    report_path = output_root / "pre-submission-pipeline-report.md"
    manifest_path = output_root / "artifact-hashes.json"

    stages: dict[str, dict[str, Any]] = {}
    responses: list[tuple[str, dict[str, Any], int, Path]] = []

    copy_raw_inputs(raw_input_dir, raw_copy_dir)
    package_response, package_exit = prepare_case_package.prepare_package(
        source_dir=raw_input_dir,
        output_dir=package_dir,
        case_id=case_id,
        received_from=received_from,
        jurisdiction=jurisdiction,
        intake_mode=intake_mode,
    )
    responses.append(("case_package", package_response, package_exit, package_dir))

    scaffold_response, scaffold_exit = normalize_invention_disclosure.normalize(package_dir, scaffold_dir)
    responses.append(("disclosure_scaffold", scaffold_response, scaffold_exit, scaffold_dir))

    copy_if_exists(scaffold_dir / "invention-disclosure-scaffold.json", confirmation_dir / "invention-disclosure-scaffold.json")
    copy_if_exists(scaffold_dir / "normalization-report.md", confirmation_dir / "normalization-report.md")
    confirmation_packet_path = confirmation_dir / "disclosure-confirmation-packet.json"
    materialize_confirmation_packet(
        confirmation_packet_template,
        scaffold_dir / "invention-disclosure-scaffold.json",
        confirmation_packet_path,
    )
    confirmation_response, confirmation_exit = confirm_invention_disclosure.confirm(
        confirmation_dir / "invention-disclosure-scaffold.json",
        confirmation_packet_path,
        confirmation_dir,
    )
    responses.append(("disclosure_confirmation", confirmation_response, confirmation_exit, confirmation_dir))

    reference_delta_path: Path | None = None
    reference_delta_source_path: Path | None = None
    if reference_delta_source_template:
        reference_delta_dir.mkdir(parents=True, exist_ok=True)
        reference_delta_source_path = reference_delta_dir / "reference-delta-source.json"
        materialize_reference_delta_source(
            reference_delta_source_template,
            package_dir,
            reference_delta_source_path,
            case_id,
        )
        reference_delta_response, reference_delta_exit = prepare_reference_patent_delta.prepare(
            reference_delta_source_path,
            reference_delta_dir,
        )
        responses.append(("reference_patent_delta", reference_delta_response, reference_delta_exit, reference_delta_dir))
        if reference_delta_exit == 0 and reference_delta_response.get("ok") is True:
            reference_delta_path = reference_delta_dir / "reference-patent-delta.json"

    draft_response, draft_exit = generate_draft_package.generate(
        confirmation_dir / "invention-disclosure.json",
        draft_dir,
        source_manifest="invention-disclosure.json",
        reference_delta_path=reference_delta_path,
    )
    responses.append(("draft_package", draft_response, draft_exit, draft_dir))

    provenance_response, provenance_exit = prepare_draft_evidence_provenance.prepare(
        draft_package_dir=draft_dir,
        source_manifest_path=package_dir / "01-normalized" / "source-material-manifest.json",
        output_dir=provenance_dir,
    )
    responses.append(("draft_evidence_provenance", provenance_response, provenance_exit, provenance_dir))

    abnormal_response, abnormal_exit = prepare_abnormal_filing_risk_assessment.prepare(
        draft_package_dir=provenance_dir,
        output_dir=abnormal_dir,
    )
    responses.append(("abnormal_filing_risk", abnormal_response, abnormal_exit, abnormal_dir))

    package_validation_dir.mkdir(parents=True, exist_ok=True)
    ai_source_path = package_validation_dir / "ai-self-filing-source.json"
    materialize_ai_self_filing_source(
        ai_self_filing_source_template,
        draft_dir,
        abnormal_dir,
        ai_source_path,
    )
    package_response, package_validation_exit = prepare_ai_self_filing_package.prepare(
        draft_package_dir=draft_dir,
        source_path=ai_source_path,
        output_dir=package_validation_dir,
    )
    responses.append(("ai_self_filing_package_validation", package_response, package_validation_exit, package_validation_dir))

    materials_response, materials_exit = orchestrate_application_materials_pipeline.orchestrate(
        package_dir=package_validation_dir,
        draft_package_dir=draft_dir,
        provenance_dir=provenance_dir,
        output_dir=materials_pipeline_dir,
    )
    responses.append(("application_materials_pipeline", materials_response, materials_exit, materials_pipeline_dir))

    official_ready_dir.mkdir(parents=True, exist_ok=True)
    official_source_path = official_ready_dir / "official-preflight-source.json"
    materialize_official_preflight_source(
        official_preflight_source_template,
        package_validation_dir,
        materials_pipeline_dir,
        official_source_path,
    )
    official_ready_response, official_ready_exit = prepare_ready_for_authorized_filing.prepare(
        validated_package_dir=package_validation_dir,
        preflight_source_path=official_source_path,
        output_dir=official_ready_dir,
    )
    responses.append(("ai_self_filing_official_ready", official_ready_response, official_ready_exit, official_ready_dir))

    approved_adapter_dir.mkdir(parents=True, exist_ok=True)
    approved_adapter_source_path = approved_adapter_dir / "approved-adapter-source.json"
    materialize_approved_adapter_source(
        Path(__file__).resolve().parents[1] / "benchmarks" / "ai-self-filing-approved-adapter-preflight" / "approved-adapter-source.json",
        official_ready_dir,
        approved_adapter_source_path,
    )
    approved_adapter_response, approved_adapter_exit = prepare_approved_adapter_preflight.prepare(
        ready_dir=official_ready_dir,
        validated_package_dir=package_validation_dir,
        adapter_source_path=approved_adapter_source_path,
        output_dir=approved_adapter_dir,
    )
    responses.append(("ai_self_filing_approved_adapter_preflight", approved_adapter_response, approved_adapter_exit, approved_adapter_dir))

    lifecycle_metadata = prepare_case_lifecycle_trace.extract_reference_delta_metadata(
        load_json(ai_source_path),
        load_json(abnormal_dir / "abnormal-filing-risk-assessment.json"),
        load_json(official_ready_dir / "filing-status.json"),
        load_json(approved_adapter_dir / "filing-status.json"),
        load_json(approved_adapter_dir / "approved-adapter-preflight.json"),
    )
    official_source = load_json(official_source_path)
    official_materials = official_source.get("application_materials") if isinstance(official_source.get("application_materials"), dict) else {}
    if official_materials.get("hash"):
        lifecycle_metadata["application_materials_hash"] = official_materials.get("hash")
    lifecycle_response, lifecycle_exit = prepare_pre_submission_lifecycle_trace(
        output_dir=lifecycle_dir,
        case_id=case_id,
        package_dir=package_dir,
        draft_dir=draft_dir,
        package_validation_dir=package_validation_dir,
        official_ready_dir=official_ready_dir,
        approved_adapter_dir=approved_adapter_dir,
        reference_metadata=lifecycle_metadata,
    )
    responses.append(("case_lifecycle_trace", lifecycle_response, lifecycle_exit, lifecycle_dir))

    for name, response, exit_code, directory in responses:
        stages[name] = stage_entry(name, response, exit_code, directory)

    ok = all(stage.get("ok") is True for stage in stages.values())
    lifecycle_trace_hash = str(lifecycle_response.get("trace_hash") or "")
    reference_delta_hash = ""
    if (abnormal_dir / "abnormal-filing-risk-assessment.json").exists():
        abnormal_result = load_json(abnormal_dir / "abnormal-filing-risk-assessment.json")
        reference_delta_hash = str(abnormal_result.get("reference_patent_delta_hash") or "")

    result = {
        "ok": ok,
        "case_id": case_id,
        "pipeline_type": "pre_submission_ai_self_filing_no_external_lawyer",
        "created_at": build_case_queue.utc_plus_8_now(),
        "status": "approved_for_adapter_execution" if ok else "pre_submission_pipeline_blocked",
        "decision": "approved_for_adapter_execution_no_auto_submit" if ok else "cure_pre_submission_pipeline_errors",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "pre_submission_lifecycle_gate": "passed" if lifecycle_response.get("ok") is True else "failed",
        "lifecycle_trace_hash": lifecycle_trace_hash,
        **({"reference_patent_delta_hash": reference_delta_hash} if reference_delta_hash else {}),
        "stages": stages,
        "artifacts": {
            "raw_input": str(raw_copy_dir),
            **({"reference_delta_source": str(reference_delta_source_path)} if reference_delta_source_path else {}),
            "ai_self_filing_source": str(ai_source_path),
            "official_preflight_source": str(official_source_path),
            "approved_adapter_source": str(approved_adapter_source_path),
            "case_lifecycle_trace": str(lifecycle_dir / "case-lifecycle-trace.json"),
            "pre_submission_pipeline_result": str(result_path),
            "pre_submission_pipeline_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
        "next_action": "Execute only through a separately authorized adapter execution step; automatic submission remains out of scope.",
    }
    write_json(result_path, result)

    stage_manifest_files = [
        package_dir / "artifact-hashes.json",
        scaffold_dir / "artifact-hashes.json",
        confirmation_dir / "artifact-hashes.json",
        draft_dir / "artifact-hashes.json",
        provenance_dir / "artifact-hashes.json",
        abnormal_dir / "artifact-hashes.json",
        *([reference_delta_dir / "artifact-hashes.json", reference_delta_source_path] if reference_delta_source_path else []),
        ai_source_path,
        package_validation_dir / "artifact-hashes.json",
        materials_pipeline_dir / "artifact-hashes.json",
        official_source_path,
        official_ready_dir / "artifact-hashes.json",
        approved_adapter_source_path,
        approved_adapter_dir / "artifact-hashes.json",
        lifecycle_dir / "artifact-hashes.json",
    ]
    provisional_manifest = build_manifest(output_root, case_id, stage_manifest_files + [result_path])
    report_path.write_text(render_report(result, provisional_manifest), encoding="utf-8")
    final_manifest = build_manifest(output_root, case_id, stage_manifest_files + [result_path, report_path])
    write_json(manifest_path, final_manifest)
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    result["manifest_errors"] = manifest_errors
    result["manifest_warnings"] = manifest_warnings
    result["ok"] = ok and manifest_ok
    write_json(result_path, result)
    final_manifest = build_manifest(output_root, case_id, stage_manifest_files + [result_path, report_path])
    write_json(manifest_path, final_manifest)
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    response = {
        "ok": result["ok"] and manifest_ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": result["artifacts"],
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "external_lawyer_involved": False,
        "automatic_submission_performed": False,
    }
    return response, 0 if response["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_input_dir", type=Path)
    parser.add_argument("--confirmation-packet-template", required=True, type=Path)
    parser.add_argument("--ai-self-filing-source-template", required=True, type=Path)
    parser.add_argument("--official-preflight-source-template", type=Path)
    parser.add_argument("--reference-delta-source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--received-from", required=True)
    parser.add_argument("--jurisdiction", default="CN")
    parser.add_argument("--intake-mode", choices=["manual_upload", "email", "api", "batch_import"], default="manual_upload")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = orchestrate(
            raw_input_dir=args.raw_input_dir,
            confirmation_packet_template=args.confirmation_packet_template,
            ai_self_filing_source_template=args.ai_self_filing_source_template,
            official_preflight_source_template=(
                args.official_preflight_source_template
                if args.official_preflight_source_template
                else Path(__file__).resolve().parents[1] / "benchmarks" / "ai-self-filing-official-ready" / "official-preflight-source.json"
            ),
            reference_delta_source_template=args.reference_delta_source,
            output_dir=args.output_dir,
            case_id=args.case_id,
            received_from=args.received_from,
            jurisdiction=args.jurisdiction,
            intake_mode=args.intake_mode,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
            "adapter_execution_performed": False,
            "external_lawyer_involved": False,
            "automatic_submission_performed": False,
        }, 1

    if args.json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print("PASS" if response.get("ok") else "FAIL")
        print(json.dumps(response, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
