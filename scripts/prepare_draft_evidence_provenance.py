#!/usr/bin/env python3
"""Prepare draft evidence provenance artifacts for a patent draft package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_claim_support_map
import validate_filing_status_transition
import validate_invention_disclosure
import validate_patent_application_draft
import validate_reference_patent_delta
import validate_source_material_manifest


SHA_RE = re.compile(r"sha256:[0-9a-f]{64}")
SHA256_FULL_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PRIOR_ART_TYPES = {"prior_art", "reference_patent", "patent", "public_prior_art"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def collect_sha256(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for item in value.values():
            found.update(collect_sha256(item))
    elif isinstance(value, list):
        for item in value:
            found.update(collect_sha256(item))
    elif isinstance(value, str):
        found.update(SHA_RE.findall(value))
    return found


def material_indexes(manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], set[str], set[str]]:
    by_hash: dict[str, dict[str, Any]] = {}
    own_support: set[str] = set()
    prior_art: set[str] = set()
    for item in as_list(manifest.get("materials")):
        if not isinstance(item, dict):
            continue
        item_hash = str(item.get("hash") or "")
        if not SHA256_FULL_RE.fullmatch(item_hash):
            continue
        by_hash[item_hash] = item
        material_type = str(item.get("type") or "").lower()
        is_prior_art = material_type in PRIOR_ART_TYPES or "prior" in material_type or item.get("confidentiality") == "public"
        if is_prior_art:
            prior_art.add(item_hash)
        elif item.get("usable_for_claim_support") is True:
            own_support.add(item_hash)
    return by_hash, own_support, prior_art


def resolve_material_path(base_dir: Path, raw_path: Any) -> Path:
    return validate_source_material_manifest.resolve_material_path(base_dir, raw_path)


def copy_manifest_material_files(manifest: dict[str, Any], source_base_dir: Path, output_root: Path) -> list[Path]:
    copied: list[Path] = []
    for item in as_list(manifest.get("materials")):
        if not isinstance(item, dict) or not item.get("filename"):
            continue
        raw_filename = str(item["filename"])
        try:
            source = resolve_material_path(source_base_dir, raw_filename)
        except ValueError:
            continue
        if not source.exists() or not source.is_file():
            continue
        target = output_root / raw_filename
        if source.resolve() != target.resolve():
            copy_file(source, target)
        copied.append(target)
    return copied


def copy_reference_delta_support_files(reference_delta: dict[str, Any], source_base_dir: Path, output_root: Path) -> list[Path]:
    copied: list[Path] = []
    raw_paths: list[str] = []
    source_input = reference_delta.get("source_input") if isinstance(reference_delta.get("source_input"), dict) else {}
    if source_input.get("path"):
        raw_paths.append(str(source_input["path"]))
    for item in as_list(reference_delta.get("claim_elements")):
        if isinstance(item, dict) and item.get("support_path"):
            raw_paths.append(str(item["support_path"]))
    for raw_path in sorted(set(raw_paths)):
        path = Path(raw_path)
        if path.is_absolute() or ".." in path.parts:
            continue
        source = (source_base_dir / path).resolve()
        if not source.exists() or not source.is_file():
            continue
        target = output_root / path
        if source.resolve() != target.resolve():
            copy_file(source, target)
        copied.append(target)
    return copied


def claims_section(draft_path: Path) -> str:
    text = draft_path.read_text(encoding="utf-8", errors="replace")
    return validate_patent_application_draft.section_text(text, "## Claims Draft")


def build_rows(
    claim_map_path: Path,
    manifest: dict[str, Any],
    disclosure: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    _, rows = validate_claim_support_map.parse_tables(claim_map_path.read_text(encoding="utf-8", errors="replace"))
    by_hash, own_support_hashes, prior_art_hashes = material_indexes(manifest)
    disclosure_hashes = collect_sha256(disclosure.get("data_and_evidence", {}))
    disclosure_hashes.update(collect_sha256(disclosure.get("technical_effects", [])))
    allowed_hashes = own_support_hashes.intersection(disclosure_hashes) or own_support_hashes or disclosure_hashes

    provenance_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        evidence_hash = str(row.get("Evidence hash") or "").strip()
        material = by_hash.get(evidence_hash, {})
        role = "unknown"
        row_errors: list[str] = []
        if not SHA256_FULL_RE.fullmatch(evidence_hash):
            row_errors.append("evidence_hash_missing_or_invalid")
        elif evidence_hash in prior_art_hashes:
            role = "reference_or_prior_art"
            row_errors.append("claim_limitation_uses_reference_or_prior_art_as_support")
        elif evidence_hash in allowed_hashes:
            role = "own_source_material"
        elif evidence_hash in disclosure_hashes:
            role = "disclosure_evidence_without_manifest_material"
            warnings.append(f"row_{index}_evidence_hash_not_in_source_manifest: {evidence_hash}")
        else:
            row_errors.append("evidence_hash_not_found_in_disclosure_or_source_manifest")

        if row_errors:
            errors.extend([f"row_{index}: {item}" for item in row_errors])
        provenance_rows.append(
            {
                "row": index,
                "claim": row.get("Claim", ""),
                "limitation": row.get("Limitation", ""),
                "evidence_hash": evidence_hash,
                "evidence_role": role,
                "material_id": material.get("material_id", ""),
                "material_type": material.get("type", ""),
                "source_owner": material.get("source_owner", ""),
                "passes": not row_errors,
                "errors": row_errors,
            }
        )
    return provenance_rows, errors, warnings


def reference_identifiers(disclosure: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for item in as_list(disclosure.get("known_prior_art")):
        if isinstance(item, dict) and item.get("publication"):
            refs.append(str(item["publication"]))
    return refs


def render_report(provenance: dict[str, Any]) -> str:
    lines = [
        "# Draft Evidence Provenance Report",
        "",
        f"Case ID: {provenance.get('case_id')}",
        "Status: draft_evidence_provenance_checked",
        "Decision: draft_only_do_not_file",
        f"Claim support rows checked: {len(provenance.get('claim_support_rows') or [])}",
        f"Unsupported rows: {len(provenance.get('unsupported_rows') or [])}",
        "Official system touched: no",
        "Official submission performed: no",
        "",
        "## Claim Support Evidence",
        "",
        "| Claim | Limitation | Evidence hash | Evidence role | Material ID | Pass |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in provenance.get("claim_support_rows", []):
        lines.append(
            "| {claim} | {limitation} | {evidence_hash} | {role} | {material_id} | {passes} |".format(
                claim=str(row.get("claim", "")).replace("|", "/"),
                limitation=str(row.get("limitation", "")).replace("|", "/"),
                evidence_hash=str(row.get("evidence_hash", "")).replace("|", "/"),
                role=str(row.get("evidence_role", "")).replace("|", "/"),
                material_id=str(row.get("material_id", "")).replace("|", "/"),
                passes="yes" if row.get("passes") else "no",
            )
        )
    lines.extend(
        [
            "",
        "## Reference Patent Boundary",
        "",
        "Reference patents may be used for vocabulary, problem framing, category patterns, and prior-art boundaries. They must not be used as evidence for the applicant's own claim limitations, copied claim text, synonym-substituted variants, or fabricated technical effects.",
        "",
        "## Reference Patent Delta Binding",
        "",
        "When `reference-patent-delta.json` is present, this provenance gate validates and hash-binds it as claim-strategy boundary evidence. It remains prohibited as applicant claim support.",
        "",
        "## Filing Boundary",
            "",
            "This provenance gate is draft-only evidence. It is not legal advice, not lawyer review, not patent-agent review, not filing package validation, not official-channel preflight, not an official submission, not a receipt, and not an application number.",
            "",
        ]
    )
    return "\n".join(lines)


def artifact_manifest(output_dir: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [
            {
                "path": rel(path, output_dir),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
    }


def prepare(draft_package_dir: Path, source_manifest_path: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    draft_root = draft_package_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    disclosure_path = draft_root / "invention-disclosure.json"
    draft_path = draft_root / "patent-application-draft.md"
    claim_map_path = draft_root / "claim-support-map.md"
    status_path = draft_root / "filing-status.json"
    reference_delta_path = draft_root / "reference-patent-delta.json"
    for path in [disclosure_path, draft_path, claim_map_path, status_path, source_manifest_path.resolve()]:
        if not path.exists():
            raise RuntimeError(f"missing_required_file: {path}")

    disclosure = load_json(disclosure_path)
    manifest = validate_source_material_manifest.load_packet(source_manifest_path.resolve())
    status = load_json(status_path)
    case_id = str(disclosure.get("case_id") or status.get("case_id") or "unknown-case")

    source_ok, source_errors, source_warnings = validate_source_material_manifest.validate(
        manifest,
        base_dir=source_manifest_path.resolve().parent,
    )
    disclosure_ok, disclosure_errors, disclosure_warnings = validate_invention_disclosure.validate(disclosure)
    draft_ok, draft_errors, draft_warnings = validate_patent_application_draft.validate(draft_path)
    claim_ok, claim_errors, claim_warnings = validate_claim_support_map.validate(claim_map_path, allow_draft=True)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(status)
    reference_delta: dict[str, Any] | None = None
    reference_delta_ok = True
    reference_delta_errors: list[str] = []
    reference_delta_warnings: list[str] = []
    if reference_delta_path.exists():
        reference_delta = load_json(reference_delta_path)
        reference_delta_ok, reference_delta_errors, reference_delta_warnings = validate_reference_patent_delta.validate(
            reference_delta,
            draft_root,
        )
        if reference_delta.get("case_id") != case_id:
            reference_delta_ok = False
            reference_delta_errors.append("reference_delta_case_id_must_match_provenance_case_id")

    rows, row_errors, row_warnings = build_rows(claim_map_path, manifest, disclosure)
    claims_text = claims_section(draft_path)
    refs = reference_identifiers(disclosure)
    reference_claim_errors = [
        f"claim_text_contains_reference_identifier: {ref}"
        for ref in refs
        if ref and ref.lower() in claims_text.lower()
    ]

    output_manifest = output_root / "source-material-manifest.yaml"
    output_disclosure = output_root / "invention-disclosure.json"
    output_draft = output_root / "patent-application-draft.md"
    output_claim_map = output_root / "claim-support-map.md"
    output_status = output_root / "filing-status.json"
    output_reference_delta = output_root / "reference-patent-delta.json"
    for source, target in [
        (source_manifest_path.resolve(), output_manifest),
        (disclosure_path, output_disclosure),
        (draft_path, output_draft),
        (claim_map_path, output_claim_map),
        (status_path, output_status),
    ]:
        copy_file(source, target)
    if reference_delta_path.exists():
        copy_file(reference_delta_path, output_reference_delta)
    copied_reference_delta_files = (
        copy_reference_delta_support_files(reference_delta, draft_root, output_root)
        if reference_delta_path.exists() and reference_delta
        else []
    )
    copied_material_files = copy_manifest_material_files(
        manifest,
        source_manifest_path.resolve().parent,
        output_root,
    )

    _, own_hashes, prior_hashes = material_indexes(manifest)
    all_errors = (
        [f"source_manifest: {item}" for item in source_errors]
        + [f"invention_disclosure: {item}" for item in disclosure_errors]
        + [f"patent_application_draft: {item}" for item in draft_errors]
        + [f"claim_support_map: {item}" for item in claim_errors]
        + [f"filing_status: {item}" for item in status_errors]
        + [f"reference_patent_delta: {item}" for item in reference_delta_errors]
        + row_errors
        + reference_claim_errors
    )
    all_warnings = (
        [f"source_manifest: {item}" for item in source_warnings]
        + [f"invention_disclosure: {item}" for item in disclosure_warnings]
        + [f"patent_application_draft: {item}" for item in draft_warnings]
        + [f"claim_support_map: {item}" for item in claim_warnings]
        + [f"filing_status: {item}" for item in status_warnings]
        + [f"reference_patent_delta: {item}" for item in reference_delta_warnings]
        + row_warnings
    )
    provenance = {
        "case_id": case_id,
        "status": "draft_evidence_provenance_checked",
        "decision": "draft_only_do_not_file",
        "source_material_manifest_hash": sha256_file(output_manifest),
        "invention_disclosure_hash": sha256_file(output_disclosure),
        "patent_application_draft_hash": sha256_file(output_draft),
        "claim_support_map_hash": sha256_file(output_claim_map),
        "filing_status_hash": sha256_file(output_status),
        **({"reference_patent_delta_hash": sha256_file(output_reference_delta)} if reference_delta_path.exists() else {}),
        **({"reference_delta_claim_elements_count": len(reference_delta.get("claim_elements") or [])} if reference_delta_path.exists() and reference_delta else {}),
        **({"reference_delta_rows_count": len(reference_delta.get("delta_rows") or [])} if reference_delta_path.exists() and reference_delta else {}),
        "own_support_hashes": sorted(own_hashes),
        "prohibited_reference_hashes": sorted(prior_hashes),
        "reference_identifiers": refs,
        "claim_support_rows": rows,
        "unsupported_rows": [row for row in rows if not row.get("passes")],
        "errors": all_errors,
        "warnings": all_warnings,
        "draft_generation_allowed": True,
        "filing_allowed": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }
    provenance_path = output_root / "draft-evidence-provenance.json"
    write_json(provenance_path, provenance)
    report_path = output_root / "draft-evidence-provenance-report.md"
    report_path.write_text(render_report(provenance), encoding="utf-8")
    hashes_path = output_root / "artifact-hashes.json"
    files = [
        output_manifest,
        *copied_material_files,
        *copied_reference_delta_files,
        output_disclosure,
        output_draft,
        output_claim_map,
        output_status,
        *([output_reference_delta] if reference_delta_path.exists() else []),
        provenance_path,
        report_path,
    ]
    write_json(hashes_path, artifact_manifest(output_root, case_id, files))
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hashes_path)

    ok = (
        source_ok
        and disclosure_ok
        and draft_ok
        and claim_ok
        and status_ok
        and reference_delta_ok
        and not row_errors
        and not reference_claim_errors
        and hash_ok
    )
    return {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "source_material_manifest": str(output_manifest),
            "invention_disclosure": str(output_disclosure),
            "patent_application_draft": str(output_draft),
            "claim_support_map": str(output_claim_map),
            "filing_status": str(output_status),
            **({"reference_patent_delta": str(output_reference_delta)} if reference_delta_path.exists() else {}),
            "draft_evidence_provenance": str(provenance_path),
            "draft_evidence_provenance_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "errors": all_errors,
        "warnings": all_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft_package_dir", type=Path)
    parser.add_argument("source_material_manifest", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.draft_package_dir, args.source_material_manifest, args.output_dir)
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "official_system_touched": False,
            "official_submission_performed": False,
            "external_lawyer_involved": False,
        }, 1
    rendered = json.dumps(response, ensure_ascii=False, indent=2)
    if args.json:
        print(rendered)
    else:
        print("PASS" if response.get("ok") else "FAIL")
        print(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
