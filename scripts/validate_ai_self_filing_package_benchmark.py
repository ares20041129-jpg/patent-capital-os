#!/usr/bin/env python3
"""Validate generated AI self-filing package benchmark artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import validate_abnormal_filing_risk_assessment
import validate_ai_self_filing_authorization
import validate_artifact_hash_manifest
import validate_filing_package_manifest
import validate_filing_status_transition


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    packet_path = benchmark_dir / "ai-self-filing-authorization-packet.json"
    abnormal_path = benchmark_dir / "abnormal-filing-risk-assessment.json"
    manifest_path = benchmark_dir / "filing-package-manifest.yaml"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "ai-self-filing-package-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    packet = {}
    if packet_path.exists():
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_ai_self_filing_authorization.validate(packet, base_dir=benchmark_dir)
        if not ok:
            errors.extend([f"ai_self_filing_packet: {item}" for item in errs])
        warnings.extend([f"ai_self_filing_packet: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {packet_path}")

    if abnormal_path.exists():
        abnormal = json.loads(abnormal_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_abnormal_filing_risk_assessment.validate(abnormal)
        if not ok:
            errors.extend([f"abnormal_filing_risk_assessment: {item}" for item in errs])
        warnings.extend([f"abnormal_filing_risk_assessment: {item}" for item in warns])
        if packet:
            expected_hash = packet.get("ai_compliance_review", {}).get("abnormal_filing_risk_assessment", {}).get("artifact_hash")
            actual_hash = "sha256:" + hashlib.sha256(abnormal_path.read_bytes()).hexdigest()
            if expected_hash != actual_hash:
                errors.append("abnormal_filing_risk_assessment_hash_mismatch")
            if abnormal.get("case_id") != packet.get("case_id"):
                errors.append("abnormal_filing_risk_assessment_case_id_mismatch")
            if abnormal.get("risk_level") != "low":
                errors.append("abnormal_filing_risk_assessment_must_be_low")
            if abnormal.get("reference_patent_delta_hash"):
                packet_assessment = packet.get("ai_compliance_review", {}).get("abnormal_filing_risk_assessment", {})
                if packet_assessment.get("reference_patent_delta_hash") != abnormal.get("reference_patent_delta_hash"):
                    errors.append("reference_patent_delta_hash_mismatch")
                for key in ["reference_delta_rows_count", "reference_delta_claim_elements_count"]:
                    if packet_assessment.get(key) != abnormal.get(key):
                        errors.append(f"{key}_mismatch")
                if packet_assessment.get("reference_delta_boundary_preserved") is not True:
                    errors.append("reference_delta_boundary_must_be_preserved")
    else:
        errors.append(f"missing_file: {abnormal_path}")

    if manifest_path.exists():
        manifest = validate_filing_package_manifest.load_packet(manifest_path)
        ok, errs, warns = validate_filing_package_manifest.validate(manifest, base_dir=benchmark_dir)
        if not ok:
            errors.extend([f"filing_package_manifest: {item}" for item in errs])
        warnings.extend([f"filing_package_manifest: {item}" for item in warns])
        if packet and manifest.get("case_id") != packet.get("case_id"):
            errors.append("packet_manifest_case_id_mismatch")
        if packet and manifest.get("final_package_hash") != packet.get("final_package_hash"):
            errors.append("packet_manifest_final_package_hash_mismatch")
    else:
        errors.append(f"missing_file: {manifest_path}")

    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        if status.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("status_legal_gate_mode_must_be_ai_self_filing")
        if status.get("external_lawyer_involved") is not False:
            errors.append("status_external_lawyer_involved_must_be_false")
        if status.get("official_system_touched") is not False:
            errors.append("status_must_not_touch_official_system")
        if status.get("official_submission_performed") is not False:
            errors.append("status_must_not_submit")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "ai self-filing",
            "ai legal gate review",
            "authorization scope check",
            "self-filing eligibility check",
            "official channel boundary check",
            "abnormal filing risk evidence",
            "assessment hash",
            "no external lawyer",
            "not a lawyer review",
            "not a patent-agent review",
            "not an official submission",
        ]:
            if needle not in text:
                errors.append(f"ai_self_filing_report_missing_text: {needle}")
        if abnormal_path.exists():
            abnormal = json.loads(abnormal_path.read_text(encoding="utf-8"))
            if abnormal.get("reference_patent_delta_hash"):
                for needle in [
                    "reference delta boundary",
                    "reference-patent delta hash",
                    "boundary preserved: true",
                    "not applicant claim support",
                ]:
                    if needle not in text:
                        errors.append(f"ai_self_filing_reference_delta_report_missing_text: {needle}")
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
