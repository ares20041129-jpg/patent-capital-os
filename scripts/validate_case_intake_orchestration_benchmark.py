#!/usr/bin/env python3
"""Validate raw case intake orchestration benchmark artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import validate_artifact_hash_manifest
import validate_batch_processor_result
import validate_case_package_manifest
import validate_case_queue
import validate_filing_status_transition
import validate_invention_disclosure_scaffold
import validate_source_material_manifest


PROHIBITED_DEFAULT_REVIEW_TERMS = re.compile(
    r"\b(attorney|lawyer|counsel)\b|patent-agent|patent agent",
    re.IGNORECASE,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_no_default_review_terms(text: str, label: str, errors: list[str]) -> None:
    if PROHIBITED_DEFAULT_REVIEW_TERMS.search(text):
        errors.append(f"{label}_must_not_default_to_lawyer_or_patent_agent_review")


def require_legal_gate_metadata(rows: list, label: str, errors: list[str]) -> None:
    for index, item in enumerate(rows, start=1):
        if not isinstance(item, dict):
            continue
        if item.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append(f"{label}_{index}_must_preserve_ai_self_filing_legal_gate_mode")
        if item.get("external_lawyer_involved") is not False:
            errors.append(f"{label}_{index}_external_lawyer_involved_must_be_false")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    package_dir = benchmark_dir / "case-package"
    scaffold_dir = benchmark_dir / "disclosure-normalization-scaffold"
    package_manifest_path = package_dir / "case-package-manifest.json"
    source_manifest_path = package_dir / "01-normalized" / "source-material-manifest.json"
    filing_status_path = package_dir / "filing-status.json"
    scaffold_path = scaffold_dir / "invention-disclosure-scaffold.json"
    queue_path = benchmark_dir / "case-queue.json"
    result_path = benchmark_dir / "batch-processor-result.json"
    report_path = benchmark_dir / "intake-orchestration-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    if package_manifest_path.exists():
        manifest = load_json(package_manifest_path)
        ok, errs, warns = validate_case_package_manifest.validate(manifest, root=package_dir)
        if not ok:
            errors.extend([f"case_package_manifest: {item}" for item in errs])
        warnings.extend([f"case_package_manifest: {item}" for item in warns])
        if manifest.get("legal_gate", {}).get("filing_allowed") is not False:
            errors.append("case_package_must_not_allow_filing")
        legal_gate = manifest.get("legal_gate", {}) if isinstance(manifest.get("legal_gate"), dict) else {}
        if legal_gate.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("case_package_must_default_to_ai_self_filing_legal_gate_mode")
        if "counsel_review_present" in legal_gate:
            errors.append("case_package_must_not_default_to_counsel_review_present")
        if legal_gate.get("ai_legal_compliance_confirmation_present") is not False:
            errors.append("case_package_ai_legal_confirmation_must_be_pending")
        if legal_gate.get("external_lawyer_involved") is not False:
            errors.append("case_package_external_lawyer_involved_must_be_false")
        if manifest.get("official_actions", {}).get("official_system_touched") is not False:
            errors.append("case_package_must_not_touch_official_system")
        if manifest.get("official_actions", {}).get("official_submission_performed") is not False:
            errors.append("case_package_must_not_submit")
    else:
        errors.append(f"missing_file: {package_manifest_path}")

    if source_manifest_path.exists():
        source_manifest = load_json(source_manifest_path)
        ok, errs, warns = validate_source_material_manifest.validate(source_manifest, base_dir=package_dir)
        if not ok:
            errors.extend([f"source_material_manifest: {item}" for item in errs])
        warnings.extend([f"source_material_manifest: {item}" for item in warns])
        missing_materials = source_manifest.get("missing_materials", [])
        if isinstance(missing_materials, list):
            for item in missing_materials:
                require_no_default_review_terms(str(item), "source_manifest_missing_materials", errors)
        if "AI legal/compliance gate confirmation" not in missing_materials:
            errors.append("source_manifest_must_require_ai_legal_compliance_confirmation")
    else:
        errors.append(f"missing_file: {source_manifest_path}")

    if filing_status_path.exists():
        ok, errs, warns = validate_filing_status_transition.validate(load_json(filing_status_path))
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        status = load_json(filing_status_path)
        if status.get("status") != "intake_received":
            errors.append("filing_status_must_remain_intake_received")
        if status.get("official_system_touched") is not False:
            errors.append("filing_status_must_not_touch_official_system")
        if status.get("official_submission_performed") is not False:
            errors.append("filing_status_must_not_submit")
        if status.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("filing_status_must_preserve_ai_self_filing_legal_gate_mode")
        if status.get("external_lawyer_involved") is not False:
            errors.append("filing_status_external_lawyer_involved_must_be_false")
    else:
        errors.append(f"missing_file: {filing_status_path}")

    if scaffold_path.exists():
        scaffold = load_json(scaffold_path)
        ok, errs, warns = validate_invention_disclosure_scaffold.validate(scaffold)
        if not ok:
            errors.extend([f"invention_disclosure_scaffold: {item}" for item in errs])
        warnings.extend([f"invention_disclosure_scaffold: {item}" for item in warns])
        disclosure = scaffold.get("invention_disclosure", {}) if isinstance(scaffold.get("invention_disclosure"), dict) else {}
        if "counsel_questions" in disclosure:
            errors.append("scaffold_must_not_default_to_counsel_questions")
        if not isinstance(disclosure.get("ai_legal_compliance_questions"), list) or not disclosure.get("ai_legal_compliance_questions"):
            errors.append("scaffold_must_include_ai_legal_compliance_questions")
        controls = scaffold.get("scaffold_controls", {})
        if scaffold.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("scaffold_must_preserve_ai_self_filing_legal_gate_mode")
        if scaffold.get("external_lawyer_involved") is not False:
            errors.append("scaffold_external_lawyer_involved_must_be_false")
        if controls.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("scaffold_controls_must_preserve_ai_self_filing_legal_gate_mode")
        if controls.get("external_lawyer_involved") is not False:
            errors.append("scaffold_controls_external_lawyer_involved_must_be_false")
        if controls.get("filing_allowed") is not False:
            errors.append("scaffold_must_not_allow_filing")
        if controls.get("draft_generation_allowed") is not False:
            errors.append("scaffold_must_not_allow_draft_generation")
    else:
        errors.append(f"missing_file: {scaffold_path}")

    if queue_path.exists():
        queue = load_json(queue_path)
        ok, errs, warns = validate_case_queue.validate(queue)
        if not ok:
            errors.extend([f"case_queue: {item}" for item in errs])
        warnings.extend([f"case_queue: {item}" for item in warns])
        if queue.get("official_submission_allowed") is not False:
            errors.append("queue_must_not_allow_official_submission")
        if queue.get("official_system_touch_allowed") is not False:
            errors.append("queue_must_not_allow_official_system_touch")
        require_legal_gate_metadata(queue.get("items", []), "queue_item", errors)
    else:
        errors.append(f"missing_file: {queue_path}")

    if result_path.exists():
        result = load_json(result_path)
        ok, errs, warns = validate_batch_processor_result.validate(result)
        if not ok:
            errors.extend([f"batch_result: {item}" for item in errs])
        warnings.extend([f"batch_result: {item}" for item in warns])
        if result.get("official_system_touched") is not False:
            errors.append("batch_result_must_not_touch_official_system")
        if result.get("official_submission_performed") is not False:
            errors.append("batch_result_must_not_submit")
        if result.get("batch_errors"):
            errors.append("batch_result_must_not_have_batch_errors")
        require_legal_gate_metadata(result.get("results", []), "batch_result", errors)
    else:
        errors.append(f"missing_file: {result_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "case intake orchestration report",
            "official system touched: no",
            "official submission performed: no",
            "filing allowed: no",
            "draft generation allowed: no",
            "legal gate metadata: present",
            "external professional involved: no",
            "pending confirmations",
            "ai legal/compliance gate confirmation",
        ]:
            if needle not in text:
                errors.append(f"intake_orchestration_report_missing_text: {needle}")
        require_no_default_review_terms(text, "intake_orchestration_report", errors)
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
