#!/usr/bin/env python3
"""Prepare a reference-patent delta and claim strategy package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_reference_patent_delta


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def render_strategy(delta: dict[str, Any]) -> str:
    lines = [
        "# Reference Patent Delta Claim Strategy",
        "",
        f"Case ID: {delta.get('case_id')}",
        f"Status: {delta.get('status')}",
        "Official system touched: no",
        "Official submission performed: no",
        "External lawyer involved: no",
        "Novelty guarantee claimed: no",
        "",
        "## Inventive Concept",
        "",
        str(delta.get("inventive_concept") or "Inventive concept pending."),
        "",
        "## Claim Strategy",
        "",
        "| Element | Distinguishing Feature | Technical Effect Evidence | Strategy | Fallback |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in delta.get("delta_rows", []):
        if isinstance(row, dict):
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row.get("element_id") or ""),
                        str(row.get("applicant_distinguishing_feature") or ""),
                        str(row.get("technical_effect_evidence") or ""),
                        str(row.get("claim_strategy") or ""),
                        str(row.get("fallback_position") or ""),
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Reference patents are boundary evidence only. They do not provide applicant claim support, legal advice, patentability guarantees, or filing authorization.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_report(delta: dict[str, Any]) -> str:
    refs = delta.get("reference_patents") if isinstance(delta.get("reference_patents"), list) else []
    rows = delta.get("delta_rows") if isinstance(delta.get("delta_rows"), list) else []
    return "\n".join(
        [
            "# Reference Patent Delta Report",
            "",
            f"Case ID: {delta.get('case_id')}",
            f"Reference patents: {len(refs)}",
            f"Delta rows: {len(rows)}",
            "Legal gate mode: ai_self_filing_no_external_lawyer",
            "Official system touched: no",
            "Official submission performed: no",
            "External lawyer involved: no",
            "Novelty guarantee claimed: no",
            "",
            "This report converts cited patents into prior-art boundaries and claim-strategy deltas. It does not claim novelty, inventiveness, allowance, lawyer review, patent-agent review, official filing, receipt, or application number.",
            "",
        ]
    )


def artifact_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [
            {"path": rel(path, output_dir), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in files
        ],
    }


def prepare(source_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    source = load_json(source_path.resolve())
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    delta_path = output_root / "reference-patent-delta.json"
    strategy_path = output_root / "claim-strategy.md"
    report_path = output_root / "reference-patent-delta-report.md"
    hashes_path = output_root / "artifact-hashes.json"

    delta = {
        "case_id": source.get("case_id"),
        "created_at": build_case_queue.utc_plus_8_now(),
        "delta_type": "reference_patent_delta_claim_strategy",
        "status": "reference_delta_ready_for_draft_strategy",
        "decision": "use_references_as_boundary_not_claim_support",
        "source_input": {
            "path": rel(source_path.resolve(), output_root),
            "hash": sha256_file(source_path.resolve()),
        },
        "invention_title": source.get("invention_title"),
        "inventive_concept": source.get("inventive_concept"),
        "reference_patents": source.get("reference_patents") or [],
        "claim_elements": source.get("claim_elements") or [],
        "delta_rows": source.get("delta_rows") or [],
        "controls": {
            "reference_patents_used_as_boundary_only": True,
            "reference_patents_used_as_applicant_claim_support": False,
            "novelty_guarantee_claimed": False,
            "patentability_guarantee_claimed": False,
            "legal_advice_claimed": False,
            "lawyer_or_agent_review_claimed": False,
            "filing_authorized": False,
        },
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
        "next_action": "Use this delta to draft or revise claims from applicant evidence; do not file from reference-patent similarity alone.",
    }
    write_json(delta_path, delta)
    strategy_path.write_text(render_strategy(delta), encoding="utf-8")
    report_path.write_text(render_report(delta), encoding="utf-8")
    write_json(hashes_path, artifact_manifest(output_root, str(delta.get("case_id") or ""), [delta_path, strategy_path, report_path]))

    delta_ok, delta_errors, delta_warnings = validate_reference_patent_delta.validate(delta, output_root)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
    ok = delta_ok and hash_ok
    return {
        "ok": ok,
        "case_id": delta.get("case_id"),
        "output_dir": str(output_root),
        "artifacts": {
            "reference_patent_delta": str(delta_path),
            "claim_strategy": str(strategy_path),
            "reference_patent_delta_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "delta_errors": delta_errors,
        "delta_warnings": delta_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        response, exit_code = prepare(args.source, args.output_dir)
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
