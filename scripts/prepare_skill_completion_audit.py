#!/usr/bin/env python3
"""Prepare a local skill-completion audit for Patent Capital OS."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest


AUDIT_ITEMS = [
    {
        "id": "reference_patent_delta",
        "label": "Reference patent delta",
        "evidence_paths": ["benchmarks/reference-patent-delta"],
        "validator": "validate_reference_patent_delta_benchmark",
        "target": "benchmarks/reference-patent-delta",
    },
    {
        "id": "application_materials_generation",
        "label": "Application materials generation",
        "evidence_paths": ["benchmarks/application-materials-pipeline"],
        "validator": "validate_application_materials_pipeline_benchmark",
        "target": "benchmarks/application-materials-pipeline",
    },
    {
        "id": "ai_legal_gate_no_external_lawyer",
        "label": "AI legal gate without external lawyer",
        "evidence_paths": ["benchmarks/ai-self-filing-package-validation"],
        "validator": "validate_ai_self_filing_package_benchmark",
        "target": "benchmarks/ai-self-filing-package-validation",
    },
    {
        "id": "batch_inbox_to_handoff",
        "label": "Batch inbox to handoff",
        "evidence_paths": ["benchmarks/inbox-to-handoff"],
        "validator": "validate_inbox_to_handoff_benchmark",
        "target": "benchmarks/inbox-to-handoff",
    },
    {
        "id": "unsafe_inbox_rejection",
        "label": "Unsafe inbox rejection",
        "evidence_paths": ["benchmarks/inbox-to-handoff-rejection"],
        "validator": "validate_inbox_to_handoff_rejection_benchmark",
        "target": "benchmarks/inbox-to-handoff-rejection",
    },
    {
        "id": "read_only_handoff",
        "label": "Read-only handoff",
        "evidence_paths": ["benchmarks/pre-submission-to-handoff-reference-delta"],
        "validator": "validate_pre_submission_to_handoff_benchmark",
        "target": "benchmarks/pre-submission-to-handoff-reference-delta",
    },
    {
        "id": "handoff_index",
        "label": "Final handoff index",
        "evidence_paths": ["benchmarks/inbox-handoff-index"],
        "validator": "validate_inbox_handoff_index_benchmark",
        "target": "benchmarks/inbox-handoff-index",
    },
    {
        "id": "hash_binding_and_regression_gate",
        "label": "Hash binding and regression gate",
        "evidence_paths": ["scripts/run_regression_gate.py", "references/regression-gate.md"],
        "validator": "",
        "target": "",
    },
    {
        "id": "production_runbook",
        "label": "Production intake runbook",
        "evidence_paths": ["references/production-intake-runbook.md"],
        "validator": "",
        "target": "",
    },
    {
        "id": "official_boundary",
        "label": "Official filing boundary",
        "evidence_paths": ["references/filing-execution-boundary.md", "references/production-architecture.md"],
        "validator": "",
        "target": "",
    },
]


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def evidence_ref(skill_root: Path, rel_path: str) -> dict[str, Any]:
    path = (skill_root / rel_path).resolve()
    ref: dict[str, Any] = {"path": rel_path, "exists": path.exists()}
    if path.is_file():
        ref["sha256"] = sha256_file(path)
    return ref


def run_validator(skill_root: Path, validator_name: str, target: str) -> dict[str, Any]:
    if not validator_name:
        return {"ok": True, "validator": "", "target": target, "errors": [], "warnings": []}
    module = importlib.import_module(validator_name)
    ok, errors, warnings = module.validate((skill_root / target).resolve())
    return {
        "ok": ok,
        "validator": validator_name,
        "target": target,
        "errors": errors,
        "warnings": warnings,
    }


def build_audit_item(skill_root: Path, item: dict[str, str]) -> dict[str, Any]:
    evidence = [evidence_ref(skill_root, path) for path in item["evidence_paths"]]
    missing = [ref["path"] for ref in evidence if ref.get("exists") is not True]
    validation = run_validator(skill_root, item["validator"], item["target"])
    passed = not missing and validation.get("ok") is True
    return {
        "id": item["id"],
        "label": item["label"],
        "status": "passed" if passed else "blocked",
        "evidence": evidence,
        "validation": validation,
        "errors": [f"missing_evidence_path: {path}" for path in missing] + [str(value) for value in validation.get("errors", [])],
        "warnings": [str(value) for value in validation.get("warnings", [])],
    }


def render_report(audit: dict[str, Any]) -> str:
    lines = [
        "# Patent Capital OS Skill Completion Audit",
        "",
        f"Audit status: {'pass' if audit.get('ok') else 'fail'}",
        f"Decision: {audit.get('decision')}",
        "Route: AI self-filing, no external lawyer or patent agent in default path",
        "Official system touched: no",
        "Official submission performed: no",
        "Adapter execution performed: no",
        "Automatic submission performed: no",
        "External lawyer involved: no",
        "",
        "## Audit Items",
        "",
        "| Item | Status | Validator |",
        "| --- | --- | --- |",
    ]
    for item in audit.get("audit_items", []):
        if not isinstance(item, dict):
            continue
        validation = item.get("validation") if isinstance(item.get("validation"), dict) else {}
        lines.append(f"| {item.get('label')} | {item.get('status')} | {validation.get('validator') or 'path evidence'} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit closes the local skill loop only. It does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.",
            "",
            "## Next Action",
            "",
            str(audit.get("next_action") or ""),
        ]
    )
    return "\n".join(lines) + "\n"


def run(skill_root: Path, output_dir: Path, audit_id: str) -> dict[str, Any]:
    root = skill_root.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    audit_items = [build_audit_item(root, item) for item in AUDIT_ITEMS]
    passed = sum(1 for item in audit_items if item.get("status") == "passed")
    ok = passed == len(audit_items)
    audit_path = output_root / "skill-completion-audit.json"
    report_path = output_root / "skill-completion-audit.md"
    manifest_path = output_root / "artifact-hashes.json"
    audit = {
        "ok": ok,
        "audit_id": audit_id,
        "audit_type": "patent_capital_os_skill_completion_audit",
        "created_at": build_case_queue.utc_plus_8_now(),
        "status": "approved_for_adapter_execution" if ok else "skill_completion_blocked",
        "decision": "skill_closed_loop_ready_no_auto_submit" if ok else "cure_skill_completion_errors",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "completion_scope": {
            "included": [
                "received material intake",
                "reference patent delta",
                "application materials generation",
                "AI legal and compliance gate",
                "batch inbox processing",
                "unsafe input rejection",
                "read-only handoff",
                "handoff index",
                "runbook",
                "local regression gate contract",
            ],
            "excluded": [
                "API server",
                "dashboard",
                "database",
                "watcher service",
                "real official submission",
                "official login",
                "signature",
                "payment",
                "receipt capture",
                "application number claim",
            ],
        },
        "summary": {"total": len(audit_items), "passed": passed, "blocked": len(audit_items) - passed},
        "audit_items": audit_items,
        "next_action": "Run the local regression gate after this audit and keep automatic submission, adapter execution, receipt capture, and application-number evidence as separate future gates.",
        "artifacts": {
            "skill_completion_audit": str(audit_path),
            "skill_completion_audit_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
    }
    write_json(audit_path, audit)
    report_path.write_text(render_report(audit), encoding="utf-8")
    write_json(manifest_path, build_manifest(output_root, audit_id, [audit_path, report_path]))
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)
    return {
        "ok": ok and manifest_ok,
        "audit_id": audit_id,
        "output_dir": str(output_root),
        "artifacts": audit["artifacts"],
        "summary": audit["summary"],
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
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--audit-id", default="PATENT-CAPITAL-OS-SKILL-CLOSURE-001")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response = run(args.skill_root, args.output_dir, args.audit_id)
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
