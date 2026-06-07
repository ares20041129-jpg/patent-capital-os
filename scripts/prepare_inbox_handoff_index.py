#!/usr/bin/env python3
"""Prepare a read-only index for inbox-to-handoff outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest


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
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [sha256_item(path, output_dir) for path in files if path.exists() and path.is_file()],
    }


def display_path(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        try:
            return Path("..", *path.resolve().relative_to(base.resolve().parent).parts).as_posix()
        except ValueError:
            return str(path.resolve())


def resolve_path(raw: Any, base: Path) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        return path.resolve()
    return (base / path).resolve()


def artifact_ref(path: Path, base: Path) -> dict[str, Any]:
    return {
        "path": display_path(path, base),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else "",
    }


def find_quality_review(case_dir: Path) -> dict[str, Any]:
    path = (
        case_dir
        / "pre-submission-pipeline"
        / "application-materials-pipeline"
        / "application-materials-quality-gate"
        / "application-materials-quality-review.json"
    )
    if not path.exists():
        return {"status": "missing", "weighted_score": 0}
    review = load_json(path)
    gate = review.get("quality_gate") if isinstance(review.get("quality_gate"), dict) else {}
    return {
        "status": gate.get("status") or "unknown",
        "weighted_score": gate.get("weighted_score", 0),
        "minimum_score_for_official_preflight": gate.get("minimum_score_for_official_preflight", 85),
        "official_preflight_allowed": gate.get("official_preflight_allowed") is True,
        "review_path": display_path(path, case_dir.parent.parent),
        "review_hash": sha256_file(path),
    }


def build_case_index(
    item: dict[str, Any],
    source_root: Path,
    output_root: Path,
    batch_by_case: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    case_id = str(item.get("case_id") or "")
    case_output_dir = resolve_path(item.get("output_dir"), source_root)
    result_path = case_output_dir / "pre-submission-to-handoff-result.json"
    handoff_path = case_output_dir / "pre-submission-handoff-package" / "pre-submission-handoff-package.json"
    result = load_json(result_path) if result_path.exists() else {}
    handoff = load_json(handoff_path) if handoff_path.exists() else {}
    batch_item = batch_by_case.get(case_id, {})
    quality = find_quality_review(case_output_dir)
    reference_delta_present = bool(result.get("reference_patent_delta_hash") or item.get("reference_delta_source"))
    warnings = item.get("warnings") if isinstance(item.get("warnings"), list) else []
    errors = item.get("errors") if isinstance(item.get("errors"), list) else []
    batch_warnings = batch_item.get("warnings") if isinstance(batch_item.get("warnings"), list) else []
    batch_errors = batch_item.get("errors") if isinstance(batch_item.get("errors"), list) else []

    return {
        "case_id": case_id,
        "status": result.get("status") or "unknown",
        "decision": result.get("decision") or item.get("decision") or "",
        "legal_gate_mode": result.get("legal_gate_mode") or "ai_self_filing_no_external_lawyer",
        "quality_gate": quality,
        "reference_delta_present": reference_delta_present,
        "reference_patent_delta_hash": result.get("reference_patent_delta_hash") or "",
        "reference_delta_rows_count": result.get("reference_delta_rows_count") or 0,
        "reference_delta_claim_elements_count": result.get("reference_delta_claim_elements_count") or 0,
        "reference_delta_boundary_preserved": result.get("reference_delta_boundary_preserved") is True,
        "pre_submission_to_handoff_result": artifact_ref(result_path, output_root),
        "handoff_package": artifact_ref(handoff_path, output_root),
        "handoff_package_hash": result.get("handoff_package_hash") or handoff.get("source_pre_submission_hash") or "",
        "lifecycle_trace_hash": result.get("lifecycle_trace_hash") or "",
        "source_pre_submission_hash": result.get("source_pre_submission_hash") or "",
        "output_dir": display_path(case_output_dir, output_root),
        "errors": [str(value) for value in [*errors, *batch_errors]][:10],
        "warnings": [str(value) for value in [*warnings, *batch_warnings]][:20],
        "warning_count": len(warnings) + len(batch_warnings),
        "next_action": batch_item.get("next_action")
        or result.get("next_action")
        or "Use the read-only handoff package only as approved-adapter execution input evidence.",
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "external_lawyer_involved": False,
    }


def render_report(index: dict[str, Any]) -> str:
    lines = [
        "# Inbox Handoff Index",
        "",
        f"Inbox ID: {index.get('inbox_id')}",
        f"Index status: {'pass' if index.get('ok') else 'fail'}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        "Official system touched: no",
        "Official submission performed: no",
        "Adapter execution performed: no",
        "Automatic submission performed: no",
        "External lawyer involved: no",
        "",
        "## Cases",
        "",
        "| Case | Status | Decision | Quality | Reference delta | Handoff hash |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in index.get("cases", []):
        if not isinstance(item, dict):
            continue
        quality = item.get("quality_gate") if isinstance(item.get("quality_gate"), dict) else {}
        lines.append(
            "| {case_id} | {status} | {decision} | {quality} | {delta} | {hash_value} |".format(
                case_id=item.get("case_id"),
                status=item.get("status"),
                decision=item.get("decision"),
                quality=quality.get("weighted_score", 0),
                delta="yes" if item.get("reference_delta_present") else "no",
                hash_value=item.get("handoff_package", {}).get("sha256", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This index summarizes local read-only handoff evidence. It does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.",
            "",
            "## Next Action",
            "",
            str(index.get("next_action") or ""),
        ]
    )
    return "\n".join(lines) + "\n"


def run(source_inbox_dir: Path, output_dir: Path, index_id: str) -> dict[str, Any]:
    source_root = source_inbox_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    result_path = source_root / "inbox-to-handoff-result.json"
    queue_path = source_root / "case-queue.json"
    batch_path = source_root / "batch-processor-result.json"
    source_manifest_path = source_root / "artifact-hashes.json"
    for required in [result_path, queue_path, batch_path, source_manifest_path]:
        if not required.exists():
            raise FileNotFoundError(f"missing_source_artifact: {required}")

    source_result = load_json(result_path)
    batch_result = load_json(batch_path)
    batch_by_case = {
        str(item.get("case_id")): item
        for item in batch_result.get("results", [])
        if isinstance(item, dict) and item.get("case_id")
    }
    cases = [
        build_case_index(item, source_root, output_root, batch_by_case)
        for item in source_result.get("case_results", [])
        if isinstance(item, dict)
    ]
    passed = sum(1 for item in cases if item.get("status") == "approved_for_adapter_execution")
    reference_delta_cases = sum(1 for item in cases if item.get("reference_delta_present") is True)
    ok = (
        source_result.get("ok") is True
        and batch_result.get("official_system_touched") is False
        and batch_result.get("official_submission_performed") is False
        and bool(cases)
        and passed == len(cases)
    )

    index_path = output_root / "inbox-handoff-index.json"
    report_path = output_root / "inbox-handoff-index.md"
    manifest_path = output_root / "artifact-hashes.json"
    index = {
        "ok": ok,
        "index_id": index_id,
        "index_type": "inbox_handoff_index_ai_self_filing_no_external_lawyer",
        "created_at": build_case_queue.utc_plus_8_now(),
        "source_inbox_dir": display_path(source_root, output_root),
        "inbox_id": source_result.get("inbox_id"),
        "status": "approved_for_adapter_execution" if ok else "inbox_handoff_index_blocked",
        "decision": "handoff_index_ready_no_auto_submit" if ok else "cure_inbox_handoff_index_errors",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "source_artifacts": {
            "inbox_to_handoff_result": artifact_ref(result_path, output_root),
            "case_queue": artifact_ref(queue_path, output_root),
            "batch_processor_result": artifact_ref(batch_path, output_root),
            "source_artifact_hashes": artifact_ref(source_manifest_path, output_root),
        },
        "summary": {
            "total": len(cases),
            "passed": passed,
            "blocked": len(cases) - passed,
            "reference_delta_cases": reference_delta_cases,
        },
        "cases": cases,
        "next_action": "Use each indexed handoff package only as approved-adapter execution input evidence; adapter execution, receipt capture, and application-number evidence remain separate gates.",
        "artifacts": {
            "inbox_handoff_index": str(index_path),
            "inbox_handoff_index_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
    }
    write_json(index_path, index)
    report_path.write_text(render_report(index), encoding="utf-8")
    write_json(manifest_path, build_manifest(output_root, index_id, [index_path, report_path]))
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)
    return {
        "ok": ok and manifest_ok,
        "index_id": index_id,
        "output_dir": str(output_root),
        "artifacts": index["artifacts"],
        "summary": index["summary"],
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "external_lawyer_involved": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_inbox_dir", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--index-id", default="INBOX-HANDOFF-INDEX-001")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response = run(args.source_inbox_dir, args.output_dir, args.index_id)
    except Exception as exc:
        response = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
            "adapter_execution_performed": False,
            "automatic_submission_performed": False,
            "external_lawyer_involved": False,
        }
    if args.json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print("PASS" if response.get("ok") else "FAIL")
        print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0 if response.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
