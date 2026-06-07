#!/usr/bin/env python3
"""Validate scaffold confirmation to invention disclosure benchmark artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_disclosure_confirmation_packet
import validate_filing_status_transition
import validate_invention_disclosure

AI_ONLY_REVIEW_ROLES = {"ai_legal_compliance_reviewer", "ai_self_filing_compliance_operator"}
PROHIBITED_REVIEW_ROLES = {"patent_agent", "attorney", "in_house_ip_counsel"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def require_ai_only_review(data: dict[str, Any], prefix: str, errors: list[str]) -> None:
    role = str(get_path(data, "legal_drafting_review.reviewed_by.role") or "")
    if role in PROHIBITED_REVIEW_ROLES:
        errors.append(f"{prefix}_must_not_claim_lawyer_or_patent_agent_review")
    elif role not in AI_ONLY_REVIEW_ROLES:
        errors.append(f"{prefix}_must_use_ai_legal_compliance_review_role")
    if get_path(data, "controls.external_lawyer_involved") is not False:
        errors.append(f"{prefix}_external_lawyer_involved_must_be_false")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    scaffold_path = benchmark_dir / "invention-disclosure-scaffold.json"
    packet_path = benchmark_dir / "disclosure-confirmation-packet.json"
    disclosure_path = benchmark_dir / "invention-disclosure.json"
    status_path = benchmark_dir / "filing-status.json"
    report_path = benchmark_dir / "confirmation-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"

    expected_hash = sha256_file(scaffold_path) if scaffold_path.exists() else None
    if expected_hash is None:
        errors.append(f"missing_file: {scaffold_path}")

    if packet_path.exists():
        packet = load_json(packet_path)
        ok, errs, warns = validate_disclosure_confirmation_packet.validate(packet, expected_hash)
        if not ok:
            errors.extend([f"confirmation_packet: {item}" for item in errs])
        warnings.extend([f"confirmation_packet: {item}" for item in warns])
        require_ai_only_review(packet, "confirmation_packet", errors)
    else:
        errors.append(f"missing_file: {packet_path}")

    if disclosure_path.exists():
        ok, errs, warns = validate_invention_disclosure.validate(load_json(disclosure_path))
        if not ok:
            errors.extend([f"invention_disclosure: {item}" for item in errs])
        warnings.extend([f"invention_disclosure: {item}" for item in warns])
        record = load_json(disclosure_path).get("confirmation_record", {})
        if record.get("draft_generation_allowed") is not True:
            errors.append("confirmation_record_must_allow_draft_generation")
        if record.get("filing_allowed") is not False:
            errors.append("confirmation_record_must_not_allow_filing")
        if record.get("external_lawyer_involved") is not False:
            errors.append("confirmation_record_external_lawyer_involved_must_be_false")
        review = record.get("legal_drafting_review", {})
        if isinstance(review, dict):
            role = str(get_path({"legal_drafting_review": review}, "legal_drafting_review.reviewed_by.role") or "")
            if role in PROHIBITED_REVIEW_ROLES:
                errors.append("confirmation_record_must_not_claim_lawyer_or_patent_agent_review")
            elif role not in AI_ONLY_REVIEW_ROLES:
                errors.append("confirmation_record_must_use_ai_legal_compliance_review_role")
    else:
        errors.append(f"missing_file: {disclosure_path}")

    if status_path.exists():
        status = load_json(status_path)
        ok, errs, warns = validate_filing_status_transition.validate(status)
        if not ok:
            errors.extend([f"filing_status: {item}" for item in errs])
        warnings.extend([f"filing_status: {item}" for item in warns])
        if status.get("status") != "draft_only":
            errors.append("status_must_be_draft_only")
        if status.get("legal_gate") != "failed":
            errors.append("legal_gate_must_fail_for_filing")
        if status.get("decision") != "do_not_file":
            errors.append("decision_must_be_do_not_file")
        if status.get("draft_generation_allowed") is not True:
            errors.append("draft_generation_allowed_must_be_true")
        if status.get("filing_allowed") is not False:
            errors.append("filing_allowed_must_be_false")
        if status.get("external_lawyer_involved") is not False:
            errors.append("external_lawyer_involved_must_be_false")
        if status.get("official_system_touched") is not False:
            errors.append("official_system_touched_must_be_false")
        if status.get("official_submission_performed") is not False:
            errors.append("official_submission_performed_must_be_false")
    else:
        errors.append(f"missing_file: {status_path}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "disclosure confirmation report",
            "draft generation allowed: yes",
            "filing allowed: no",
            "legal gate for filing: failed",
            "ai legal/compliance draft review",
            "no external lawyer",
            "official system touched: no",
            "official submission performed: no",
        ]:
            if needle not in text:
                errors.append(f"confirmation_report_missing_text: {needle}")
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
