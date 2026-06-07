#!/usr/bin/env python3
"""Validate application materials pipeline benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_application_materials_quality_benchmark
import validate_artifact_hash_manifest
import validate_patent_application_materials_benchmark


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    materials_dir = benchmark_dir / "application-materials"
    quality_dir = benchmark_dir / "application-materials-quality-gate"
    result_path = benchmark_dir / "application-materials-pipeline-result.json"
    report_path = benchmark_dir / "application-materials-pipeline-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if materials_dir.exists():
        ok, errs, warns = validate_patent_application_materials_benchmark.validate(materials_dir)
        if not ok:
            errors.extend([f"application_materials: {item}" for item in errs])
        warnings.extend([f"application_materials: {item}" for item in warns])
    else:
        errors.append(f"missing_dir: {materials_dir}")

    if quality_dir.exists():
        ok, errs, warns = validate_application_materials_quality_benchmark.validate(quality_dir)
        if not ok:
            errors.extend([f"quality_gate: {item}" for item in errs])
        warnings.extend([f"quality_gate: {item}" for item in warns])
    else:
        errors.append(f"missing_dir: {quality_dir}")

    if result_path.exists():
        result = load_json(result_path)
        if result.get("ok") is not True:
            errors.append("pipeline_result_ok_must_be_true")
        if result.get("pipeline_type") != "application_materials_to_quality_gate":
            errors.append("pipeline_type_invalid")
        if result.get("status") != "package_valid_official_preflight_pending":
            errors.append("pipeline_status_must_stay_preflight_pending")
        if result.get("decision") != "official_channel_preflight_required":
            errors.append("pipeline_decision_must_require_official_preflight")
        if result.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("pipeline_legal_gate_mode_invalid")
        for field in ["official_system_touched", "official_submission_performed", "external_lawyer_involved"]:
            if result.get(field) is not False:
                errors.append(f"pipeline_result_{field}_must_be_false")
        stages = result.get("stages") if isinstance(result.get("stages"), dict) else {}
        for stage_name in ["application_materials", "quality_gate"]:
            stage = stages.get(stage_name) if isinstance(stages.get(stage_name), dict) else {}
            if stage.get("ok") is not True:
                errors.append(f"pipeline_stage_must_pass: {stage_name}")
            if not stage.get("artifacts"):
                errors.append(f"pipeline_stage_artifacts_missing: {stage_name}")
    else:
        errors.append(f"missing_file: {result_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "application materials pipeline report",
            "pipeline status: pass",
            "application materials",
            "quality gate",
            "official system touched: no",
            "official submission performed: no",
            "external lawyer involved: no",
            "official-channel preflight",
        ]:
            if needle not in text:
                errors.append(f"pipeline_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {hashes_path}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.benchmark_dir)
    result = {"ok": ok, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if ok else "FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
