#!/usr/bin/env python3
"""Process an inbox of raw material folders into read-only handoff packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import build_case_queue
import orchestrate_pre_submission_to_handoff
import run_case_queue
import validate_artifact_hash_manifest


CASE_ID_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_item(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_manifest(output_dir: Path, inbox_id: str, files: list[Path]) -> dict[str, Any]:
    root = output_dir.resolve()
    entries: list[dict[str, Any]] = []
    for path in files:
        if not path.exists() or not path.is_file():
            continue
        try:
            path.resolve().relative_to(root)
        except ValueError:
            continue
        entries.append(sha256_item(path, root))
    return {
        "case_id": inbox_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": entries,
    }


def sanitize_case_id(value: str) -> str:
    cleaned = CASE_ID_RE.sub("-", value.strip()).strip(".-")
    return cleaned or "CASE"


def safe_child_path(base_dir: Path, rel_value: str, label: str) -> Path:
    rel_path = Path(rel_value)
    if rel_path.is_absolute() or ".." in rel_path.parts:
        raise ValueError(f"unsafe_{label}: {rel_value}")
    resolved = (base_dir / rel_path).resolve()
    try:
        resolved.relative_to(base_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"{label}_outside_case_dir: {rel_value}") from exc
    return resolved


def load_case_config(case_dir: Path) -> dict[str, Any]:
    config_path = case_dir / "case-config.json"
    if not config_path.exists():
        return {}
    config = load_json(config_path)
    if not isinstance(config, dict):
        raise ValueError(f"case_config_not_object: {config_path}")
    return config


def case_dirs(inbox_dir: Path) -> list[Path]:
    folders = [
        item
        for item in sorted(inbox_dir.iterdir(), key=lambda path: path.name.lower())
        if item.is_dir() and not item.name.startswith(".")
    ]
    if not folders:
        raise ValueError(f"inbox_has_no_case_folders: {inbox_dir}")
    return folders


def resolve_raw_input(case_dir: Path, config: dict[str, Any]) -> Path:
    if config.get("raw_input_dir"):
        raw_dir = safe_child_path(case_dir, str(config["raw_input_dir"]), "raw_input_dir")
    else:
        candidate = case_dir / "raw-input"
        raw_dir = candidate if candidate.exists() else case_dir
    if not raw_dir.exists() or not raw_dir.is_dir():
        raise FileNotFoundError(f"raw_input_dir_missing: {raw_dir}")
    return raw_dir


def resolve_optional_case_file(case_dir: Path, config: dict[str, Any], key: str) -> Path | None:
    value = config.get(key)
    if value in (None, ""):
        return None
    path = safe_child_path(case_dir, str(value), key)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"{key}_missing: {path}")
    return path


def render_report(result: dict[str, Any], manifest: dict[str, Any]) -> str:
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    lines = [
        "# Inbox To Handoff Report",
        "",
        f"Inbox ID: {result.get('inbox_id')}",
        f"Pipeline status: {'pass' if result.get('ok') else 'fail'}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        "Official system touched: no",
        "Official submission performed: no",
        "Adapter execution performed: no",
        "Automatic submission performed: no",
        "External lawyer involved: no",
        "",
        "## Summary",
        "",
        f"- Total: {summary.get('total', 0)}",
        f"- Passed: {summary.get('passed', 0)}",
        f"- Blocked: {summary.get('blocked', 0)}",
        "",
        "## Cases",
        "",
        "| Case | Status | Decision | Reference delta | Output |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in result.get("case_results", []):
        if not isinstance(item, dict):
            continue
        reference_delta = "yes" if item.get("reference_delta_source") else "no"
        lines.append(
            f"| {item.get('case_id')} | {'pass' if item.get('ok') else 'fail'} | "
            f"{item.get('decision')} | {reference_delta} | {item.get('output_dir')} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This inbox orchestration processes received raw material folders into local read-only handoff packages. It does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for item in manifest.get("files", []):
        lines.append(f"- {item.get('path')}: {item.get('sha256')}")
    return "\n".join(lines) + "\n"


def orchestrate(
    inbox_dir: Path,
    output_dir: Path,
    inbox_id: str,
    confirmation_packet_template: Path,
    ai_self_filing_source_template: Path,
    official_preflight_source_template: Path,
    queue_owner: str,
    scripts_dir: Path,
) -> tuple[dict[str, Any], int]:
    inbox_root = inbox_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    processed_dir = output_root / "processed-cases"
    result_path = output_root / "inbox-to-handoff-result.json"
    report_path = output_root / "inbox-to-handoff-report.md"
    queue_path = output_root / "case-queue.json"
    batch_result_path = output_root / "batch-processor-result.json"
    manifest_path = output_root / "artifact-hashes.json"
    if processed_dir.exists() or result_path.exists() or queue_path.exists() or batch_result_path.exists():
        response = {
            "ok": False,
            "errors": [f"output_dir_already_has_inbox_outputs: {output_root}"],
            "official_system_touched": False,
            "official_submission_performed": False,
            "adapter_execution_performed": False,
            "automatic_submission_performed": False,
            "external_lawyer_involved": False,
        }
        return response, 1
    processed_dir.mkdir(parents=True, exist_ok=True)

    case_results: list[dict[str, Any]] = []
    case_output_dirs: list[Path] = []
    for index, case_dir in enumerate(case_dirs(inbox_root), start=1):
        config = load_case_config(case_dir)
        case_id = sanitize_case_id(str(config.get("case_id") or case_dir.name))
        received_from = str(config.get("received_from") or case_dir.name)
        jurisdiction = str(config.get("jurisdiction") or "CN")
        intake_mode = str(config.get("intake_mode") or "batch_import")
        raw_input_dir = resolve_raw_input(case_dir, config)
        reference_delta_source = resolve_optional_case_file(case_dir, config, "reference_delta_source")
        case_output_dir = processed_dir / f"{index:03d}-{case_id}"

        response, exit_code = orchestrate_pre_submission_to_handoff.orchestrate(
            raw_input_dir=raw_input_dir,
            confirmation_packet_template=confirmation_packet_template,
            ai_self_filing_source_template=ai_self_filing_source_template,
            official_preflight_source_template=official_preflight_source_template,
            reference_delta_source_template=reference_delta_source,
            output_dir=case_output_dir,
            case_id=case_id,
            received_from=received_from,
            jurisdiction=jurisdiction,
            intake_mode=intake_mode,
        )
        case_output_dirs.append(case_output_dir)
        case_results.append(
            {
                "ok": exit_code == 0 and response.get("ok") is True,
                "case_id": case_id,
                "source_case_dir": str(case_dir),
                "raw_input_dir": str(raw_input_dir),
                "output_dir": str(case_output_dir),
                "reference_delta_source": str(reference_delta_source) if reference_delta_source else "",
                "decision": "handoff_ready_no_auto_submit" if response.get("ok") is True else "blocked",
                "artifacts": response.get("artifacts", {}),
                "errors": response.get("errors", []) + response.get("manifest_errors", []),
                "warnings": response.get("warnings", []) + response.get("manifest_warnings", []),
            }
        )

    queue = build_case_queue.build_queue(
        case_folders=case_output_dirs,
        output_base=output_root,
        queue_id=f"{inbox_id}-QUEUE",
        queue_owner=queue_owner,
        execution_mode="dry_run",
    )
    write_json(queue_path, queue)

    batch_result, runner_exit = run_case_queue.process_queue(queue_path, scripts_dir)
    write_json(batch_result_path, batch_result)

    summary = batch_result.get("summary") if isinstance(batch_result.get("summary"), dict) else {}
    case_ok = all(item.get("ok") is True for item in case_results)
    batch_ok = runner_exit == 0 and batch_result.get("official_system_touched") is False and batch_result.get("official_submission_performed") is False
    result = {
        "ok": case_ok and batch_ok,
        "inbox_id": inbox_id,
        "pipeline_type": "inbox_to_handoff_ai_self_filing_no_external_lawyer",
        "created_at": build_case_queue.utc_plus_8_now(),
        "status": "approved_for_adapter_execution" if case_ok and batch_ok else "inbox_to_handoff_blocked",
        "decision": "handoff_ready_no_auto_submit" if case_ok and batch_ok else "cure_inbox_to_handoff_errors",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "summary": summary,
        "case_results": case_results,
        "artifacts": {
            "case_queue": str(queue_path),
            "batch_processor_result": str(batch_result_path),
            "inbox_to_handoff_result": str(result_path),
            "inbox_to_handoff_report": str(report_path),
            "artifact_hashes": str(manifest_path),
            "processed_cases": str(processed_dir),
        },
        "next_action": "Use each read-only handoff package only as approved-adapter execution input evidence; adapter execution, receipt capture, and application-number evidence remain separate gates.",
    }
    write_json(result_path, result)

    manifest_files = [
        queue_path,
        batch_result_path,
        *[case_dir / "artifact-hashes.json" for case_dir in case_output_dirs],
        result_path,
    ]
    provisional_manifest = build_manifest(output_root, inbox_id, manifest_files)
    report_path.write_text(render_report(result, provisional_manifest), encoding="utf-8")
    write_json(manifest_path, build_manifest(output_root, inbox_id, [*manifest_files, report_path]))
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    result["manifest_errors"] = manifest_errors
    result["manifest_warnings"] = manifest_warnings
    result["ok"] = result["ok"] and manifest_ok
    write_json(result_path, result)
    write_json(manifest_path, build_manifest(output_root, inbox_id, [*manifest_files, report_path]))
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)
    result["manifest_errors"] = manifest_errors
    result["manifest_warnings"] = manifest_warnings
    result["ok"] = result["ok"] and manifest_ok
    write_json(result_path, result)
    write_json(manifest_path, build_manifest(output_root, inbox_id, [*manifest_files, report_path]))

    response = {
        "ok": result["ok"],
        "inbox_id": inbox_id,
        "output_dir": str(output_root),
        "artifacts": result["artifacts"],
        "summary": summary,
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
    parser.add_argument("inbox_dir", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--inbox-id", required=True)
    parser.add_argument("--confirmation-packet-template", required=True, type=Path)
    parser.add_argument("--ai-self-filing-source-template", required=True, type=Path)
    parser.add_argument("--official-preflight-source-template", type=Path)
    parser.add_argument("--queue-owner", default="Patent Capital OS")
    parser.add_argument("--scripts-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = orchestrate(
            inbox_dir=args.inbox_dir,
            output_dir=args.output_dir,
            inbox_id=args.inbox_id,
            confirmation_packet_template=args.confirmation_packet_template,
            ai_self_filing_source_template=args.ai_self_filing_source_template,
            official_preflight_source_template=(
                args.official_preflight_source_template
                if args.official_preflight_source_template
                else Path(__file__).resolve().parents[1] / "benchmarks" / "ai-self-filing-official-ready" / "official-preflight-source.json"
            ),
            queue_owner=args.queue_owner,
            scripts_dir=args.scripts_dir.resolve() if args.scripts_dir else Path(__file__).resolve().parent,
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
