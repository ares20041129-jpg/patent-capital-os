#!/usr/bin/env python3
"""Validate draft evidence provenance JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def require_hash_list(values: Any, label: str, errors: list[str]) -> None:
    if is_blank(values):
        return
    if not isinstance(values, list):
        errors.append(f"{label}_must_be_list")
        return
    for index, value in enumerate(values):
        require_hash(value, f"{label}[{index}]", errors)


def validate(data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in [
        "case_id",
        "status",
        "decision",
        "source_material_manifest_hash",
        "invention_disclosure_hash",
        "patent_application_draft_hash",
        "claim_support_map_hash",
        "filing_status_hash",
        "claim_support_rows",
    ]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("status") != "draft_evidence_provenance_checked":
        errors.append("status_must_be_draft_evidence_provenance_checked")
    if data.get("decision") != "draft_only_do_not_file":
        errors.append("decision_must_be_draft_only_do_not_file")
    if data.get("filing_allowed") is not False:
        errors.append("filing_allowed_must_be_false")
    if data.get("draft_generation_allowed") is not True:
        errors.append("draft_generation_allowed_must_be_true")
    if data.get("official_system_touched") is not False:
        errors.append("official_system_touched_must_be_false")
    if data.get("official_submission_performed") is not False:
        errors.append("official_submission_performed_must_be_false")
    if data.get("external_lawyer_involved") is not False:
        errors.append("external_lawyer_involved_must_be_false")
    if data.get("errors") not in ([], None):
        errors.append("provenance_errors_must_be_empty")
    if data.get("unsupported_rows") not in ([], None):
        errors.append("unsupported_rows_must_be_empty")

    for key in [
        "source_material_manifest_hash",
        "invention_disclosure_hash",
        "patent_application_draft_hash",
        "claim_support_map_hash",
        "filing_status_hash",
    ]:
        require_hash(data.get(key), key, errors)
    if data.get("reference_patent_delta_hash") is not None:
        require_hash(data.get("reference_patent_delta_hash"), "reference_patent_delta_hash", errors)
        if int(data.get("reference_delta_claim_elements_count") or 0) <= 0:
            errors.append("reference_delta_claim_elements_count_required")
        if int(data.get("reference_delta_rows_count") or 0) <= 0:
            errors.append("reference_delta_rows_count_required")
    require_hash_list(data.get("own_support_hashes"), "own_support_hashes", errors)
    require_hash_list(data.get("prohibited_reference_hashes"), "prohibited_reference_hashes", errors)

    rows = data.get("claim_support_rows")
    if isinstance(rows, list):
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"row_{index}_must_be_object")
                continue
            for key in ["claim", "limitation", "evidence_hash", "evidence_role", "passes"]:
                if is_blank(row.get(key)):
                    errors.append(f"row_{index}_missing_required_field: {key}")
            if row.get("passes") is not True:
                errors.append(f"row_{index}_must_pass")
            if row.get("evidence_role") == "reference_or_prior_art":
                errors.append(f"row_{index}_must_not_use_prior_art_as_support")
            evidence_hash = str(row.get("evidence_hash") or "")
            if evidence_hash and not SHA256_RE.fullmatch(evidence_hash):
                errors.append(f"row_{index}_evidence_hash_must_be_sha256_64_hex")
    else:
        errors.append("claim_support_rows_must_be_list")

    if not data.get("reference_identifiers"):
        warnings.append("reference_identifiers_missing")
    if not data.get("own_support_hashes"):
        warnings.append("own_support_hashes_missing")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("provenance", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        ok, errors, warnings = validate(load_json(args.provenance))
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
