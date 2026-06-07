#!/usr/bin/env python3
"""Run an offline patent case queue through configured validators.

This runner coordinates local validation only. It does not log in to,
touch, submit to, sign in, pay through, or claim receipt from any official
filing system.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import validate_batch_processor_result
import validate_case_queue


VALIDATOR_NAME_RE = re.compile(r"^validate_[A-Za-z0-9_]+$")

DIRECTORY_VALIDATORS = {
    "validate_adapter_execution_benchmark",
    "validate_abnormal_filing_risk_benchmark",
    "validate_application_materials_quality_benchmark",
    "validate_application_materials_pipeline_benchmark",
    "validate_pre_submission_handoff_package",
    "validate_pre_submission_handoff_rejection_benchmark",
    "validate_pre_submission_pipeline_benchmark",
    "validate_pre_submission_to_handoff_benchmark",
    "validate_abnormal_filing_risk_rejection_benchmark",
    "validate_ai_self_filing_abnormal_risk_binding_rejection_benchmark",
    "validate_ai_self_filing_application_materials_binding_rejection_benchmark",
    "validate_ai_self_filing_cure_revalidation_benchmark",
    "validate_ai_self_filing_deficiency_report_benchmark",
    "validate_ai_self_filing_legal_gate_rejection_benchmark",
    "validate_ai_self_filing_package_benchmark",
    "validate_patent_application_materials_benchmark",
    "validate_generated_adapter_execution_result_benchmark",
    "validate_generated_application_number_benchmark",
    "validate_generated_receipt_capture_benchmark",
    "validate_application_number_benchmark",
    "validate_approved_adapter_benchmark",
    "validate_authorized_ready_benchmark",
    "validate_benchmark_gate",
    "validate_case_processor_benchmark",
    "validate_case_lifecycle_rejection_benchmark",
    "validate_case_lifecycle_benchmark",
    "validate_case_package_benchmark",
    "validate_case_intake_orchestration_benchmark",
    "validate_case_queue_benchmark",
    "validate_approved_adapter_evidence_queue_benchmark",
    "validate_disclosure_confirmation_rejection_benchmark",
    "validate_disclosure_normalization_benchmark",
    "validate_draft_evidence_provenance_benchmark",
    "validate_draft_package_generation_benchmark",
    "validate_draft_to_package_benchmark",
    "validate_generated_approved_adapter_preflight_benchmark",
    "validate_inbox_handoff_index_benchmark",
    "validate_inbox_to_handoff_benchmark",
    "validate_inbox_to_handoff_rejection_benchmark",
    "validate_incoming_application_benchmark",
    "validate_official_ready_benchmark",
    "validate_official_session_authorization_benchmark",
    "validate_patent_application_materials_rejection_benchmark",
    "validate_production_adapter_readiness_benchmark",
    "validate_production_official_evidence_gate_benchmark",
    "validate_receipt_capture_benchmark",
    "validate_ready_for_authorized_filing_benchmark",
    "validate_scaffold_confirmation_benchmark",
    "validate_skill_completion_audit_benchmark",
    "validate_validated_filing_package_benchmark",
    "validate_workflow_orchestration_benchmark",
}

FILE_VALIDATOR_DEFAULTS = {
    "validate_case_record": "case-record.json",
    "validate_case_package_manifest": "case-package-manifest.json",
    "validate_case_queue": "case-queue.json",
    "validate_claim_support_map": "claim-support-map.md",
    "validate_filing_package_manifest": "filing-package-manifest.yaml",
    "validate_invention_disclosure": "invention-disclosure.json",
    "validate_invention_disclosure_scaffold": "invention-disclosure-scaffold.json",
    "validate_official_channel_preflight": "official-channel-preflight.yaml",
    "validate_patent_application_draft": "patent-application-draft.md",
    "validate_receipt_capture": "receipt-capture.yaml",
    "validate_source_material_manifest": "source-material-manifest.yaml",
    "validate_submission_packet": "submission-packet.json",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_plus_8_now() -> str:
    tz = dt.timezone(dt.timedelta(hours=8))
    return dt.datetime.now(tz=tz).replace(microsecond=0).isoformat()


def resolve_case_folder(queue_path: Path, item: dict[str, Any]) -> Path:
    raw = item.get("case_folder") or "."
    path = Path(str(raw))
    if not path.is_absolute():
        path = queue_path.parent / path
    return path.resolve()


def validator_target(case_folder: Path, name: str, item: dict[str, Any]) -> Path:
    explicit = item.get("validator_inputs", {})
    if isinstance(explicit, dict) and explicit.get(name):
        path = Path(str(explicit[name]))
        return path if path.is_absolute() else (case_folder / path).resolve()

    if name in DIRECTORY_VALIDATORS:
        return case_folder

    rel = FILE_VALIDATOR_DEFAULTS.get(name)
    if rel:
        return (case_folder / rel).resolve()

    return case_folder


def safe_validator_script(scripts_dir: Path, name: str) -> Path:
    if not VALIDATOR_NAME_RE.fullmatch(name):
        raise ValueError(f"invalid_validator_name: {name}")
    script = (scripts_dir / f"{name}.py").resolve()
    if not script.exists():
        raise FileNotFoundError(f"validator_script_not_found: {name}")
    if scripts_dir.resolve() not in script.parents:
        raise ValueError(f"validator_script_outside_scripts_dir: {name}")
    return script


def run_validator(
    scripts_dir: Path,
    queue_path: Path,
    item: dict[str, Any],
    name: str,
) -> tuple[bool, list[str], list[str]]:
    case_folder = resolve_case_folder(queue_path, item)
    script = safe_validator_script(scripts_dir, name)
    target = validator_target(case_folder, name, item)
    command = [sys.executable, "-X", "utf8", str(script), str(target), "--json"]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, [f"{name}: timeout"], []

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        return False, [f"{name}: invalid_json_output"], [stderr] if stderr else []

    ok = bool(payload.get("ok")) and completed.returncode == 0
    errors = [f"{name}: {err}" for err in payload.get("errors", [])]
    warnings = [f"{name}: {warn}" for warn in payload.get("warnings", [])]
    if completed.returncode != 0 and not errors:
        errors.append(f"{name}: exit_code_{completed.returncode}")
    if stderr:
        warnings.append(f"{name}: stderr: {stderr}")
    return ok, errors, warnings


def normalized_outcome(expected: str, validator_errors: list[str]) -> str:
    if validator_errors:
        return "blocked"
    if expected in {"deficiency", "handoff", "blocked"}:
        return expected
    return "passed"


def decision_for(expected: str, outcome: str) -> str:
    if outcome == "blocked":
        return "blocked_by_validator"
    if outcome == "deficiency":
        return "do_not_file"
    if outcome == "handoff":
        return "handoff_required"
    if expected == "official_preflight":
        return "official_preflight_required"
    if expected == "disclosure_scaffold":
        return "disclosure_scaffold_pending_confirmation"
    if expected == "case_intake_orchestration":
        return "case_intake_orchestration_pending_confirmations"
    if expected == "confirmed_disclosure":
        return "confirmed_disclosure_draft_only"
    if expected == "abnormal_filing_risk":
        return "abnormal_filing_risk_assessment_passed"
    if expected == "abnormal_filing_risk_rejection":
        return "abnormal_filing_risk_rejection_passed"
    if expected == "ai_self_filing_abnormal_risk_binding_rejection":
        return "ai_self_filing_abnormal_risk_binding_rejection_passed"
    if expected == "ai_self_filing_application_materials_binding_rejection":
        return "ai_self_filing_application_materials_binding_rejection_passed"
    if expected == "patent_application_materials_rejection":
        return "patent_application_materials_rejection_passed"
    if expected == "inbox_handoff_index":
        return "inbox_handoff_index_ready"
    if expected == "skill_completion_audit":
        return "skill_completion_audit_passed"
    if expected == "pre_submission_handoff_rejection":
        return "pre_submission_handoff_rejection_passed"
    if expected == "inbox_to_handoff":
        return "inbox_to_handoff_ready"
    if expected == "inbox_to_handoff_rejection":
        return "inbox_to_handoff_rejection_passed"
    if expected == "pre_submission_to_handoff":
        return "pre_submission_to_handoff_ready"
    if expected == "disclosure_confirmation_rejection":
        return "disclosure_confirmation_rejection_passed"
    if expected == "draft_evidence_provenance":
        return "draft_evidence_provenance_passed"
    if expected == "draft_package":
        return "draft_package_ai_self_filing_authorization_needed"
    if expected == "package_validation":
        return "package_validation_passed"
    if expected == "ai_self_filing_package_validation":
        return "ai_self_filing_package_validation_passed"
    if expected == "patent_application_materials":
        return "patent_application_materials_generated"
    if expected == "application_materials_quality":
        return "application_materials_quality_gate_passed"
    if expected == "application_materials_pipeline":
        return "application_materials_pipeline_passed"
    if expected == "pre_submission_handoff_package":
        return "pre_submission_handoff_ready"
    if expected == "pre_submission_pipeline":
        return "pre_submission_pipeline_passed"
    if expected == "approved_adapter_preflight":
        return "approved_adapter_preflight_passed"
    if expected == "adapter_execution":
        return "adapter_execution_result_captured"
    if expected == "receipt_capture":
        return "official_receipt_captured"
    if expected == "application_number":
        return "application_number_evidence_accepted"
    if expected == "production_official_evidence":
        return "production_official_evidence_gate_passed"
    if expected == "production_adapter_readiness":
        return "production_adapter_readiness_gate_passed"
    if expected == "official_session_authorization":
        return "official_session_authorization_gate_passed"
    if expected == "ai_self_filing_cure_revalidation":
        return "ai_self_filing_cure_revalidation_passed"
    if expected == "dry_run_ok":
        return "dry_run_ok"
    return "validation_passed"


def next_action_for(expected: str, outcome: str, item: dict[str, Any]) -> str:
    if item.get("next_action"):
        return str(item["next_action"])
    if outcome == "blocked":
        return "Fix validator errors before advancing the case."
    if outcome == "deficiency":
        return "Cure legal, authorization, ownership, secrecy, support, or package deficiencies before filing."
    if outcome == "handoff":
        return "Authorized filing operator performs final official-system action or approves a lawful adapter run."
    if expected == "official_preflight":
        return "Run official-channel preflight and receipt-capture planning."
    if expected == "disclosure_scaffold":
        return "Collect inventor, applicant/ownership, no-copying, evidence, secrecy, and legal confirmations before draft generation."
    if expected == "case_intake_orchestration":
        return "Review the intake orchestration report and collect confirmations before draft generation or filing readiness."
    if expected == "confirmed_disclosure":
        return "Generate draft-only AI legal/compliance authorization artifacts; do not file until final legal authorization and official-channel gates pass."
    if expected == "abnormal_filing_risk":
        return "Proceed only to AI self-filing legal/compliance authorization for the no-external-lawyer route; do not file from abnormal-risk assessment alone."
    if expected == "abnormal_filing_risk_rejection":
        return "Keep unsafe mutations blocked and expand rejection cases when new abnormal-filing patterns appear."
    if expected == "ai_self_filing_abnormal_risk_binding_rejection":
        return "Keep AI self-filing package validation bound to the abnormal-risk assessment artifact hash."
    if expected == "ai_self_filing_application_materials_binding_rejection":
        return "Keep AI self-filing official-ready preflight bound to the validated application materials artifact hash."
    if expected == "patent_application_materials_rejection":
        return "Keep malformed application materials blocked before official-channel preflight."
    if expected == "inbox_handoff_index":
        return "Use the index as the production-control summary for read-only handoff evidence; adapter execution, receipt capture, and application-number evidence remain separate gates."
    if expected == "skill_completion_audit":
        return "Treat the skill as closed for local no-auto-submit handoff only after the regression gate remains green."
    if expected == "pre_submission_handoff_rejection":
        return "Keep malformed pre-submission handoff packages blocked before adapter execution."
    if expected == "inbox_to_handoff_rejection":
        return "Keep unsafe inbox inputs blocked before raw materials enter pre-submission-to-handoff generation."
    if expected == "disclosure_confirmation_rejection":
        return "Keep lawyer or patent-agent claims, weak hashes, external-lawyer flags, and reference-hash contamination blocked before draft generation."
    if expected == "draft_evidence_provenance":
        return "Proceed only to draft package review or AI self-filing authorization after unsupported claim facts are removed."
    if expected == "draft_package":
        return "Run AI self-filing legal/compliance authorization; do not build a filing package until applicant authorization, legal gate evidence, and package hashes pass."
    if expected == "package_validation":
        return "Run official-channel preflight before any upload, signature, payment, or submission."
    if expected == "ai_self_filing_package_validation":
        return "Run AI self-filing official-channel preflight before any upload, signature, payment, or submission."
    if expected == "patent_application_materials":
        return "Run official-channel preflight against the generated application materials before any upload, signature, payment, or submission."
    if expected == "application_materials_quality":
        return "Run official-channel preflight only after the quality score, legal/safety boundary, and hash-bound materials review remain passed."
    if expected == "application_materials_pipeline":
        return "Run official-channel preflight only after application materials generation and independent quality review remain passed."
    if expected == "inbox_to_handoff":
        return "Use each read-only handoff package only as approved-adapter execution input evidence; adapter execution, receipt capture, and application-number evidence remain separate gates."
    if expected == "pre_submission_to_handoff":
        return "Use the read-only handoff package as approved-adapter execution input evidence only; adapter execution, receipt capture, and application-number evidence remain separate gates."
    if expected == "pre_submission_handoff_package":
        return "Use the read-only handoff package as approved-adapter execution input evidence only; adapter execution and receipt capture remain separate gates."
    if expected == "pre_submission_pipeline":
        return "Prepare approved-adapter execution handoff only after the full pre-submission pipeline and lifecycle audit gate remain green; automatic submission remains out of scope."
    if expected == "approved_adapter_preflight":
        return "An approved adapter may attempt the authorized action next; capture adapter execution result before any status advance."
    if expected == "adapter_execution":
        return "Capture official receipt evidence before marking receipt received, accepted, or application-number status."
    if expected == "receipt_capture":
        return "Validate application-number evidence before marking accepted or application-number received."
    if expected == "application_number":
        return "Maintain docket deadlines, portfolio ownership, fee monitoring, and prosecution workflow."
    if expected == "production_official_evidence":
        return "Treat production official evidence as usable only when the strict gate passes on real, non-mock artifacts."
    if expected == "production_adapter_readiness":
        return "Allow approved adapter execution only after a real, non-shape-test adapter readiness packet passes strict validation."
    if expected == "official_session_authorization":
        return "Allow approved adapter execution only after real, non-shape-test official session authorization passes strict validation."
    if expected == "ai_self_filing_cure_revalidation":
        return "Run AI self-filing package validation before official-channel preflight; do not file from cure revalidation alone."
    return "Proceed only to the next authorized offline gate."


def process_queue(queue_path: Path, scripts_dir: Path) -> tuple[dict[str, Any], int]:
    queue = load_json(queue_path)
    queue_ok, queue_errors, queue_warnings = validate_case_queue.validate(queue)

    results: list[dict[str, Any]] = []
    summary = {"total": 0, "passed": 0, "blocked": 0, "handoff": 0, "deficiency": 0}
    execution_mode = str(queue.get("execution_mode") or "dry_run")
    approved_adapter_evidence_mode = queue.get("approved_adapter_evidence_mode") is True
    batch_errors = [f"case_queue: {err}" for err in queue_errors]
    batch_warnings = [f"case_queue: {warn}" for warn in queue_warnings]

    if execution_mode == "approved_adapter":
        if approved_adapter_evidence_mode:
            batch_warnings.append("approved_adapter_evidence_mode_local_validation_only")
        else:
            batch_errors.append("approved_adapter_execution_requires_evidence_mode_in_offline_runner")

    items = queue.get("items") if isinstance(queue.get("items"), list) else []
    for item in items:
        if not isinstance(item, dict):
            continue
        validator_errors: list[str] = []
        validator_warnings: list[str] = []
        validators_run: list[str] = []

        for validator_name in item.get("required_validators", []):
            validators_run.append(str(validator_name))
            try:
                ok, errors, warnings = run_validator(
                    scripts_dir=scripts_dir,
                    queue_path=queue_path,
                    item=item,
                    name=str(validator_name),
                )
            except Exception as exc:  # Keep processing other cases.
                ok, errors, warnings = False, [str(exc)], []
            validator_errors.extend(errors)
            validator_warnings.extend(warnings)
            if not ok:
                validator_errors.append(f"{validator_name}: failed")

        expected = str(item.get("expected_outcome") or "")
        outcome = normalized_outcome(expected, validator_errors)
        if outcome not in summary:
            outcome = "blocked"
        summary[outcome] += 1
        summary["total"] += 1

        results.append(
            {
                "case_id": item.get("case_id"),
                "input_status": item.get("current_status"),
                "output_status": item.get("target_status"),
                "expected_outcome": expected,
                "legal_gate_mode": item.get("legal_gate_mode") or "",
                "external_lawyer_involved": item.get("external_lawyer_involved") is True,
                "decision": decision_for(expected, outcome),
                "outcome": outcome,
                "validators_run": validators_run,
                "errors": validator_errors,
                "warnings": validator_warnings,
                "next_action": next_action_for(expected, outcome, item),
                "owner": item.get("owner"),
                "official_system_touched": False,
                "official_submission_performed": False,
                "generator_official_system_touched": False,
                "generator_official_submission_performed": False,
                "generator_adapter_execution_performed": False,
            }
        )

    result = {
        "queue_id": queue.get("queue_id"),
        "processed_at": utc_plus_8_now(),
        "execution_mode": execution_mode,
        "approved_adapter_evidence_mode": approved_adapter_evidence_mode,
        "official_system_touched": False,
        "official_submission_performed": False,
        "generator_official_system_touched": False,
        "generator_official_submission_performed": False,
        "generator_adapter_execution_performed": False,
        "summary": summary,
        "results": results,
        "batch_errors": batch_errors,
        "batch_warnings": batch_warnings,
    }

    result_ok, result_errors, result_warnings = validate_batch_processor_result.validate(result)
    if not result_ok:
        result["batch_errors"].extend([f"batch_result: {err}" for err in result_errors])
    result["batch_warnings"].extend([f"batch_result: {warn}" for warn in result_warnings])

    exit_code = 0 if queue_ok and result_ok and not result["batch_errors"] else 1
    return result, exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("queue", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--scripts-dir", type=Path)
    args = parser.parse_args()

    queue_path = args.queue.resolve()
    scripts_dir = args.scripts_dir.resolve() if args.scripts_dir else Path(__file__).resolve().parent
    result, exit_code = process_queue(queue_path, scripts_dir)

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
