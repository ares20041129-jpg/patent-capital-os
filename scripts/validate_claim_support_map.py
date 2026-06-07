#!/usr/bin/env python3
"""Validate a claim support map before filing-readiness use."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_COLUMNS = {
    "Claim",
    "Limitation",
    "Disclosure support",
    "Prior-art delta",
    "Technical effect",
    "Evidence hash",
    "Status",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def parse_tables(text: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    headers: list[str] = []
    rows: list[dict[str, str]] = []

    for i, line in enumerate(lines):
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not headers and set(cells) & REQUIRED_COLUMNS:
            headers = cells
            continue
        if headers and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        if headers and len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))

    return headers, rows


def validate(path: Path, allow_draft: bool = False) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return False, [f"missing_file: {path}"], warnings

    text = path.read_text(encoding="utf-8", errors="replace")
    headers, rows = parse_tables(text)

    missing_columns = sorted(REQUIRED_COLUMNS - set(headers))
    for column in missing_columns:
        errors.append(f"missing_required_column: {column}")

    if not rows:
        errors.append("no_claim_support_rows")

    for index, row in enumerate(rows, start=1):
        for column in REQUIRED_COLUMNS:
            value = row.get(column, "").strip()
            if not value:
                errors.append(f"row_{index}_missing_value: {column}")

        evidence_hash = row.get("Evidence hash", "").strip()
        if evidence_hash and not SHA256_RE.fullmatch(evidence_hash):
            errors.append(f"row_{index}_evidence_hash_must_be_sha256_64_hex")

        status = row.get("Status", "").strip().lower()
        if status in {"missing", "unsupported", "blocked"}:
            errors.append(f"row_{index}_unsupported_status: {status}")
        elif allow_draft and status.startswith("draft"):
            warnings.append(f"row_{index}_draft_status: {status}")

    if "Decision: proceed" not in text and "Decision: revise" not in text and "Decision: block" not in text:
        warnings.append("reviewer_decision_not_found")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("claim_support_map", type=Path)
    parser.add_argument("--allow-draft", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.claim_support_map, allow_draft=args.allow_draft)
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
