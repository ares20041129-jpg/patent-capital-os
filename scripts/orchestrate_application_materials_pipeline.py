#!/usr/bin/env python3
"""Orchestrate application materials generation plus quality review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import prepare_application_materials_quality_review
import prepare_patent_application_materials
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


def render_report(result: dict[str, Any], manifest: dict[str, Any]) -> str:
    stages = result.get("stages") if isinstance(result.get("stages"), dict) else {}
    materials = stages.get("application_materials") if isinstance(stages.get("application_materials"), dict) else {}
    quality = stages.get("quality_gate") if isinstance(stages.get("quality_gate"), dict) else {}
    lines = [
        "# Application Materials Pipeline Report",
        "",
        f"Case ID: {result.get('case_id')}",
        f"Pipeline status: {'pass' if result.get('ok') else 'fail'}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        "Official system touched: no",
        "Official submission performed: no",
        "External lawyer involved: no",
        "",
        "## Stages",
        "",
        "| Stage | Status | Output |",
        "| --- | --- | --- |",
        f"| Application materials | {'pass' if materials.get('ok') else 'fail'} | {materials.get('output_dir')} |",
        f"| Quality gate | {'pass' if quality.get('ok') else 'fail'} | {quality.get('output_dir')} |",
        "",
        "## Next Action",
        "",
        "- Run official-channel preflight only after this pipeline remains green; do not upload, sign, pay, submit, or claim receipt from this pipeline alone.",
        "",
        "## Boundary",
        "",
        "This pipeline generates and reviews local application materials only. It does not log in, touch an official system, upload, sign, pay, submit, capture a real receipt, or create an application number.",
        "",
        "## Generated Artifacts",
        "",
    ]
    for item in manifest.get("files", []):
        lines.append(f"- {item.get('path')}: {item.get('sha256')}")
    return "\n".join(lines) + "\n"


def orchestrate(
    package_dir: Path,
    draft_package_dir: Path,
    provenance_dir: Path,
    output_dir: Path,
) -> tuple[dict[str, Any], int]:
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    materials_dir = output_root / "application-materials"
    quality_dir = output_root / "application-materials-quality-gate"
    result_path = output_root / "application-materials-pipeline-result.json"
    report_path = output_root / "application-materials-pipeline-report.md"
    manifest_path = output_root / "artifact-hashes.json"

    materials_response, materials_exit = prepare_patent_application_materials.prepare(
        package_dir=package_dir,
        draft_package_dir=draft_package_dir,
        provenance_dir=provenance_dir,
        output_dir=materials_dir,
    )

    quality_response: dict[str, Any] = {
        "ok": False,
        "skipped": True,
        "reason": "application_materials_stage_failed",
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }
    quality_exit = 1
    if materials_exit == 0 and materials_response.get("ok") is True:
        quality_response, quality_exit = prepare_application_materials_quality_review.prepare(
            materials_dir=materials_dir,
            output_dir=quality_dir,
        )

    case_id = str(materials_response.get("case_id") or quality_response.get("case_id") or "")
    ok = (
        materials_exit == 0
        and quality_exit == 0
        and materials_response.get("official_system_touched") is False
        and materials_response.get("official_submission_performed") is False
        and quality_response.get("official_system_touched") is False
        and quality_response.get("official_submission_performed") is False
        and quality_response.get("external_lawyer_involved") is False
    )
    result = {
        "ok": ok,
        "case_id": case_id,
        "pipeline_type": "application_materials_to_quality_gate",
        "created_at": build_case_queue.utc_plus_8_now(),
        "status": "package_valid_official_preflight_pending",
        "decision": "official_channel_preflight_required" if ok else "pipeline_blocked",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "stages": {
            "application_materials": {
                "ok": materials_response.get("ok") is True,
                "output_dir": str(materials_dir),
                "artifacts": materials_response.get("artifacts", {}),
                "errors": materials_response.get("materials_errors", []) + materials_response.get("hash_errors", []),
                "warnings": materials_response.get("materials_warnings", []) + materials_response.get("hash_warnings", []),
            },
            "quality_gate": {
                "ok": quality_response.get("ok") is True,
                "output_dir": str(quality_dir),
                "artifacts": quality_response.get("artifacts", {}),
                "errors": quality_response.get("review_errors", []) + quality_response.get("hash_errors", []),
                "warnings": quality_response.get("review_warnings", []) + quality_response.get("hash_warnings", []),
            },
        },
        "next_action": "Run official-channel preflight; do not file from pipeline output alone." if ok else "Cure pipeline errors before official-channel preflight.",
    }
    write_json(result_path, result)

    stage_files = [
        materials_dir / "application-materials.json",
        materials_dir / "artifact-hashes.json",
        quality_dir / "application-materials-quality-review.json",
        quality_dir / "artifact-hashes.json",
    ]
    existing_stage_files = [path for path in stage_files if path.exists()]
    provisional_manifest = build_manifest(output_root, case_id, existing_stage_files + [result_path])
    report_path.write_text(render_report(result, provisional_manifest), encoding="utf-8")
    final_manifest = build_manifest(output_root, case_id, existing_stage_files + [report_path])
    write_json(manifest_path, final_manifest)
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    result["artifact_hashes"] = str(manifest_path)
    result["manifest_errors"] = manifest_errors
    result["manifest_warnings"] = manifest_warnings
    write_json(result_path, result)

    final_manifest = build_manifest(output_root, case_id, existing_stage_files + [result_path, report_path])
    write_json(manifest_path, final_manifest)
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    response = {
        "ok": ok and manifest_ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "application_materials_dir": str(materials_dir),
            "quality_gate_dir": str(quality_dir),
            "pipeline_result": str(result_path),
            "pipeline_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }
    return response, 0 if response["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--draft-package-dir", required=True, type=Path)
    parser.add_argument("--provenance-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = orchestrate(
            package_dir=args.package_dir,
            draft_package_dir=args.draft_package_dir,
            provenance_dir=args.provenance_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
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
