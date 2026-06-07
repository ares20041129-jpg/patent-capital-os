#!/usr/bin/env python3
"""Prepare an end-to-end lifecycle trace from benchmark case artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_case_lifecycle_trace


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


REFERENCE_DELTA_DIRECT_KEYS = [
    "reference_patent_delta_hash",
    "reference_delta_rows_count",
    "reference_delta_claim_elements_count",
    "reference_delta_boundary_preserved",
]


def extract_reference_delta_metadata(*sources: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        for key in REFERENCE_DELTA_DIRECT_KEYS:
            value = source.get(key)
            if value not in (None, "", [], {}) and key not in metadata:
                metadata[key] = value
        nested = get_path(source, "ai_compliance_review.abnormal_filing_risk_assessment")
        if isinstance(nested, dict):
            for key in REFERENCE_DELTA_DIRECT_KEYS:
                value = nested.get(key)
                if value not in (None, "", [], {}) and key not in metadata:
                    metadata[key] = value
        application_materials_hash = source.get("application_materials_hash")
        if application_materials_hash and "application_materials_hash" not in metadata:
            metadata["application_materials_hash"] = application_materials_hash
    return metadata


def artifact_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [
            {
                "path": rel(path, output_dir),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
    }


def stage(
    order: int,
    name: str,
    status: str,
    artifact: Path,
    output_root: Path,
    validator: str,
    legal_gate: str,
    decision: str,
    next_gate: str,
    official_touched: bool = False,
    official_submitted: bool = False,
    adapter_performed: bool = False,
    receipt_hash: str = "",
    application_number: str = "",
    final_package_hash: str = "",
    reviewed_package_hash: str = "",
    submitted_package_hash: str = "",
    official_session_authorization_hash: str = "",
    official_session_reference_hash: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "order": order,
        "stage": name,
        "status": status,
        "artifact": rel(artifact, output_root),
        "artifact_hash": sha256_file(artifact),
        "validator": validator,
        "validation_result": "passed",
        "legal_gate": legal_gate,
        "official_system_touched": official_touched,
        "official_submission_performed": official_submitted,
        "adapter_execution_performed": adapter_performed,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_adapter_execution_performed": False,
        "evidence_claims_official_system_touched": official_touched,
        "evidence_claims_official_submission_performed": official_submitted,
        "evidence_claims_adapter_execution_performed": adapter_performed,
        "receipt_hash": receipt_hash,
        "application_number": application_number,
        "benchmark_mock": True,
        "decision": decision,
        "next_required_gate": next_gate,
    }
    if final_package_hash:
        data["final_package_hash"] = final_package_hash
    if reviewed_package_hash:
        data["reviewed_package_hash"] = reviewed_package_hash
    if submitted_package_hash:
        data["submitted_package_hash"] = submitted_package_hash
    if official_session_authorization_hash:
        data["official_session_authorization_hash"] = official_session_authorization_hash
    if official_session_reference_hash:
        data["official_session_reference_hash"] = official_session_reference_hash
    if metadata:
        for key, value in metadata.items():
            if value not in (None, "", [], {}):
                data[key] = value
    return data


def render_report(trace: dict[str, Any]) -> str:
    invariants = trace["invariants"]
    yes = lambda value: "yes" if value else "no"
    route = trace.get("legal_gate_mode")
    route_lines = []
    if route:
        route_lines = [
            f"Legal gate mode: {route}",
            f"External lawyer involved: {yes(trace.get('external_lawyer_involved'))}",
            "",
        ]
    reference_delta_lines = []
    if trace.get("reference_patent_delta_hash"):
        reference_delta_lines = [
            f"Reference patent delta hash: {trace.get('reference_patent_delta_hash')}",
            f"Reference delta boundary preserved: {yes(trace.get('reference_delta_boundary_preserved'))}",
            "",
        ]
    return "\n".join(
        [
            "# Case Lifecycle Trace Report",
            "",
            f"Case ID: {trace['case_id']}",
            f"Trace type: {trace['trace_type']}",
            f"Final status: {trace['final_status']}",
            "",
            *route_lines,
            *reference_delta_lines,
            "## Invariants",
            "",
            f"Legal gate never skipped: {yes(invariants['legal_gate_never_skipped'])}",
            f"Package hash consistent: {yes(invariants['package_hash_consistent'])}",
            f"No receipt before submission: {yes(invariants['no_receipt_before_submission'])}",
            f"No application number before receipt: {yes(invariants['no_application_number_before_receipt'])}",
            f"Official session hash consistent: {yes(invariants['official_session_hash_consistent'])}",
            f"Mock evidence marked: {yes(invariants['mock_evidence_marked'])}",
            *(
                [f"Reference delta boundary preserved: {yes(invariants.get('reference_delta_boundary_preserved'))}"]
                if trace.get("reference_patent_delta_hash")
                else []
            ),
            "",
            "## Boundary",
            "",
            "This benchmark trace is not a real filing, not a real receipt, and not a real application number.",
            "",
        ]
    )


def prepare_ai_self_filing(root: Path, output_dir: Path, reference_delta: bool = False) -> tuple[dict[str, Any], int]:
    repo_root = root.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    case_id = "CASE-INTAKE-ORCH-001"
    package_dir_name = "ai-self-filing-package-reference-delta" if reference_delta else "ai-self-filing-package-validation"
    draft_dir_name = "draft-package-reference-delta" if reference_delta else "draft-package-generation"
    official_ready_dir_name = "ai-self-filing-official-ready-reference-delta" if reference_delta else "ai-self-filing-official-ready"
    approved_dir_name = "ai-self-filing-approved-adapter-preflight-reference-delta" if reference_delta else "ai-self-filing-approved-adapter-preflight"
    adapter_dir_name = (
        "ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta"
        if reference_delta
        else "ai-self-filing-adapter-to-submitted-pending-receipt"
    )
    receipt_dir_name = (
        "ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta"
        if reference_delta
        else "ai-self-filing-submitted-pending-receipt-to-official-receipt"
    )
    application_dir_name = (
        "ai-self-filing-official-receipt-to-application-number-reference-delta"
        if reference_delta
        else "ai-self-filing-official-receipt-to-application-number"
    )

    package_status_path = repo_root / "benchmarks" / package_dir_name / "filing-status.json"
    authorization_packet_path = repo_root / "benchmarks" / package_dir_name / "ai-self-filing-authorization-packet.json"
    approved_status_path = repo_root / "benchmarks" / approved_dir_name / "filing-status.json"
    adapter_result_path = repo_root / "benchmarks" / adapter_dir_name / "adapter-execution-result.json"
    receipt_status_path = repo_root / "benchmarks" / receipt_dir_name / "filing-status.json"
    receipt_capture_path = repo_root / "benchmarks" / receipt_dir_name / "receipt-capture.yaml"
    app_evidence_path = repo_root / "benchmarks" / application_dir_name / "application-number-evidence.json"

    package_status = load_json(package_status_path)
    authorization_packet = load_json(authorization_packet_path)
    final_hash = str(package_status.get("final_package_hash") or "")
    reviewed_hash = str(package_status.get("reviewed_package_hash") or "")
    approved_status = load_json(approved_status_path)
    adapter_result = load_json(adapter_result_path) if adapter_result_path.exists() else {}
    receipt_status = load_json(receipt_status_path) if receipt_status_path.exists() else {}
    app_evidence = load_json(app_evidence_path) if app_evidence_path.exists() else {}
    reference_metadata = extract_reference_delta_metadata(
        authorization_packet,
        package_status,
        approved_status,
        adapter_result,
        receipt_status,
        app_evidence,
    )
    if not reference_delta:
        reference_metadata = {}
    reference_only_metadata = {key: value for key, value in reference_metadata.items() if key != "application_materials_hash"}

    stages = [
        stage(
            1,
            "source_intake",
            "intake_received",
            repo_root / "benchmarks/case-package-orchestration-dry-run/case-package/case-package-manifest.json",
            output_root,
            "validate_case_intake_orchestration_benchmark",
            "pending",
            "intake_received",
            "disclosure_confirmation",
        ),
        stage(
            2,
            "draft_generation",
            "draft_only",
            repo_root / "benchmarks" / draft_dir_name / "patent-application-draft.md",
            output_root,
            "validate_draft_package_generation_benchmark",
            "pending",
            "draft_only_do_not_file",
            "ai_self_filing_authorization",
            metadata=reference_only_metadata,
        ),
        stage(
            3,
            "ai_self_filing_authorization",
            "ready_for_package_validation",
            authorization_packet_path,
            output_root,
            "validate_ai_self_filing_authorization",
            "passed",
            "ai_self_filing_gate_passed",
            "package_validation",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            metadata=reference_only_metadata,
        ),
        stage(
            4,
            "ai_self_filing_package_validation",
            "package_valid_official_preflight_pending",
            repo_root / "benchmarks" / package_dir_name / "filing-package-manifest.yaml",
            output_root,
            "validate_ai_self_filing_package_benchmark",
            "passed",
            "package_valid_official_preflight_pending",
            "official_channel_preflight",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            metadata=reference_only_metadata,
        ),
        stage(
            5,
            "official_channel_preflight",
            "ready_for_authorized_filing",
            repo_root / "benchmarks" / official_ready_dir_name / "official-channel-preflight.yaml",
            output_root,
            "validate_ready_for_authorized_filing_benchmark",
            "passed",
            "ready_for_authorized_filing",
            "approved_adapter_preflight",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            metadata=reference_metadata,
        ),
        stage(
            6,
            "approved_adapter_preflight",
            "approved_for_adapter_execution",
            repo_root / "benchmarks" / approved_dir_name / "approved-adapter-preflight.json",
            output_root,
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
    final_status = "approved_for_adapter_execution"
    if adapter_result_path.exists():
        submitted_hash = str(get_path(adapter_result, "official_submission_evidence.submitted_package_hash") or final_hash)
        stages.append(
            stage(
                7,
                "adapter_execution_result",
                "submitted_pending_receipt",
                adapter_result_path,
                output_root,
                "validate_generated_adapter_execution_result_benchmark",
                "passed",
                "submitted_pending_receipt_mock",
                "receipt_capture",
                official_touched=True,
                official_submitted=True,
                adapter_performed=True,
                final_package_hash=final_hash,
                reviewed_package_hash=reviewed_hash,
                submitted_package_hash=submitted_hash,
                official_session_authorization_hash=str(adapter_result.get("official_session_authorization_hash") or ""),
                official_session_reference_hash=str(adapter_result.get("official_session_reference_hash") or ""),
                metadata=reference_metadata,
            )
        )
        final_status = "submitted_pending_receipt"
        if receipt_status_path.exists() and receipt_capture_path.exists():
            receipt_hash = str(receipt_status.get("official_receipt_hash") or "")
            stages.append(
                stage(
                    8,
                    "receipt_capture",
                    "official_receipt_received",
                    receipt_capture_path,
                    output_root,
                    "validate_generated_receipt_capture_benchmark",
                    "passed",
                    "official_receipt_received_mock",
                    "application_number_evidence",
                    official_touched=True,
                    official_submitted=True,
                    adapter_performed=True,
                    receipt_hash=receipt_hash,
                    final_package_hash=final_hash,
                    reviewed_package_hash=reviewed_hash,
                    submitted_package_hash=submitted_hash,
                    official_session_authorization_hash=str(receipt_status.get("official_session_authorization_hash") or ""),
                    official_session_reference_hash=str(receipt_status.get("official_session_reference_hash") or ""),
                    metadata=reference_metadata,
                )
            )
            final_status = "official_receipt_received"
            if app_evidence_path.exists():
                app_number = str(get_path(app_evidence, "application.application_number") or "")
                stages.append(
                    stage(
                        9,
                        "application_number_evidence",
                        "accepted_or_application_number_received",
                        app_evidence_path,
                        output_root,
                        "validate_generated_application_number_benchmark",
                        "passed",
                        "accepted_or_application_number_received_mock",
                        "portfolio_maintenance",
                        official_touched=True,
                        official_submitted=True,
                        adapter_performed=True,
                        receipt_hash=receipt_hash,
                        application_number=app_number,
                        final_package_hash=final_hash,
                        reviewed_package_hash=reviewed_hash,
                        submitted_package_hash=submitted_hash,
                        official_session_authorization_hash=str(app_evidence.get("official_session_authorization_hash") or ""),
                        official_session_reference_hash=str(app_evidence.get("official_session_reference_hash") or ""),
                        metadata=reference_metadata,
                    )
                )
                final_status = "accepted_or_application_number_received"

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
        "lifecycle_id": (
            "AI-SELF-FILING-REFERENCE-DELTA-LIFECYCLE-CASE-INTAKE-ORCH-001"
            if reference_delta
            else "AI-SELF-FILING-LIFECYCLE-CASE-INTAKE-ORCH-001"
        ),
        "case_id": case_id,
        "jurisdiction": "CN",
        "trace_type": "benchmark_mock",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "final_status": final_status,
        "stages": stages,
        "invariants": invariants,
    }
    trace.update(reference_metadata)

    trace_path = output_root / "case-lifecycle-trace.json"
    report_path = output_root / "lifecycle-report.md"
    hashes_path = output_root / "artifact-hashes.json"
    write_json(trace_path, trace)
    report_path.write_text(render_report(trace), encoding="utf-8")
    write_json(hashes_path, artifact_manifest(output_root, case_id, [trace_path, report_path]))

    trace_ok, trace_errors, trace_warnings = validate_case_lifecycle_trace.validate(trace, base_dir=output_root)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
    ok = trace_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "case_lifecycle_trace": str(trace_path),
            "lifecycle_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "trace_errors": trace_errors,
        "trace_warnings": trace_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "final_status": final_status,
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "official_system_touched": False,
        "official_submission_performed": False,
    }, 0 if ok else 1


def prepare(
    root: Path,
    output_dir: Path,
    route: str = "counsel_or_agent_review",
    reference_delta: bool = False,
) -> tuple[dict[str, Any], int]:
    if route == "ai_self_filing_no_external_lawyer":
        return prepare_ai_self_filing(root, output_dir, reference_delta=reference_delta)
    if reference_delta:
        return {"ok": False, "errors": ["reference_delta_requires_ai_self_filing_no_external_lawyer_route"]}, 1

    repo_root = root.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    case_id = "CASE-INTAKE-ORCH-001"
    package_status = load_json(repo_root / "benchmarks/draft-package-to-filing-validation/filing-status.json")
    approved_status = load_json(repo_root / "benchmarks/official-ready-to-approved-adapter-preflight/filing-status.json")
    adapter_result = load_json(repo_root / "benchmarks/approved-adapter-to-submitted-pending-receipt/adapter-execution-result.json")
    receipt_status = load_json(repo_root / "benchmarks/submitted-pending-receipt-to-official-receipt/filing-status.json")
    app_evidence = load_json(repo_root / "benchmarks/official-receipt-to-application-number/application-number-evidence.json")

    final_hash = str(package_status.get("final_package_hash") or adapter_result.get("final_package_hash") or "")
    reviewed_hash = str(package_status.get("reviewed_package_hash") or adapter_result.get("reviewed_package_hash") or "")
    submitted_hash = str(get_path(adapter_result, "official_submission_evidence.submitted_package_hash") or final_hash)
    receipt_hash = str(receipt_status.get("official_receipt_hash") or "")
    app_number = str(get_path(app_evidence, "application.application_number") or "")

    stages = [
        stage(
            1,
            "source_intake",
            "intake_received",
            repo_root / "benchmarks/case-package-orchestration-dry-run/case-package/case-package-manifest.json",
            output_root,
            "validate_case_intake_orchestration_benchmark",
            "pending",
            "intake_received",
            "disclosure_confirmation",
        ),
        stage(
            2,
            "draft_generation",
            "draft_only",
            repo_root / "benchmarks/draft-package-generation/patent-application-draft.md",
            output_root,
            "validate_draft_package_generation_benchmark",
            "pending",
            "draft_only_do_not_file",
            "legal_authorization",
        ),
        stage(
            3,
            "legal_authorization",
            "ready_for_package_validation",
            repo_root / "benchmarks/draft-package-to-filing-validation/submission-authorization-packet.json",
            output_root,
            "validate_submission_packet",
            "passed",
            "legal_gate_passed",
            "package_validation",
        ),
        stage(
            4,
            "package_validation",
            "package_valid_official_preflight_pending",
            repo_root / "benchmarks/draft-package-to-filing-validation/filing-package-manifest.yaml",
            output_root,
            "validate_validated_filing_package_benchmark",
            "passed",
            "package_valid_official_preflight_pending",
            "official_channel_preflight",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
        ),
        stage(
            5,
            "official_channel_preflight",
            "ready_for_authorized_filing",
            repo_root / "benchmarks/validated-package-to-official-ready/official-channel-preflight.yaml",
            output_root,
            "validate_ready_for_authorized_filing_benchmark",
            "passed",
            "ready_for_authorized_filing",
            "approved_adapter_preflight",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
        ),
        stage(
            6,
            "approved_adapter_preflight",
            "approved_for_adapter_execution",
            repo_root / "benchmarks/official-ready-to-approved-adapter-preflight/approved-adapter-preflight.json",
            output_root,
            "validate_generated_approved_adapter_preflight_benchmark",
            "passed",
            "approved_for_adapter_execution",
            "adapter_execution_result",
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            official_session_authorization_hash=str(approved_status.get("official_session_authorization_hash") or ""),
            official_session_reference_hash=str(approved_status.get("official_session_reference_hash") or ""),
        ),
        stage(
            7,
            "adapter_execution_result",
            "submitted_pending_receipt",
            repo_root / "benchmarks/approved-adapter-to-submitted-pending-receipt/adapter-execution-result.json",
            output_root,
            "validate_generated_adapter_execution_result_benchmark",
            "passed",
            "submitted_pending_receipt_mock",
            "receipt_capture",
            official_touched=True,
            official_submitted=True,
            adapter_performed=True,
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            submitted_package_hash=submitted_hash,
            official_session_authorization_hash=str(adapter_result.get("official_session_authorization_hash") or ""),
            official_session_reference_hash=str(adapter_result.get("official_session_reference_hash") or ""),
        ),
        stage(
            8,
            "receipt_capture",
            "official_receipt_received",
            repo_root / "benchmarks/submitted-pending-receipt-to-official-receipt/receipt-capture.yaml",
            output_root,
            "validate_generated_receipt_capture_benchmark",
            "passed",
            "official_receipt_received_mock",
            "application_number_evidence",
            official_touched=True,
            official_submitted=True,
            adapter_performed=True,
            receipt_hash=receipt_hash,
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            submitted_package_hash=submitted_hash,
            official_session_authorization_hash=str(receipt_status.get("official_session_authorization_hash") or ""),
            official_session_reference_hash=str(receipt_status.get("official_session_reference_hash") or ""),
        ),
        stage(
            9,
            "application_number_evidence",
            "accepted_or_application_number_received",
            repo_root / "benchmarks/official-receipt-to-application-number/application-number-evidence.json",
            output_root,
            "validate_generated_application_number_benchmark",
            "passed",
            "accepted_or_application_number_received_mock",
            "portfolio_maintenance",
            official_touched=True,
            official_submitted=True,
            adapter_performed=True,
            receipt_hash=receipt_hash,
            application_number=app_number,
            final_package_hash=final_hash,
            reviewed_package_hash=reviewed_hash,
            submitted_package_hash=submitted_hash,
            official_session_authorization_hash=str(app_evidence.get("official_session_authorization_hash") or ""),
            official_session_reference_hash=str(app_evidence.get("official_session_reference_hash") or ""),
        ),
    ]

    trace = {
        "lifecycle_id": "LIFECYCLE-CASE-INTAKE-ORCH-001",
        "case_id": case_id,
        "jurisdiction": "CN",
        "trace_type": "benchmark_mock",
        "generated_at": build_case_queue.utc_plus_8_now(),
        "final_status": "accepted_or_application_number_received",
        "stages": stages,
        "invariants": {
            "legal_gate_never_skipped": True,
            "package_hash_consistent": True,
            "no_receipt_before_submission": True,
            "no_application_number_before_receipt": True,
            "official_session_hash_consistent": True,
            "mock_evidence_marked": True,
        },
    }

    trace_path = output_root / "case-lifecycle-trace.json"
    report_path = output_root / "lifecycle-report.md"
    hashes_path = output_root / "artifact-hashes.json"
    write_json(trace_path, trace)
    report_path.write_text(render_report(trace), encoding="utf-8")
    write_json(hashes_path, artifact_manifest(output_root, case_id, [trace_path, report_path]))

    trace_ok, trace_errors, trace_warnings = validate_case_lifecycle_trace.validate(trace, base_dir=output_root)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
    ok = trace_ok and hash_ok
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "case_lifecycle_trace": str(trace_path),
            "lifecycle_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "trace_errors": trace_errors,
        "trace_warnings": trace_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "final_status": "accepted_or_application_number_received",
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--route",
        choices=["counsel_or_agent_review", "ai_self_filing_no_external_lawyer"],
        default="counsel_or_agent_review",
    )
    parser.add_argument("--reference-delta", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(
            args.root,
            args.output_dir,
            args.route,
            reference_delta=args.reference_delta,
        )
    except Exception as exc:
        response, exit_code = {"ok": False, "errors": [str(exc)]}, 1
    rendered = json.dumps(response, ensure_ascii=False, indent=2)
    if args.json:
        print(rendered)
    else:
        print("PASS" if response.get("ok") else "FAIL")
        print(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
