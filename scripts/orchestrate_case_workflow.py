#!/usr/bin/env python3
"""Orchestrate an offline Patent Capital OS queue workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import run_case_queue
import validate_artifact_hash_manifest


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_item(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    rel = path.relative_to(root).as_posix()
    return {
        "path": rel,
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_manifest(output_dir: Path, queue_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": queue_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [sha256_item(path, output_dir) for path in files],
    }


def render_report(queue: dict[str, Any], result: dict[str, Any], manifest: dict[str, Any]) -> str:
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    lines = [
        "# Workflow Orchestration Report",
        "",
        f"Queue ID: {queue.get('queue_id')}",
        f"Execution mode: {queue.get('execution_mode')}",
        "Official system touched: no",
        "Official submission performed: no",
        "External professional involved: no",
        "Legal gate metadata: present",
        "Offline orchestration only: yes",
        "",
        "## Summary",
        "",
        f"- Total: {summary.get('total', 0)}",
        f"- Passed: {summary.get('passed', 0)}",
        f"- Blocked: {summary.get('blocked', 0)}",
        f"- Handoff: {summary.get('handoff', 0)}",
        f"- Deficiency: {summary.get('deficiency', 0)}",
        "",
        "## Per-Case Results",
        "",
        "| Case | Input status | Output status | Outcome | Decision | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in result.get("results", []):
        if not isinstance(item, dict):
            continue
        next_action = str(item.get("next_action") or "").replace("|", "/")
        lines.append(
            f"| {item.get('case_id')} | {item.get('input_status')} | {item.get('output_status')} | "
            f"{item.get('outcome')} | {item.get('decision')} | {next_action} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This orchestrator builds and runs local validation queues. It does not log in, sign, pay, submit, capture a real receipt, or create an application number.",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for item in manifest.get("files", []):
        lines.append(f"- {item.get('path')}: {item.get('sha256')}")
    return "\n".join(lines) + "\n"


def orchestrate(
    case_folders: list[Path],
    output_dir: Path,
    queue_id: str,
    queue_owner: str,
    execution_mode: str,
    scripts_dir: Path,
) -> tuple[dict[str, Any], int]:
    output_dir.mkdir(parents=True, exist_ok=True)

    queue_path = output_dir / "case-queue.json"
    result_path = output_dir / "batch-processor-result.json"
    report_path = output_dir / "orchestration-report.md"
    manifest_path = output_dir / "artifact-hashes.json"

    queue = build_case_queue.build_queue(
        case_folders=case_folders,
        output_base=output_dir,
        queue_id=queue_id,
        queue_owner=queue_owner,
        execution_mode=execution_mode,
    )
    write_json(queue_path, queue)

    result, exit_code = run_case_queue.process_queue(queue_path, scripts_dir)
    write_json(result_path, result)

    provisional_manifest = build_manifest(output_dir, queue_id, [queue_path, result_path])
    report_path.write_text(render_report(queue, result, provisional_manifest), encoding="utf-8")

    final_manifest = build_manifest(output_dir, queue_id, [queue_path, result_path, report_path])
    write_json(manifest_path, final_manifest)
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    ok = exit_code == 0 and manifest_ok
    response = {
        "ok": ok,
        "queue_id": queue_id,
        "output_dir": str(output_dir),
        "artifacts": {
            "case_queue": str(queue_path),
            "batch_processor_result": str(result_path),
            "orchestration_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
        "summary": result.get("summary", {}),
        "batch_errors": result.get("batch_errors", []),
        "batch_warnings": result.get("batch_warnings", []),
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
    }
    return response, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_folders", nargs="+", type=Path)
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--queue-owner", default="Patent Capital OS")
    parser.add_argument("--execution-mode", choices=["dry_run", "handoff"], default="dry_run")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--scripts-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    scripts_dir = args.scripts_dir.resolve() if args.scripts_dir else Path(__file__).resolve().parent
    response, exit_code = orchestrate(
        case_folders=args.case_folders,
        output_dir=args.output_dir.resolve(),
        queue_id=args.queue_id,
        queue_owner=args.queue_owner,
        execution_mode=args.execution_mode,
        scripts_dir=scripts_dir,
    )
    rendered = json.dumps(response, ensure_ascii=False, indent=2)
    if args.json:
        print(rendered)
    else:
        print("PASS" if response["ok"] else "FAIL")
        print(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
