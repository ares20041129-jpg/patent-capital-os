#!/usr/bin/env python3
"""Validate a disclosure confirmation packet before scaffold promotion."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_PATHS = [
    "case_id",
    "scaffold_hash",
    "confirmed_at",
    "applicant_context.applicant_name",
    "applicant_context.actual_r_and_d_basis",
    "applicant_context.ownership_basis",
    "inventor_input.inventors",
    "inventor_input.contribution_confirmed",
    "technical_effects",
    "similarity_control.no_copying_or_synonym_substitution_confirmed",
    "similarity_control.real_technical_contribution_summary",
    "data_and_evidence.source_hashes",
    "secrecy.invention_completed_in_china",
    "secrecy.foreign_or_pct_planned",
    "secrecy.secrecy_review_status",
    "legal_drafting_review.reviewed_by.name",
    "legal_drafting_review.reviewed_by.organization",
    "legal_drafting_review.reviewed_by.role",
    "legal_drafting_review.review_timestamp",
    "legal_drafting_review.reviewed_scaffold_hash",
    "legal_drafting_review.approval_scope",
    "legal_drafting_review.approval_statement",
    "controls.draft_generation_allowed",
    "controls.filing_allowed",
    "controls.external_lawyer_involved",
    "controls.official_system_touched",
    "controls.official_submission_performed",
    "ai_legal_compliance_questions",
]

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SHA256_TOKEN_RE = re.compile(r"sha256:[^\s,.;)\]\}]+")
ALLOWED_REVIEW_ROLES = {"ai_legal_compliance_reviewer", "ai_self_filing_compliance_operator"}
PROHIBITED_REVIEW_ROLES = {"patent_agent", "attorney", "in_house_ip_counsel"}
PROHIBITED_REVIEW_CLAIM_TOKENS = [
    "patent agent",
    "patent-agent",
    "attorney",
    "lawyer",
    "counsel",
]
RESOLVED_SECRECY_STATUSES = {"completed", "cleared", "not_required"}


def load_packet(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def require_hash(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"{field}_must_be_sha256_64_hex")


def require_hash_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{field}_must_be_list")
        return []

    hashes: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not SHA256_RE.fullmatch(item):
            errors.append(f"{field}[{index}]_must_be_sha256_64_hex")
        else:
            hashes.append(item)
    return hashes


def extract_hash_tokens(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    return [token.rstrip(".,;:)]}") for token in SHA256_TOKEN_RE.findall(value)]


def contains_prohibited_review_claim(value: Any) -> bool:
    text = str(value or "").lower()
    return any(token in text for token in PROHIBITED_REVIEW_CLAIM_TOKENS)


def require_ai_legal_questions(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("ai_legal_compliance_questions_must_be_non_empty_list")
        return
    for index, item in enumerate(value, start=1):
        if is_blank(item):
            errors.append(f"ai_legal_compliance_questions[{index}]_must_not_be_blank")
        if contains_prohibited_review_claim(item):
            errors.append(f"ai_legal_compliance_questions[{index}]_must_not_claim_lawyer_or_patent_agent_review")


def validate(data: dict[str, Any], expected_scaffold_hash: str | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_PATHS:
        if is_blank(get_path(data, path)):
            errors.append(f"missing_required_field: {path}")

    if get_path(data, "inventor_input.contribution_confirmed") is not True:
        errors.append("inventor_contribution_not_confirmed")

    inventors = get_path(data, "inventor_input.inventors")
    if isinstance(inventors, list):
        for index, inventor in enumerate(inventors, start=1):
            if not isinstance(inventor, dict) or is_blank(inventor.get("name")) or is_blank(inventor.get("contribution")):
                errors.append(f"inventor_{index}_missing_name_or_contribution")

    effects = get_path(data, "technical_effects")
    if isinstance(effects, list):
        for index, effect in enumerate(effects, start=1):
            if not isinstance(effect, dict) or is_blank(effect.get("effect")) or is_blank(effect.get("evidence")):
                errors.append(f"technical_effect_{index}_missing_evidence")
    else:
        errors.append("technical_effects_must_be_list")

    if get_path(data, "similarity_control.no_copying_or_synonym_substitution_confirmed") is not True:
        errors.append("no_copying_confirmation_missing")
    contribution = str(get_path(data, "similarity_control.real_technical_contribution_summary") or "").lower()
    if "synonym" in contribution or "random" in contribution or "copy" in contribution:
        errors.append("real_technical_contribution_summary_suggests_copying_or_random_generation")

    evidence = get_path(data, "data_and_evidence")
    source_hashes: list[str] = []
    prohibited_reference_hashes: set[str] = set()
    if isinstance(evidence, dict):
        if is_blank(evidence.get("prototypes")) and is_blank(evidence.get("experiments")) and is_blank(evidence.get("logs_or_measurements")):
            errors.append("confirmation_requires_prototype_experiment_or_measurement_evidence")
        source_hashes = require_hash_list(evidence.get("source_hashes"), "data_and_evidence.source_hashes", errors)
        prohibited_reference_hashes = set(
            require_hash_list(
                evidence.get("prohibited_reference_hashes", []),
                "data_and_evidence.prohibited_reference_hashes",
                errors,
            )
        )
        for source_hash in source_hashes:
            if source_hash in prohibited_reference_hashes:
                errors.append("source_hash_must_not_include_prohibited_reference_hash")
        logs = evidence.get("logs_or_measurements")
        if isinstance(logs, list):
            for index, item in enumerate(logs, start=1):
                for token in extract_hash_tokens(item):
                    if not SHA256_RE.fullmatch(token):
                        errors.append(f"data_and_evidence.logs_or_measurements[{index}]_hash_must_be_sha256_64_hex")
                    elif token in prohibited_reference_hashes:
                        errors.append(f"data_and_evidence.logs_or_measurements[{index}]_uses_prohibited_reference_hash")
    else:
        errors.append("data_and_evidence_must_be_object")

    if isinstance(effects, list):
        source_hash_set = set(source_hashes)
        for index, effect in enumerate(effects, start=1):
            evidence_text = effect.get("evidence") if isinstance(effect, dict) else ""
            for token in extract_hash_tokens(evidence_text):
                if not SHA256_RE.fullmatch(token):
                    errors.append(f"technical_effect_{index}_evidence_hash_must_be_sha256_64_hex")
                elif token in prohibited_reference_hashes:
                    errors.append(f"technical_effect_{index}_uses_prohibited_reference_hash")
                elif token not in source_hash_set:
                    errors.append(f"technical_effect_{index}_evidence_hash_not_in_source_hashes")

    completed_in_china = get_path(data, "secrecy.invention_completed_in_china")
    foreign_planned = get_path(data, "secrecy.foreign_or_pct_planned")
    secrecy_status = str(get_path(data, "secrecy.secrecy_review_status") or "").lower()
    if foreign_planned is True and completed_in_china is True and secrecy_status not in RESOLVED_SECRECY_STATUSES:
        errors.append("secrecy_review_unresolved_for_foreign_or_pct_plan")

    review_role = str(get_path(data, "legal_drafting_review.reviewed_by.role") or "")
    if review_role in PROHIBITED_REVIEW_ROLES:
        errors.append("legal_drafting_review_must_not_claim_lawyer_or_patent_agent_review")
    elif review_role not in ALLOWED_REVIEW_ROLES:
        errors.append("legal_drafting_review_role_invalid")
    for field in [
        "legal_drafting_review.reviewed_by.name",
        "legal_drafting_review.reviewed_by.organization",
        "legal_drafting_review.approval_statement",
    ]:
        if contains_prohibited_review_claim(get_path(data, field)):
            errors.append(f"{field}_must_not_claim_lawyer_or_patent_agent_review")
    if get_path(data, "legal_drafting_review.approval_scope") != "draft_generation_only":
        errors.append("legal_drafting_review_scope_must_be_draft_generation_only")
    if get_path(data, "legal_drafting_review.filing_approved") is not False:
        errors.append("legal_drafting_review_must_not_approve_filing")
    require_ai_legal_questions(get_path(data, "ai_legal_compliance_questions"), errors)
    if not is_blank(get_path(data, "counsel_questions")):
        errors.append("confirmation_packet_must_not_use_counsel_questions")

    scaffold_hash = str(get_path(data, "scaffold_hash") or "")
    reviewed_hash = str(get_path(data, "legal_drafting_review.reviewed_scaffold_hash") or "")
    require_hash(scaffold_hash, "scaffold_hash", errors)
    require_hash(reviewed_hash, "legal_drafting_review.reviewed_scaffold_hash", errors)
    if scaffold_hash and reviewed_hash and scaffold_hash != reviewed_hash:
        errors.append("scaffold_hash_mismatch_between_packet_and_legal_review")
    if expected_scaffold_hash and scaffold_hash != expected_scaffold_hash:
        errors.append("scaffold_hash_does_not_match_input_scaffold")

    if get_path(data, "controls.draft_generation_allowed") is not True:
        errors.append("draft_generation_must_be_allowed_by_confirmation_controls")
    if get_path(data, "controls.filing_allowed") is not False:
        errors.append("confirmation_packet_must_not_allow_filing")
    if get_path(data, "controls.external_lawyer_involved") is not False:
        errors.append("confirmation_packet_must_not_involve_external_lawyer")
    if get_path(data, "controls.official_system_touched") is not False:
        errors.append("confirmation_packet_must_not_touch_official_system")
    if get_path(data, "controls.official_submission_performed") is not False:
        errors.append("confirmation_packet_must_not_perform_official_submission")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--expected-scaffold-hash")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_packet(args.packet), args.expected_scaffold_hash)
    except Exception as exc:
        ok, errors, warnings = False, [str(exc)], []

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
