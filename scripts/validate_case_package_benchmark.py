#!/usr/bin/env python3
"""Validate case package intake dry-run benchmark artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import validate_artifact_hash_manifest
import validate_case_package_manifest
import validate_filing_status_transition
import validate_source_material_manifest


PROHIBITED_DEFAULT_REVIEW_TERMS = re.compile(
    r"\b(attorney|lawyer|counsel)\b|patent-agent|patent agent",
    re.IGNORECASE,
)


def require_no_default_review_terms(text: str, label: str, errors: list[str]) -> None:
    if PROHIBITED_DEFAULT_REVIEW_TERMS.search(text):
        errors.append(f"{label}_must_not_default_to_lawyer_or_patent_agent_review")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    raw_dir = benchmark_dir / "raw-input"
    package_dir = benchmark_dir / "case-package"
    manifest_path = package_dir / "case-package-manifest.json"
    source_manifest_path = package_dir / "01-normalized" / "source-material-manifest.json"
    status_path = package_dir / "filing-status.json"
    report_path = package_dir / "intake-report.md"
    hashes_path = package_dir / "artifact-hashes.json"

    if not raw_dir.exists() or not any(raw_dir.rglob("*")):
        errors.append("raw_input_missing_or_empty")

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_case_package_manifest.validate(manifest, root=package_dir)
        if not ok:
            errors.extend([f"case_package_manifest: {item}" for item in errs])
        warnings.extend([f"case_package_manifest: {item}" for item in warns])
        legal_gate = manifest.get("legal_gate", {}) if isinstance(manifest.get("legal_gate"), dict) else {}
        if legal_gate.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("case_manifest_must_default_to_ai_self_filing_legal_gate_mode")
        if "counsel_review_present" in legal_gate:
            errors.append("case_manifest_must_not_default_to_counsel_review_present")
        if legal_gate.get("ai_legal_compliance_confirmation_present") is not False:
            errors.append("case_manifest_ai_legal_confirmation_must_be_pending")
        if legal_gate.get("external_lawyer_involved") is not False:
            errors.append("case_manifest_external_lawyer_involved_must_be_false")
    else:
        errors.append(f"missing_file: {manifest_path}")

    if source_manifest_path.exists():
        source_manifest = validate_source_material_manifest.load_packet(source_manifest_path)
        ok, errs, warns = validate_source_material_manifest.validate(
            source_manifest,
            base_dir=package_dir,
        )
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

    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        if status.get("status") != "intake_received":
            errors.append("filing_status_must_be_intake_received")
        if status.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("filing_status_must_preserve_ai_self_filing_legal_gate_mode")
        if status.get("external_lawyer_involved") is not False:
            errors.append("filing_status_external_lawyer_involved_must_be_false")
        if status.get("official_system_touched") is not False:
            errors.append("intake_must_not_touch_official_system")
        if status.get("official_submission_performed") is not False:
            errors.append("intake_must_not_perform_official_submission")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "case package intake report",
            "package status: intake_received",
            "official system touched: no",
            "official submission performed: no",
            "filing allowed: no",
            "missing legal items",
            "ai legal/compliance gate confirmation",
        ]:
            if needle not in text:
                errors.append(f"intake_report_missing_text: {needle}")
        require_no_default_review_terms(text, "intake_report", errors)
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
