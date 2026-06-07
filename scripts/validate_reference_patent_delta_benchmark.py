#!/usr/bin/env python3
"""Validate the reference-patent delta benchmark."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_reference_patent_delta


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_failure(label: str, data: dict[str, Any], expected_error: str, base_dir: Path, errors: list[str]) -> None:
    ok, case_errors, _ = validate_reference_patent_delta.validate(data, base_dir)
    if ok:
        errors.append(f"{label}: mutation_unexpectedly_passed")
    if not any(expected_error in item for item in case_errors):
        errors.append(f"{label}: expected_error_not_found: {expected_error}")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    delta_path = benchmark_dir / "reference-patent-delta.json"
    strategy_path = benchmark_dir / "claim-strategy.md"
    report_path = benchmark_dir / "reference-patent-delta-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if delta_path.exists():
        delta = load_json(delta_path)
        ok, errs, warns = validate_reference_patent_delta.validate(delta, benchmark_dir)
        if not ok:
            errors.extend([f"reference_patent_delta: {item}" for item in errs])
        warnings.extend([f"reference_patent_delta: {item}" for item in warns])

        refs = delta.get("reference_patents") if isinstance(delta.get("reference_patents"), list) else []
        if len(refs) != 13:
            errors.append("benchmark_reference_patents_must_include_13_items")

        missing_row = copy.deepcopy(delta)
        missing_row["delta_rows"] = missing_row.get("delta_rows", [])[:-1]
        require_failure(
            "missing_delta_row_rejected",
            missing_row,
            "missing_delta_row_for_claim_element",
            benchmark_dir,
            errors,
        )

        reference_support = copy.deepcopy(delta)
        reference_support.setdefault("claim_elements", [])[0]["support_path"] = "reference-patents/CN120827118A.txt"
        require_failure(
            "reference_material_as_support_rejected",
            reference_support,
            "support_must_not_be_reference_material",
            benchmark_dir,
            errors,
        )

        novelty_claim = copy.deepcopy(delta)
        novelty_claim.setdefault("controls", {})["novelty_guarantee_claimed"] = True
        require_failure(
            "novelty_guarantee_rejected",
            novelty_claim,
            "control_novelty_guarantee_claimed_must_be_false",
            benchmark_dir,
            errors,
        )

        bad_source_hash = copy.deepcopy(delta)
        bad_source_hash.setdefault("source_input", {})["hash"] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        require_failure(
            "source_hash_mismatch_rejected",
            bad_source_hash,
            "source_input_hash_mismatch",
            benchmark_dir,
            errors,
        )
    else:
        errors.append(f"missing_file: {delta_path}")

    for path, needles in [
        (
            strategy_path,
            [
                "reference patent delta claim strategy",
                "reference patents are boundary evidence only",
                "novelty guarantee claimed: no",
            ],
        ),
        (
            report_path,
            [
                "reference patent delta report",
                "reference patents: 13",
                "does not claim novelty",
                "official system touched: no",
            ],
        ),
    ]:
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            for needle in needles:
                if needle not in text:
                    errors.append(f"{path.name}_missing_text: {needle}")
        else:
            errors.append(f"missing_file: {path}")

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
