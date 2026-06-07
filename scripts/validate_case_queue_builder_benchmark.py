#!/usr/bin/env python3
"""Validate case queue builder benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_artifact_hash_manifest
import validate_case_queue


def require_queue_legal_gate_metadata(queue: dict, errors: list[str]) -> None:
    items = queue.get("items")
    if not isinstance(items, list):
        return
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        mode = item.get("legal_gate_mode")
        if not mode:
            errors.append(f"item_{index}_missing_legal_gate_mode")
        if item.get("external_lawyer_involved") is not False:
            errors.append(f"item_{index}_external_lawyer_involved_must_be_false")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    queue_path = benchmark_dir / "generated-case-queue.json"
    report_path = benchmark_dir / "builder-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if queue_path.exists():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_case_queue.validate(queue)
        if not ok:
            errors.extend([f"generated_queue: {item}" for item in errs])
        warnings.extend([f"generated_queue: {item}" for item in warns])
        require_queue_legal_gate_metadata(queue, errors)
    else:
        errors.append(f"missing_file: {queue_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "builder mode: dry_run",
            "official system touched: no",
            "official submission allowed: no",
            "external professional involved: no",
            "legal gate metadata: present",
            "generated-case-queue.json",
        ]:
            if needle not in text:
                errors.append(f"builder_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        warnings.append("artifact_hashes_missing_until_manifest_generated")

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
