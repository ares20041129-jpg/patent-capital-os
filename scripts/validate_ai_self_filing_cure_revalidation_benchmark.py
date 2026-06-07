#!/usr/bin/env python3
"""Validate AI self-filing cure revalidation benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import validate_ai_self_filing_authorization
import validate_artifact_hash_manifest
import validate_filing_status_transition


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: object) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    source_deficiency_path = benchmark_dir / "source-deficiency-report.json"
    source_packet_path = benchmark_dir / "source-failed-authorization-packet.json"
    cured_packet_path = benchmark_dir / "cured-ai-self-filing-authorization-packet.json"
    revalidation_path = benchmark_dir / "cure-revalidation.json"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "cure-revalidation-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    source_deficiency = {}
    if source_deficiency_path.exists():
        source_deficiency = load_json(source_deficiency_path)
        if source_deficiency.get("status") != "legal_gate_failed":
            errors.append("source_deficiency_status_must_be_legal_gate_failed")
        if source_deficiency.get("decision") != "do_not_file":
            errors.append("source_deficiency_decision_must_be_do_not_file")
        if source_deficiency.get("external_lawyer_involved") is not False:
            errors.append("source_deficiency_external_lawyer_involved_must_be_false")
        if source_deficiency.get("official_system_touched") is not False:
            errors.append("source_deficiency_must_not_touch_official_system")
        if source_deficiency.get("official_submission_performed") is not False:
            errors.append("source_deficiency_must_not_submit")
        if not isinstance(source_deficiency.get("validator_errors"), list) or not source_deficiency.get("validator_errors"):
            errors.append("source_deficiency_validator_errors_missing")
    else:
        errors.append(f"missing_file: {source_deficiency_path}")

    source_packet = {}
    if source_packet_path.exists():
        source_packet = load_json(source_packet_path)
        ok, source_errors, source_warnings = validate_ai_self_filing_authorization.validate(source_packet, base_dir=benchmark_dir)
        if ok:
            errors.append("source_failed_packet_unexpectedly_passed")
        if not source_errors:
            errors.append("source_failed_packet_missing_validator_errors")
        warnings.extend([f"source_packet: {item}" for item in source_warnings])
        expected_errors = source_deficiency.get("validator_errors") if isinstance(source_deficiency.get("validator_errors"), list) else []
        missing_expected = [str(item) for item in expected_errors if str(item) not in source_errors]
        if missing_expected:
            errors.append("source_deficiency_errors_not_reproduced: " + ",".join(missing_expected))
    else:
        errors.append(f"missing_file: {source_packet_path}")

    cured_packet = {}
    if cured_packet_path.exists():
        cured_packet = load_json(cured_packet_path)
        ok, cured_errors, cured_warnings = validate_ai_self_filing_authorization.validate(cured_packet, base_dir=benchmark_dir)
        if not ok:
            errors.extend([f"cured_packet: {item}" for item in cured_errors])
        warnings.extend([f"cured_packet: {item}" for item in cured_warnings])
        if cured_packet.get("external_lawyer_involved") is not False:
            errors.append("cured_packet_external_lawyer_involved_must_be_false")
    else:
        errors.append(f"missing_file: {cured_packet_path}")

    revalidation = {}
    if revalidation_path.exists():
        revalidation = load_json(revalidation_path)
        if revalidation.get("status") != "ready_for_package_validation":
            errors.append("revalidation_status_must_be_ready_for_package_validation")
        if revalidation.get("decision") != "package_validation_required_before_official_preflight":
            errors.append("revalidation_decision_invalid")
        if revalidation.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("revalidation_legal_gate_mode_must_be_ai_self_filing")
        if revalidation.get("filing_allowed") is not False:
            errors.append("revalidation_filing_allowed_must_be_false")
        if revalidation.get("package_validation_required") is not True:
            errors.append("revalidation_package_validation_required_must_be_true")
        if revalidation.get("official_channel_preflight_required") is not True:
            errors.append("revalidation_official_channel_preflight_required_must_be_true")
        if revalidation.get("official_system_touched") is not False:
            errors.append("revalidation_must_not_touch_official_system")
        if revalidation.get("official_submission_performed") is not False:
            errors.append("revalidation_must_not_submit")
        if revalidation.get("external_lawyer_involved") is not False:
            errors.append("revalidation_external_lawyer_involved_must_be_false")
        if revalidation.get("post_validation_errors") not in ([], None):
            errors.append("revalidation_post_validation_errors_must_be_empty")
        if revalidation.get("unresolved_prior_errors") not in ([], None):
            errors.append("revalidation_unresolved_prior_errors_must_be_empty")
        for field in ["source_deficiency_hash", "source_failed_packet_hash", "cured_packet_hash"]:
            if is_blank(revalidation.get(field)) or not str(revalidation.get(field)).startswith("sha256:"):
                errors.append(f"revalidation_missing_hash: {field}")
    else:
        errors.append(f"missing_file: {revalidation_path}")

    if status_path.exists():
        status = load_json(status_path)
        ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in status_errors])
        warnings.extend([f"filing_status: {item}" for item in status_warnings])
        if status.get("previous_status") != "legal_gate_failed":
            errors.append("filing_status_previous_must_be_legal_gate_failed")
        if status.get("status") != "ready_for_package_validation":
            errors.append("filing_status_must_be_ready_for_package_validation")
        if status.get("legal_gate") != "passed":
            errors.append("filing_status_legal_gate_must_pass")
        if status.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
            errors.append("filing_status_legal_gate_mode_must_be_ai_self_filing")
        if status.get("official_system_touched") is not False:
            errors.append("filing_status_must_not_touch_official_system")
        if status.get("official_submission_performed") is not False:
            errors.append("filing_status_must_not_submit")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "ai self-filing cure revalidation report",
            "legal_gate_failed",
            "ready_for_package_validation",
            "cured prior errors",
            "do not file, pay, sign, submit",
            "not legal advice",
            "not lawyer review",
            "not patent-agent review",
            "not an official submission",
        ]:
            if needle not in text:
                errors.append(f"cure_revalidation_report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in hash_errors])
        warnings.extend([f"artifact_hashes: {item}" for item in hash_warnings])
    else:
        errors.append(f"missing_file: {hashes_path}")

    if source_deficiency and revalidation and source_deficiency.get("case_id") != revalidation.get("source_case_id"):
        errors.append("source_case_id_mismatch")
    if cured_packet and revalidation and cured_packet.get("case_id") != revalidation.get("case_id"):
        errors.append("cured_packet_case_id_mismatch")

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
