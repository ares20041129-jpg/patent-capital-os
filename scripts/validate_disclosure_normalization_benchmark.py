#!/usr/bin/env python3
"""Validate disclosure normalization scaffold benchmark artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import validate_artifact_hash_manifest
import validate_invention_disclosure_scaffold

PROHIBITED_DEFAULT_REVIEW_TERMS = re.compile(r"\b(attorney|lawyer|counsel)\b|patent-agent|patent agent", re.IGNORECASE)


def require_no_default_review_terms(path: Path, label: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if PROHIBITED_DEFAULT_REVIEW_TERMS.search(line):
            errors.append(f"{label}_must_not_default_to_lawyer_or_patent_agent_terms: line={line_number}")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    scaffold_path = benchmark_dir / "invention-disclosure-scaffold.json"
    report_path = benchmark_dir / "normalization-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if scaffold_path.exists():
        scaffold = json.loads(scaffold_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_invention_disclosure_scaffold.validate(scaffold)
        if not ok:
            errors.extend([f"invention_disclosure_scaffold: {item}" for item in errs])
        warnings.extend([f"invention_disclosure_scaffold: {item}" for item in warns])
        require_no_default_review_terms(scaffold_path, "invention_disclosure_scaffold", errors)

        controls = scaffold.get("scaffold_controls")
        if not isinstance(controls, dict):
            errors.append("scaffold_controls_missing")
        else:
            if controls.get("filing_allowed") is not False:
                errors.append("scaffold_must_not_allow_filing")
            if controls.get("draft_generation_allowed") is not False:
                errors.append("scaffold_must_not_allow_draft_generation")
            if controls.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
                errors.append("scaffold_controls_must_preserve_ai_self_filing_legal_gate_mode")
            if controls.get("external_lawyer_involved") is not False:
                errors.append("scaffold_controls_external_lawyer_involved_must_be_false")
            if controls.get("inventor_confirmation_pending") is not True:
                errors.append("inventor_confirmation_must_remain_pending")
            if controls.get("legal_gate_pending") is not True:
                errors.append("legal_gate_must_remain_pending")
            if controls.get("no_copying_confirmation_pending") is not True:
                errors.append("no_copying_confirmation_must_remain_pending")
    else:
        errors.append(f"missing_file: {scaffold_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "invention disclosure normalization report",
            "disclosure status: scaffold_pending_confirmation",
            "filing allowed: no",
            "draft generation allowed: no",
            "pending confirmations",
            "ai legal/compliance gate confirmation",
        ]:
            if needle not in text:
                errors.append(f"normalization_report_missing_text: {needle}")
        require_no_default_review_terms(report_path, "normalization_report", errors)
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
