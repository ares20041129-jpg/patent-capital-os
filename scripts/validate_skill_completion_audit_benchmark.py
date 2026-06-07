#!/usr/bin/env python3
"""Validate the Patent Capital OS skill completion audit benchmark."""

from __future__ import annotations

import argparse
import importlib
import json
import re
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED_ITEM_IDS = {
    "reference_patent_delta",
    "application_materials_generation",
    "ai_legal_gate_no_external_lawyer",
    "batch_inbox_to_handoff",
    "unsafe_inbox_rejection",
    "read_only_handoff",
    "handoff_index",
    "hash_binding_and_regression_gate",
    "production_runbook",
    "official_boundary",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def skill_root_for(benchmark_dir: Path) -> Path:
    return benchmark_dir.resolve().parents[1]


def validate_item_against_local_evidence(item: dict[str, Any], skill_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    item_id = str(item.get("id") or "")
    if item.get("status") != "passed":
        errors.append(f"audit_item_status_must_pass: {item_id}")

    evidence = item.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"audit_item_evidence_missing: {item_id}")
    else:
        for index, ref in enumerate(evidence, start=1):
            if not isinstance(ref, dict):
                errors.append(f"audit_item_{item_id}_evidence_{index}_must_be_object")
                continue
            rel_path = ref.get("path")
            if not isinstance(rel_path, str) or not rel_path:
                errors.append(f"audit_item_{item_id}_evidence_{index}_path_missing")
                continue
            path = (skill_root / rel_path).resolve()
            try:
                path.relative_to(skill_root.resolve())
            except ValueError:
                errors.append(f"audit_item_{item_id}_evidence_{index}_outside_skill_root")
                continue
            if not path.exists():
                errors.append(f"audit_item_{item_id}_evidence_{index}_missing_on_disk")
            if path.is_file():
                if not isinstance(ref.get("sha256"), str) or not SHA256_RE.fullmatch(str(ref.get("sha256"))):
                    errors.append(f"audit_item_{item_id}_evidence_{index}_hash_invalid")

    validation = item.get("validation") if isinstance(item.get("validation"), dict) else {}
    validator_name = str(validation.get("validator") or "")
    target = str(validation.get("target") or "")
    if validator_name:
        try:
            module = importlib.import_module(validator_name)
            ok, errs, warns = module.validate((skill_root / target).resolve())
        except Exception as exc:
            ok, errs, warns = False, [str(exc)], []
        if not ok:
            errors.extend([f"audit_item_{item_id}_{validator_name}: {err}" for err in errs])
        warnings.extend([f"audit_item_{item_id}_{validator_name}: {warn}" for warn in warns])
        if validation.get("ok") is not True:
            errors.append(f"embedded_validation_must_pass: {item_id}")
        if validation.get("validator") != validator_name:
            errors.append(f"embedded_validation_name_mismatch: {item_id}")
    return errors, warnings


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    audit_path = benchmark_dir / "skill-completion-audit.json"
    report_path = benchmark_dir / "skill-completion-audit.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    if not audit_path.exists():
        return False, [f"missing_file: {audit_path}"], warnings

    audit = load_json(audit_path)
    if audit.get("ok") is not True:
        errors.append("skill_completion_audit_ok_must_be_true")
    if audit.get("audit_type") != "patent_capital_os_skill_completion_audit":
        errors.append("skill_completion_audit_type_invalid")
    if audit.get("status") != "approved_for_adapter_execution":
        errors.append("skill_completion_audit_status_must_remain_approved_for_adapter_execution")
    if audit.get("decision") != "skill_closed_loop_ready_no_auto_submit":
        errors.append("skill_completion_audit_decision_invalid")
    if audit.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("skill_completion_audit_legal_gate_mode_invalid")
    for field in [
        "external_lawyer_involved",
        "official_system_touched",
        "official_submission_performed",
        "adapter_execution_performed",
        "automatic_submission_performed",
    ]:
        if audit.get(field) is not False:
            errors.append(f"skill_completion_audit_{field}_must_be_false")

    scope = audit.get("completion_scope") if isinstance(audit.get("completion_scope"), dict) else {}
    excluded = " ".join(str(item) for item in scope.get("excluded", []))
    for phrase in ["real official submission", "official login", "signature", "payment", "receipt capture", "application number claim"]:
        if phrase not in excluded:
            errors.append(f"completion_scope_missing_exclusion: {phrase}")

    items = audit.get("audit_items") if isinstance(audit.get("audit_items"), list) else []
    ids = {str(item.get("id")) for item in items if isinstance(item, dict)}
    missing_ids = REQUIRED_ITEM_IDS - ids
    for item_id in sorted(missing_ids):
        errors.append(f"missing_audit_item: {item_id}")
    summary = audit.get("summary") if isinstance(audit.get("summary"), dict) else {}
    if summary.get("total") != len(items):
        errors.append("skill_completion_audit_summary_total_mismatch")
    if summary.get("passed") != len(items):
        errors.append("skill_completion_audit_summary_passed_mismatch")
    if summary.get("blocked") != 0:
        errors.append("skill_completion_audit_summary_blocked_must_be_zero")

    root = skill_root_for(benchmark_dir)
    for item in items:
        if not isinstance(item, dict):
            errors.append("audit_item_must_be_object")
            continue
        item_errors, item_warnings = validate_item_against_local_evidence(item, root)
        errors.extend(item_errors)
        warnings.extend(item_warnings)

    next_action = str(audit.get("next_action") or "").lower()
    for needle in ["regression gate", "automatic submission", "adapter execution", "receipt capture", "application-number"]:
        if needle not in next_action:
            errors.append(f"skill_completion_audit_next_action_missing_boundary: {needle}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "patent capital os skill completion audit",
            "audit status: pass",
            "ai self-filing",
            "official system touched: no",
            "official submission performed: no",
            "adapter execution performed: no",
            "automatic submission performed: no",
            "external lawyer involved: no",
            "local skill loop only",
            "does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number",
        ]:
            if needle not in text:
                errors.append(f"skill_completion_audit_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
        manifest = load_json(hashes_path)
        paths = {item.get("path") for item in manifest.get("files", []) if isinstance(item, dict)}
        for required in ["skill-completion-audit.json", "skill-completion-audit.md"]:
            if required not in paths:
                errors.append(f"artifact_manifest_missing_required_path: {required}")
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
