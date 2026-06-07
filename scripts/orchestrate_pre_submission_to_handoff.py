#!/usr/bin/env python3
"""Run local pre-submission and then prepare a read-only handoff package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import build_case_queue
import orchestrate_pre_submission_pipeline
import prepare_pre_submission_handoff_package
import validate_artifact_hash_manifest
import validate_pre_submission_handoff_package
import validate_pre_submission_pipeline_benchmark


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_item(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    existing = [path for path in files if path.exists()]
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [sha256_item(path, output_dir) for path in existing],
    }


def stage_entry(name: str, response: dict[str, Any], exit_code: int, output_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for key in ["errors", "manifest_errors"]:
        value = response.get(key)
        if isinstance(value, list):
            errors.extend(str(item) for item in value)
    for key in ["warnings", "manifest_warnings"]:
        value = response.get(key)
        if isinstance(value, list):
            warnings.extend(str(item) for item in value)
    return {
        "ok": exit_code == 0 and response.get("ok") is True,
        "exit_code": exit_code,
        "output_dir": str(output_dir),
        "artifacts": response.get("artifacts", {}),
        "errors": errors,
        "warnings": warnings,
    }


def validation_entry(
    name: str,
    validator: Callable[[Path], tuple[bool, list[str], list[str]]],
    folder: Path,
) -> dict[str, Any]:
    try:
        ok, errors, warnings = validator(folder)
    except Exception as exc:
        ok, errors, warnings = False, [str(exc)], []
    return {
        "ok": ok,
        "validator": name,
        "target": str(folder),
        "errors": errors,
        "warnings": warnings,
    }


def render_report(result: dict[str, Any]) -> str:
    stages = result.get("stages") if isinstance(result.get("stages"), dict) else {}
    validations = result.get("validations") if isinstance(result.get("validations"), dict) else {}
    artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {}
    lines = [
        "# Pre-submission To Handoff Report",
        "",
        f"Case ID: {result.get('case_id')}",
        f"Pipeline status: {'pass' if result.get('ok') else 'fail'}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        "Official system touched: no",
        "Official submission performed: no",
        "Adapter execution performed: no",
        "Automatic submission performed: no",
        "External lawyer involved: no",
        "",
        "## Stages",
        "",
        "| Stage | Status | Output |",
        "| --- | --- | --- |",
    ]
    for name in ["pre_submission_pipeline", "pre_submission_handoff_package"]:
        stage = stages.get(name) if isinstance(stages.get(name), dict) else {}
        lines.append(f"| {name} | {'pass' if stage.get('ok') else 'fail'} | {stage.get('output_dir')} |")
    lines.extend(["", "## Validations", "", "| Validator | Status | Target |", "| --- | --- | --- |"])
    for name in ["pre_submission_pipeline", "pre_submission_handoff_package"]:
        validation = validations.get(name) if isinstance(validations.get(name), dict) else {}
        lines.append(f"| {validation.get('validator')} | {'pass' if validation.get('ok') else 'fail'} | {validation.get('target')} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This orchestration prepares a read-only handoff package after local pre-submission passes. It does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.",
            "",
            "## Next Action",
            "",
            str(result.get("next_action") or ""),
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for key, value in sorted(artifacts.items()):
        lines.append(f"- {key}: {value}")
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
    if output_root.exists() and any(output_root.iterdir()):
        response = {
            "ok": False,
            "errors": [f"output_dir_exists_and_is_not_empty: {output_root}"],
            "official_system_touched": False,
            "official_submission_performed": False,
            "adapter_execution_performed": False,
            "automatic_submission_performed": False,
            "external_lawyer_involved": False,
        }
        return response, 1
    output_root.mkdir(parents=True, exist_ok=True)

    pre_submission_dir = output_root / "pre-submission-pipeline"
    handoff_dir = output_root / "pre-submission-handoff-package"
    result_path = output_root / "pre-submission-to-handoff-result.json"
    report_path = output_root / "pre-submission-to-handoff-report.md"
    manifest_path = output_root / "artifact-hashes.json"

    pipeline_response, pipeline_exit = orchestrate_pre_submission_pipeline.orchestrate(
        raw_input_dir=raw_input_dir,
        confirmation_packet_template=confirmation_packet_template,
        ai_self_filing_source_template=ai_self_filing_source_template,
        official_preflight_source_template=official_preflight_source_template,
        reference_delta_source_template=reference_delta_source_template,
        output_dir=pre_submission_dir,
        case_id=case_id,
        received_from=received_from,
        jurisdiction=jurisdiction,
        intake_mode=intake_mode,
    )
    pipeline_stage = stage_entry("pre_submission_pipeline", pipeline_response, pipeline_exit, pre_submission_dir)
    pipeline_validation = validation_entry(
        "validate_pre_submission_pipeline_benchmark",
        validate_pre_submission_pipeline_benchmark.validate,
        pre_submission_dir,
    )

    if pipeline_stage["ok"] and pipeline_validation["ok"]:
        handoff_response = prepare_pre_submission_handoff_package.run(pre_submission_dir, handoff_dir)
        handoff_exit = 0 if handoff_response.get("ok") is True else 1
    else:
        handoff_response = {
            "ok": False,
            "errors": ["pre_submission_pipeline_not_validated"],
            "warnings": [],
            "official_system_touched": False,
            "official_submission_performed": False,
            "adapter_execution_performed": False,
            "automatic_submission_performed": False,
            "external_lawyer_involved": False,
        }
        handoff_exit = 1
    handoff_stage = stage_entry("pre_submission_handoff_package", handoff_response, handoff_exit, handoff_dir)
    handoff_validation = validation_entry(
        "validate_pre_submission_handoff_package",
        validate_pre_submission_handoff_package.validate,
        handoff_dir,
    )

    pipeline_result_path = pre_submission_dir / "pre-submission-pipeline-result.json"
    handoff_package_path = handoff_dir / "pre-submission-handoff-package.json"
    pipeline_result = load_json(pipeline_result_path) if pipeline_result_path.exists() else {}
    handoff_package = load_json(handoff_package_path) if handoff_package_path.exists() else {}
    lifecycle_trace_path = pre_submission_dir / "case-lifecycle-trace" / "case-lifecycle-trace.json"

    base_ok = (
        pipeline_stage["ok"]
        and handoff_stage["ok"]
        and pipeline_validation["ok"]
        and handoff_validation["ok"]
        and pipeline_result.get("official_system_touched") is False
        and pipeline_result.get("official_submission_performed") is False
        and pipeline_result.get("adapter_execution_performed") is False
        and pipeline_result.get("automatic_submission_performed") is False
        and pipeline_result.get("external_lawyer_involved") is False
        and handoff_package.get("official_system_touched") is False
        and handoff_package.get("official_submission_performed") is False
        and handoff_package.get("adapter_execution_performed") is False
        and handoff_package.get("automatic_submission_performed") is False
        and handoff_package.get("external_lawyer_involved") is False
    )

    result = {
        "ok": base_ok,
        "case_id": str(pipeline_result.get("case_id") or handoff_package.get("case_id") or case_id),
        "pipeline_type": "pre_submission_to_handoff_ai_self_filing_no_external_lawyer",
        "created_at": build_case_queue.utc_plus_8_now(),
        "status": "approved_for_adapter_execution" if base_ok else "pre_submission_to_handoff_blocked",
        "decision": "handoff_ready_no_auto_submit" if base_ok else "cure_pre_submission_to_handoff_errors",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "pre_submission_lifecycle_gate": pipeline_result.get("pre_submission_lifecycle_gate"),
        "lifecycle_trace_hash": pipeline_result.get("lifecycle_trace_hash"),
        "source_pre_submission_hash": sha256_file(pipeline_result_path) if pipeline_result_path.exists() else "",
        "handoff_package_hash": sha256_file(handoff_package_path) if handoff_package_path.exists() else "",
        **(
            {"reference_patent_delta_hash": pipeline_result.get("reference_patent_delta_hash")}
            if pipeline_result.get("reference_patent_delta_hash")
            else {}
        ),
        "reference_delta_rows_count": handoff_package.get("reference_delta_rows_count"),
        "reference_delta_claim_elements_count": handoff_package.get("reference_delta_claim_elements_count"),
        "reference_delta_boundary_preserved": handoff_package.get("reference_delta_boundary_preserved"),
        "stages": {
            "pre_submission_pipeline": pipeline_stage,
            "pre_submission_handoff_package": handoff_stage,
        },
        "validations": {
            "pre_submission_pipeline": pipeline_validation,
            "pre_submission_handoff_package": handoff_validation,
        },
        "artifacts": {
            "pre_submission_pipeline": str(pre_submission_dir),
            "pre_submission_pipeline_result": str(pipeline_result_path),
            "pre_submission_handoff_package": str(handoff_package_path),
            "pre_submission_handoff_report": str(handoff_dir / "pre-submission-handoff-report.md"),
            "case_lifecycle_trace": str(lifecycle_trace_path),
            "pre_submission_to_handoff_result": str(result_path),
            "pre_submission_to_handoff_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
        "next_action": "Use the read-only handoff package as approved-adapter execution input evidence only; adapter execution, receipt capture, and application-number evidence remain separate gates.",
    }

    write_json(result_path, result)
    report_path.write_text(render_report(result), encoding="utf-8")
    manifest_files = [
        pre_submission_dir / "artifact-hashes.json",
        handoff_dir / "artifact-hashes.json",
        result_path,
        report_path,
    ]
    write_json(manifest_path, build_manifest(output_root, result["case_id"], manifest_files))
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    result["manifest_errors"] = manifest_errors
    result["manifest_warnings"] = manifest_warnings
    result["ok"] = base_ok and manifest_ok
    write_json(result_path, result)
    write_json(manifest_path, build_manifest(output_root, result["case_id"], manifest_files))
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)
    result["manifest_errors"] = manifest_errors
    result["manifest_warnings"] = manifest_warnings
    result["ok"] = base_ok and manifest_ok
    write_json(result_path, result)
    write_json(manifest_path, build_manifest(output_root, result["case_id"], manifest_files))

    response = {
        "ok": result["ok"],
        "case_id": result["case_id"],
        "output_dir": str(output_root),
        "artifacts": result["artifacts"],
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "external_lawyer_involved": False,
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
            "automatic_submission_performed": False,
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
