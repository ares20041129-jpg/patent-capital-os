#!/usr/bin/env python3
"""Validate that a Patent Capital OS benchmark preserves filing gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing_file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid_json: {path}: {exc}") from exc


def contains(path: Path, needles: list[str]) -> list[str]:
    if not path.exists():
        return [f"missing_file: {path}"]
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return [
        f"missing_text: {path.name}: {needle}"
        for needle in needles
        if needle.lower() not in text
    ]


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    status_path = benchmark_dir / "submission-packet-status.json"
    report_path = benchmark_dir / "report.md"
    assessment_path = benchmark_dir / "darwin-assessment.md"
    claim_map_path = benchmark_dir / "claim-support-map.md"
    red_team_path = benchmark_dir / "red-team-independent.md"
    results_path = benchmark_dir / "results.tsv"
    prompt_runs_path = benchmark_dir / "prompt-runs" / "baseline-vs-skill.jsonl"
    source_captures_path = benchmark_dir / "prior-art" / "source-captures.jsonl"
    artifact_hashes_path = benchmark_dir / "artifact-hashes.json"

    try:
        status = load_json(status_path)
    except RuntimeError as exc:
        return False, [str(exc)], warnings

    legal_gate = str(status.get("legal_gate", "")).lower()
    decision = str(status.get("decision", "")).lower()
    case_status = str(status.get("status", "")).lower()

    if legal_gate not in {"failed", "blocked"}:
        errors.append("legal_gate_must_be_failed_or_blocked_for_draft_benchmark")

    if decision != "do_not_file":
        errors.append("decision_must_be_do_not_file_for_draft_benchmark")

    if "draft" not in case_status and "not_filing_ready" not in case_status:
        warnings.append("status_should_make_draft_or_not_filing_ready_state_explicit")

    errors.extend(contains(report_path, ["legal_gate_failed", "draft-only benchmark"]))
    errors.extend(contains(assessment_path, ["fail as an auto-filing workflow", "do_not_file"]))
    errors.extend(contains(claim_map_path, ["Decision: revise", "draft benchmark only"]))
    errors.extend(contains(red_team_path, ["do_not_file", "not a filing-ready patent application"]))

    for path in [results_path, prompt_runs_path, source_captures_path, artifact_hashes_path]:
        if not path.exists():
            errors.append(f"missing_file: {path}")

    if source_captures_path.exists():
        rows = [line for line in source_captures_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(rows) < 13:
            errors.append("source_captures_must_include_13_rows")

    if prompt_runs_path.exists():
        rows = [line for line in prompt_runs_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(rows) < 5:
            warnings.append("prompt_runs_should_cover_at_least_5_test_prompts")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_dir", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
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
