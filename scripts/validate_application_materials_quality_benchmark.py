#!/usr/bin/env python3
"""Validate application materials quality gate benchmark."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import validate_application_materials_quality_review
import validate_artifact_hash_manifest


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_failure(label: str, data: dict[str, Any], expected_error: str, base_dir: Path, errors: list[str]) -> None:
    ok, case_errors, _ = validate_application_materials_quality_review.validate(data, base_dir)
    if ok:
        errors.append(f"{label}: mutation_unexpectedly_passed")
    if not any(expected_error in item for item in case_errors):
        errors.append(f"{label}: expected_error_not_found: {expected_error}")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    review_path = benchmark_dir / "application-materials-quality-review.json"
    report_path = benchmark_dir / "application-materials-quality-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if review_path.exists():
        review = load_json(review_path)
        ok, errs, warns = validate_application_materials_quality_review.validate(review, benchmark_dir)
        if not ok:
            errors.extend([f"quality_review: {item}" for item in errs])
        warnings.extend([f"quality_review: {item}" for item in warns])

        gate = review.get("quality_gate") if isinstance(review.get("quality_gate"), dict) else {}
        if gate.get("weighted_score", 0) < 90:
            errors.append("quality_review_must_be_enterprise_ready_score")
        if gate.get("enterprise_ready") is not True:
            errors.append("quality_review_enterprise_ready_must_be_true")

        bad_hash = copy.deepcopy(review)
        bad_hash.setdefault("application_materials", {})["hash"] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        require_failure("application_materials_hash_mismatch_rejected", bad_hash, "application_materials_hash_mismatch", benchmark_dir, errors)

        low_score = copy.deepcopy(review)
        low_score.setdefault("dimensions", {}).setdefault("claim_architecture", {})["score"] = 5
        low_score["dimensions"]["claim_architecture"]["passed"] = False
        require_failure(
            "low_claim_architecture_score_rejected",
            low_score,
            "quality_dimension_score_below_minimum: claim_architecture",
            benchmark_dir,
            errors,
        )

        missing_check = copy.deepcopy(review)
        missing_check.setdefault("dimensions", {}).setdefault("evidence_binding", {})["checks"] = (
            missing_check["dimensions"]["evidence_binding"].get("checks") or []
        )[:-1]
        require_failure(
            "missing_quality_check_id_rejected",
            missing_check,
            "quality_dimension_check_ids_mismatch: evidence_binding",
            benchmark_dir,
            errors,
        )

        forged_score = copy.deepcopy(review)
        forged_score.setdefault("dimensions", {}).setdefault("auditability", {}).setdefault("checks", [])[0]["passed"] = False
        require_failure(
            "forged_dimension_score_rejected",
            forged_score,
            "quality_dimension_has_failed_check: auditability",
            benchmark_dir,
            errors,
        )
        require_failure(
            "forged_dimension_score_recalculation_rejected",
            forged_score,
            "quality_dimension_score_mismatch: auditability",
            benchmark_dir,
            errors,
        )

        failed_gate = copy.deepcopy(review)
        failed_gate.setdefault("quality_gate", {})["status"] = "failed"
        failed_gate["quality_gate"]["official_preflight_allowed"] = False
        require_failure("failed_quality_gate_rejected", failed_gate, "quality_gate_status_must_be_passed", benchmark_dir, errors)
    else:
        errors.append(f"missing_file: {review_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "application materials quality review",
            "gate status: passed",
            "weighted score",
            "official system touched: no",
            "official submission performed: no",
            "external lawyer involved: no",
            "not provide legal advice",
        ]:
            if needle not in text:
                errors.append(f"quality_report_missing_text: {needle}")
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
