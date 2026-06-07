#!/usr/bin/env python3
"""Orchestrate raw patent intake into a package, disclosure scaffold, and audit queue."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import normalize_invention_disclosure
import prepare_case_package
import run_case_queue
import validate_artifact_hash_manifest


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_item(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [sha256_item(path, output_dir) for path in files],
    }


def render_report(
    case_id: str,
    package_response: dict[str, Any],
    scaffold_response: dict[str, Any],
    queue: dict[str, Any],
    result: dict[str, Any],
    manifest: dict[str, Any],
) -> str:
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    package_warnings = package_response.get("package_warnings", []) + package_response.get("source_warnings", [])
    scaffold_warnings = scaffold_response.get("scaffold_warnings", [])

    lines = [
        "# Case Intake Orchestration Report",
        "",
        f"Case ID: {case_id}",
        f"Queue ID: {queue.get('queue_id')}",
        "Execution mode: dry_run",
        "Official system touched: no",
        "Official submission performed: no",
        "Filing allowed: no",
        "Draft generation allowed: no",
        "Legal gate metadata: present",
        "External professional involved: no",
        "",
        "## Pipeline",
        "",
        "| Step | Status | Boundary |",
        "| --- | --- | --- |",
        f"| Case package | {'pass' if package_response.get('ok') else 'fail'} | intake_received only |",
        f"| Disclosure scaffold | {'pass' if scaffold_response.get('ok') else 'fail'} | scaffold_pending_confirmation only |",
        f"| Dry-run queue | {'pass' if not result.get('batch_errors') else 'fail'} | local validators only |",
        "",
        "## Pending Confirmations",
        "",
        "- Inventor contribution confirmation.",
        "- Applicant and ownership basis.",
        "- AI legal/compliance gate confirmation.",
        "- No-copying and no-synonym-substitution confirmation.",
        "- Technical effects and evidence mapping.",
        "- Secrecy or foreign-filing review.",
        "",
        "## Queue Summary",
        "",
        f"- Total: {summary.get('total', 0)}",
        f"- Passed: {summary.get('passed', 0)}",
        f"- Blocked: {summary.get('blocked', 0)}",
        f"- Handoff: {summary.get('handoff', 0)}",
        f"- Deficiency: {summary.get('deficiency', 0)}",
        "",
        "## Warnings",
        "",
    ]
    warnings = package_warnings + scaffold_warnings + result.get("batch_warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This orchestration receives raw materials, creates an offline case package, creates a pending-confirmation disclosure scaffold, and runs local validation. It does not draft an AI self-filing authorization-ready patent application, log in, sign, pay, submit, capture a real receipt, or create an application number.",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for item in manifest.get("files", []):
        lines.append(f"- {item.get('path')}: {item.get('sha256')}")
    return "\n".join(lines) + "\n"


def orchestrate_intake(
    raw_input_dir: Path,
    output_dir: Path,
    case_id: str,
    received_from: str,
    jurisdiction: str,
    intake_mode: str,
    queue_owner: str,
    scripts_dir: Path,
) -> tuple[dict[str, Any], int]:
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    package_dir = output_root / "case-package"
    scaffold_dir = output_root / "disclosure-normalization-scaffold"
    queue_path = output_root / "case-queue.json"
    result_path = output_root / "batch-processor-result.json"
    report_path = output_root / "intake-orchestration-report.md"
    manifest_path = output_root / "artifact-hashes.json"

    package_response, package_exit = prepare_case_package.prepare_package(
        source_dir=raw_input_dir,
        output_dir=package_dir,
        case_id=case_id,
        received_from=received_from,
        jurisdiction=jurisdiction,
        intake_mode=intake_mode,
    )

    scaffold_response, scaffold_exit = normalize_invention_disclosure.normalize(
        case_package=package_dir,
        output_dir=scaffold_dir,
    )

    queue = build_case_queue.build_queue(
        case_folders=[scaffold_dir],
        output_base=output_root,
        queue_id=f"{case_id}-INTAKE-QUEUE",
        queue_owner=queue_owner,
        execution_mode="dry_run",
    )
    write_json(queue_path, queue)

    result, runner_exit = run_case_queue.process_queue(queue_path, scripts_dir)
    write_json(result_path, result)

    artifact_files = [
        package_dir / "case-package-manifest.json",
        package_dir / "01-normalized" / "source-material-manifest.json",
        package_dir / "filing-status.json",
        package_dir / "intake-report.md",
        scaffold_dir / "invention-disclosure-scaffold.json",
        scaffold_dir / "normalization-report.md",
        queue_path,
        result_path,
    ]
    provisional_manifest = build_manifest(output_root, case_id, artifact_files)
    report_path.write_text(
        render_report(case_id, package_response, scaffold_response, queue, result, provisional_manifest),
        encoding="utf-8",
    )

    final_manifest = build_manifest(output_root, case_id, artifact_files + [report_path])
    write_json(manifest_path, final_manifest)
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    ok = (
        package_exit == 0
        and scaffold_exit == 0
        and runner_exit == 0
        and manifest_ok
        and result.get("official_system_touched") is False
        and result.get("official_submission_performed") is False
    )
    response = {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "case_package": str(package_dir),
            "disclosure_scaffold": str(scaffold_dir),
            "case_queue": str(queue_path),
            "batch_processor_result": str(result_path),
            "intake_orchestration_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
        "package_errors": package_response.get("package_errors", []) + package_response.get("source_errors", []),
        "package_warnings": package_response.get("package_warnings", []) + package_response.get("source_warnings", []),
        "scaffold_errors": scaffold_response.get("scaffold_errors", []),
        "scaffold_warnings": scaffold_response.get("scaffold_warnings", []),
        "batch_errors": result.get("batch_errors", []),
        "batch_warnings": result.get("batch_warnings", []),
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "filing_allowed": False,
        "draft_generation_allowed": False,
        "official_system_touched": False,
        "official_submission_performed": False,
    }
    return response, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_input_dir", type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--received-from", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--jurisdiction", default="CN")
    parser.add_argument("--intake-mode", choices=["manual_upload", "email", "api", "batch_import"], default="manual_upload")
    parser.add_argument("--queue-owner", default="Patent Capital OS")
    parser.add_argument("--scripts-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    scripts_dir = args.scripts_dir.resolve() if args.scripts_dir else Path(__file__).resolve().parent
    try:
        response, exit_code = orchestrate_intake(
            raw_input_dir=args.raw_input_dir,
            output_dir=args.output_dir,
            case_id=args.case_id,
            received_from=args.received_from,
            jurisdiction=args.jurisdiction,
            intake_mode=args.intake_mode,
            queue_owner=args.queue_owner,
            scripts_dir=scripts_dir,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "filing_allowed": False,
            "draft_generation_allowed": False,
            "official_system_touched": False,
            "official_submission_performed": False,
        }, 1

    rendered = json.dumps(response, ensure_ascii=False, indent=2)
    if args.json:
        print(rendered)
    else:
        print("PASS" if response.get("ok") else "FAIL")
        print(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
