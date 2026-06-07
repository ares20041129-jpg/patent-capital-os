#!/usr/bin/env python3
"""Validate a generated patent application draft artifact."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_HEADINGS = [
    "## Title",
    "## Technical Field",
    "## Background",
    "## Technical Problem",
    "## Technical Solution",
    "## Beneficial Technical Effects",
    "## Brief Description Of Drawings",
    "## Detailed Embodiments",
    "## Claims Draft",
    "## Abstract",
    "## Claim Support Map Link",
    "## Filing Gate",
]

FORBIDDEN_STATUS_WORDS = [
    "official_receipt_received",
    "accepted_or_application_number_received",
    "application number received",
    "filed successfully",
    "officially filed",
]


def section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"^{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def validate(path: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return False, [f"missing_file: {path}"], warnings

    text = path.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing_heading: {heading}")
        elif not section_text(text, heading):
            errors.append(f"empty_section: {heading}")

    status_line = next((line for line in text.splitlines() if line.lower().startswith("draft status:")), "")
    if not status_line:
        errors.append("missing_draft_status")
    else:
        status = status_line.split(":", 1)[1].strip().lower()
        if status not in {"draft_only", "counsel_review_needed", "ai_self_filing_authorization_needed"}:
            errors.append("draft_status_must_be_draft_only_counsel_review_needed_or_ai_self_filing_authorization_needed")

    if "## Counsel Questions" not in text and "## AI Legal/Compliance Questions" not in text:
        errors.append("missing_heading: ## AI Legal/Compliance Questions or ## Counsel Questions")
    elif "## AI Legal/Compliance Questions" in text and not section_text(text, "## AI Legal/Compliance Questions"):
        errors.append("empty_section: ## AI Legal/Compliance Questions")
    elif "## Counsel Questions" in text and not section_text(text, "## Counsel Questions"):
        errors.append("empty_section: ## Counsel Questions")

    for word in FORBIDDEN_STATUS_WORDS:
        if word in lower:
            errors.append(f"forbidden_filing_status_phrase: {word}")

    filing_gate = section_text(text, "## Filing Gate").lower()
    if "do not file" not in filing_gate:
        errors.append("filing_gate_must_say_do_not_file")
    if "legal gate" not in filing_gate:
        errors.append("filing_gate_must_reference_legal_gate")

    claims = section_text(text, "## Claims Draft")
    if "1." not in claims:
        errors.append("claims_draft_missing_independent_claim_number")

    support_link = section_text(text, "## Claim Support Map Link")
    if "claim-support-map" not in support_link.lower():
        errors.append("claim_support_map_link_missing")

    if "unsupported" in lower:
        warnings.append("draft_contains_unsupported_marker")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.draft)
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
