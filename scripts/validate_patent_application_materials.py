#!/usr/bin/env python3
"""Validate generated patent application materials before official preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_filing_package_manifest
import validate_filing_status_transition


REQUIRED_GENERATED_TYPES = {
    "claims",
    "specification",
    "abstract",
    "drawings",
    "request_form_metadata",
    "xml_readiness_checklist",
}

REQUIRED_OFFICIAL_TYPES = {
    "claims",
    "specification",
    "abstract",
    "drawings",
    "request_metadata",
}

OFFICIAL_DOCUMENT_FIELDS = [
    "document_id",
    "type",
    "filename",
    "format",
    "hash",
    "required",
    "validation_status",
]

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
MISSING_SOURCE_SECTION_RE = re.compile(r"section not found in source draft\.", re.IGNORECASE)

REQUIRED_DOCUMENT_MARKERS = {
    "claims": ["## Claims Draft"],
    "specification": ["## Technical Problem", "## Technical Solution", "## Detailed Embodiments"],
    "abstract": ["## Abstract"],
    "drawings": ["## Brief Description Of Drawings"],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def require_hash_list(values: Any, label: str, errors: list[str], required: bool = False) -> None:
    if not isinstance(values, list) or not values:
        if required:
            errors.append(f"{label}_required")
        elif not is_blank(values):
            errors.append(f"{label}_must_be_list")
        return
    for index, value in enumerate(values):
        require_hash(value, f"{label}[{index}]", errors)


def require_positive_int(value: Any, label: str, errors: list[str]) -> None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        errors.append(f"{label}_must_be_positive_integer")
        return
    if parsed <= 0:
        errors.append(f"{label}_must_be_positive_integer")


def resolve_artifact(base_dir: Path, raw_path: Any) -> Path:
    path = Path(str(raw_path or ""))
    return path if path.is_absolute() else (base_dir / path).resolve()


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_internal_artifact(base_dir: Path, raw_path: Any, label: str, errors: list[str]) -> Path | None:
    if is_blank(raw_path):
        errors.append(f"{label}_missing_path")
        return None
    path = Path(str(raw_path))
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{label}_unsafe_path")
        return None
    resolved = (base_dir / path).resolve()
    if not is_relative_to(resolved, base_dir.resolve()):
        errors.append(f"{label}_path_outside_materials_root")
        return None
    return resolved


def validate_hash_reference(
    base_dir: Path,
    item: dict[str, Any],
    label: str,
    errors: list[str],
    hash_field_label: str | None = None,
) -> Path | None:
    raw_path = item.get("path")
    artifact_hash = item.get("hash") or item.get("artifact_hash")
    require_hash(artifact_hash, hash_field_label or f"{label}.hash", errors)
    path = resolve_internal_artifact(base_dir, raw_path, label, errors)
    if path is None:
        return None
    if not path.exists():
        errors.append(f"{label}_file_not_found: {path}")
        return None
    if artifact_hash and sha256_file(path) != artifact_hash:
        errors.append(f"{label}_hash_mismatch")
    return path


def validate_document_content(doc_type: str, path: Path | None, label: str, errors: list[str]) -> None:
    markers = REQUIRED_DOCUMENT_MARKERS.get(doc_type)
    if not markers or path is None or not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if MISSING_SOURCE_SECTION_RE.search(text):
        errors.append(f"{label}_{doc_type}_contains_missing_source_section_placeholder")
    for marker in markers:
        if marker not in text:
            errors.append(f"{label}_{doc_type}_missing_required_marker: {marker}")


def canonical_document_map(docs: Any, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(docs, list):
        return result
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        doc_type = str(doc.get("type") or "")
        if not doc_type:
            continue
        if doc_type in result:
            errors.append(f"{label}_duplicate_type: {doc_type}")
        result[doc_type] = {field: doc.get(field) for field in OFFICIAL_DOCUMENT_FIELDS}
    return result


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    base = base_dir.resolve() if base_dir else Path.cwd()

    for key in [
        "case_id",
        "status",
        "decision",
        "jurisdiction",
        "filing_type",
        "legal_gate_mode",
        "final_package_hash",
        "source_package",
        "evidence_provenance",
        "abnormal_filing_risk_assessment",
        "request_form_metadata",
        "document_materials",
        "document_generation_plan",
        "official_material_inventory",
        "xml_readiness",
        "safeguards",
    ]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")

    if data.get("status") != "application_materials_generated_official_preflight_pending":
        errors.append("status_must_be_application_materials_generated_official_preflight_pending")
    if data.get("decision") != "materials_generated_official_preflight_required":
        errors.append("decision_must_require_official_preflight")
    if data.get("legal_gate_mode") != "ai_self_filing_no_external_lawyer":
        errors.append("legal_gate_mode_must_be_ai_self_filing_no_external_lawyer")
    if data.get("external_lawyer_involved") is not False:
        errors.append("external_lawyer_involved_must_be_false")
    if data.get("official_system_touched") is not False:
        errors.append("official_system_touched_must_be_false")
    if data.get("official_submission_performed") is not False:
        errors.append("official_submission_performed_must_be_false")
    if data.get("filing_allowed") is not False:
        errors.append("filing_allowed_must_be_false_until_official_preflight")

    require_hash(data.get("final_package_hash"), "final_package_hash", errors)

    source_package = data.get("source_package") if isinstance(data.get("source_package"), dict) else {}
    if source_package.get("package_status") != "package_valid_official_preflight_pending":
        errors.append("source_package_status_must_be_package_valid_official_preflight_pending")
    source_manifest: dict[str, Any] = {}
    raw_package_dir = source_package.get("package_dir")
    if is_blank(raw_package_dir):
        errors.append("source_package_missing_package_dir")
    else:
        package_dir = resolve_artifact(base, raw_package_dir)
        if not package_dir.exists() or not package_dir.is_dir():
            errors.append(f"source_package_dir_not_found: {package_dir}")
        else:
            manifest_path = package_dir / "filing-package-manifest.yaml"
            if not manifest_path.exists():
                errors.append(f"source_package_manifest_not_found: {manifest_path}")
            else:
                if source_package.get("filing_package_manifest_hash") and sha256_file(manifest_path) != source_package.get("filing_package_manifest_hash"):
                    errors.append("source_package_manifest_hash_mismatch")
                try:
                    source_manifest = validate_filing_package_manifest.load_packet(manifest_path)
                    manifest_ok, manifest_errors, manifest_warnings = validate_filing_package_manifest.validate(
                        source_manifest,
                        base_dir=manifest_path.parent,
                    )
                    if not manifest_ok:
                        errors.extend([f"source_package_manifest: {item}" for item in manifest_errors])
                    warnings.extend([f"source_package_manifest: {item}" for item in manifest_warnings])
                except Exception as exc:
                    errors.append(f"source_package_manifest_read_failed: {exc}")
    for key in [
        "authorization_packet_hash",
        "filing_package_manifest_hash",
        "filing_status_hash",
        "source_draft_hash",
        "final_package_hash",
    ]:
        require_hash(source_package.get(key), f"source_package.{key}", errors)
    if source_package.get("final_package_hash") != data.get("final_package_hash"):
        errors.append("source_package_final_hash_mismatch")

    evidence = data.get("evidence_provenance") if isinstance(data.get("evidence_provenance"), dict) else {}
    validate_hash_reference(
        base,
        evidence,
        "evidence_provenance",
        errors,
        hash_field_label="evidence_provenance.artifact_hash",
    )
    for key in [
        "patent_application_draft_hash",
        "claim_support_map_hash",
        "source_material_manifest_hash",
    ]:
        require_hash(evidence.get(key), f"evidence_provenance.{key}", errors)
    if evidence.get("case_id") != data.get("case_id"):
        errors.append("evidence_provenance_case_id_mismatch")
    if evidence.get("patent_application_draft_hash") != source_package.get("source_draft_hash"):
        errors.append("evidence_provenance_draft_hash_mismatch")
    if evidence.get("no_reference_or_prior_art_used_as_claim_support") is not True:
        errors.append("evidence_provenance_must_block_reference_as_support")
    require_hash_list(evidence.get("own_support_hashes"), "evidence_provenance.own_support_hashes", errors, required=True)
    require_hash_list(evidence.get("prohibited_reference_hashes"), "evidence_provenance.prohibited_reference_hashes", errors)
    if int(evidence.get("claim_support_rows_count") or 0) <= 0:
        errors.append("evidence_provenance_claim_support_rows_required")
    evidence_ref_hash = evidence.get("reference_patent_delta_hash")
    if evidence_ref_hash:
        require_hash(evidence_ref_hash, "evidence_provenance.reference_patent_delta_hash", errors)
        require_positive_int(evidence.get("reference_delta_rows_count"), "evidence_provenance.reference_delta_rows_count", errors)
        require_positive_int(
            evidence.get("reference_delta_claim_elements_count"),
            "evidence_provenance.reference_delta_claim_elements_count",
            errors,
        )

    abnormal = data.get("abnormal_filing_risk_assessment") if isinstance(data.get("abnormal_filing_risk_assessment"), dict) else {}
    validate_hash_reference(
        base,
        abnormal,
        "abnormal_filing_risk_assessment",
        errors,
        hash_field_label="abnormal_filing_risk_assessment.artifact_hash",
    )
    if abnormal.get("case_id") != data.get("case_id"):
        errors.append("abnormal_filing_risk_assessment_case_id_mismatch")
    if abnormal.get("risk_level") != "low":
        errors.append("abnormal_filing_risk_assessment_risk_level_must_be_low")
    abnormal_ref_hash = abnormal.get("reference_patent_delta_hash")
    if abnormal_ref_hash:
        require_hash(abnormal_ref_hash, "abnormal_filing_risk_assessment.reference_patent_delta_hash", errors)
        require_positive_int(
            abnormal.get("reference_delta_rows_count"),
            "abnormal_filing_risk_assessment.reference_delta_rows_count",
            errors,
        )
        require_positive_int(
            abnormal.get("reference_delta_claim_elements_count"),
            "abnormal_filing_risk_assessment.reference_delta_claim_elements_count",
            errors,
        )
        if abnormal.get("reference_delta_boundary_preserved") is not True:
            errors.append("abnormal_filing_risk_assessment_reference_delta_boundary_must_be_true")
    if evidence_ref_hash or abnormal_ref_hash:
        if evidence_ref_hash != abnormal_ref_hash:
            errors.append("reference_patent_delta_hash_mismatch_between_provenance_and_abnormal_risk")
        for key in ["reference_delta_rows_count", "reference_delta_claim_elements_count"]:
            if evidence.get(key) != abnormal.get(key):
                errors.append(f"{key}_mismatch_between_provenance_and_abnormal_risk")

    request_metadata = data.get("request_form_metadata") if isinstance(data.get("request_form_metadata"), dict) else {}
    validate_hash_reference(base, request_metadata, "request_form_metadata", errors)
    for key in ["applicant_name", "inventors", "fee_payer", "secrecy_review_status", "official_system"]:
        if is_blank(request_metadata.get(key)):
            errors.append(f"request_form_metadata_missing_required_field: {key}")
    if request_metadata.get("external_lawyer_involved") is not False:
        errors.append("request_form_metadata_external_lawyer_involved_must_be_false")
    if request_metadata.get("lawyer_or_agent_review_claimed") is not False:
        errors.append("request_form_metadata_must_not_claim_lawyer_or_agent_review")

    generation_plan = data.get("document_generation_plan") if isinstance(data.get("document_generation_plan"), dict) else {}
    validate_hash_reference(base, generation_plan, "document_generation_plan", errors)

    generated_types: set[str] = set()
    documents = data.get("document_materials")
    if not isinstance(documents, list) or not documents:
        errors.append("document_materials_must_be_nonempty_list")
    else:
        for index, doc in enumerate(documents, start=1):
            if not isinstance(doc, dict):
                errors.append(f"document_material_{index}_must_be_object")
                continue
            doc_type = str(doc.get("type") or "")
            generated_types.add(doc_type)
            for key in ["type", "path", "hash", "format", "validation_status"]:
                if is_blank(doc.get(key)):
                    errors.append(f"document_material_{index}_missing_required_field: {key}")
            if doc.get("required") is not True:
                errors.append(f"document_material_{index}_must_be_required")
            if doc.get("validation_status") != "generated_and_source_bound":
                errors.append(f"document_material_{index}_validation_status_invalid")
            material_path = validate_hash_reference(base, doc, f"document_material_{index}", errors)
            validate_document_content(doc_type, material_path, f"document_material_{index}", errors)

    for doc_type in sorted(REQUIRED_GENERATED_TYPES - generated_types):
        errors.append(f"missing_generated_material_type: {doc_type}")

    official_types: set[str] = set()
    official_docs = data.get("official_material_inventory")
    if not isinstance(official_docs, list) or not official_docs:
        errors.append("official_material_inventory_must_be_nonempty_list")
    else:
        for index, doc in enumerate(official_docs, start=1):
            if not isinstance(doc, dict):
                errors.append(f"official_material_{index}_must_be_object")
                continue
            doc_type = str(doc.get("type") or "")
            official_types.add(doc_type)
            for key in ["document_id", "type", "filename", "format"]:
                if is_blank(doc.get(key)):
                    errors.append(f"official_material_{index}_missing_required_field: {key}")
            require_hash(doc.get("hash"), f"official_material_{index}.hash", errors)
            if doc.get("required") is not True:
                errors.append(f"official_material_{index}_must_be_required")
            if doc.get("validation_status") != "passed":
                errors.append(f"official_material_{index}_validation_status_must_be_passed")

    for doc_type in sorted(REQUIRED_OFFICIAL_TYPES - official_types):
        errors.append(f"missing_official_material_type: {doc_type}")

    source_docs = source_manifest.get("documents") if isinstance(source_manifest, dict) else []
    if source_docs:
        official_map = canonical_document_map(official_docs, "official_material", errors)
        source_map = canonical_document_map(source_docs, "source_package_manifest_document", errors)
        if official_map and source_map and official_map != source_map:
            errors.append("official_material_inventory_source_manifest_mismatch")

    xml = data.get("xml_readiness") if isinstance(data.get("xml_readiness"), dict) else {}
    validate_hash_reference(base, xml, "xml_readiness", errors)
    require_hash(xml.get("final_xml_hash"), "xml_readiness.final_xml_hash", errors)
    if not is_blank(xml.get("validation_report_hash")):
        require_hash(xml.get("validation_report_hash"), "xml_readiness.validation_report_hash", errors)
    if xml.get("xml_required") is not True:
        errors.append("xml_readiness_xml_required_must_be_true")
    if xml.get("validation_result") != "passed":
        errors.append("xml_readiness_validation_result_must_be_passed")
    if xml.get("official_channel_preflight_required") is not True:
        errors.append("xml_readiness_official_channel_preflight_required_must_be_true")

    safeguards = data.get("safeguards") if isinstance(data.get("safeguards"), dict) else {}
    for key in [
        "no_legal_advice_claimed",
        "no_lawyer_or_agent_review_claimed",
        "no_official_submission_claimed",
        "no_receipt_claimed",
        "no_application_number_claimed",
        "external_lawyer_absent",
    ]:
        if safeguards.get(key) is not True:
            errors.append(f"safeguard_missing_or_false: {key}")
    if safeguards.get("official_system_touched") is not False:
        errors.append("safeguards_official_system_touched_must_be_false")
    if safeguards.get("official_submission_performed") is not False:
        errors.append("safeguards_official_submission_performed_must_be_false")

    baseline = data.get("cnipa_material_baseline") if isinstance(data.get("cnipa_material_baseline"), dict) else {}
    if not baseline.get("official_reference_urls"):
        warnings.append("cnipa_material_baseline_official_reference_urls_missing")

    filing_status_ref = data.get("filing_status") if isinstance(data.get("filing_status"), dict) else {}
    if filing_status_ref:
        status_path = validate_hash_reference(base, filing_status_ref, "filing_status", errors)
        if status_path and status_path.exists():
            ok, errs, warns = validate_filing_status_transition.validate(load_json(status_path))
            if not ok:
                errors.extend([f"filing_status: {item}" for item in errs])
            warnings.extend([f"filing_status: {item}" for item in warns])

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("materials", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        path = args.materials.resolve()
        ok, errors, warnings = validate(load_json(path), path.parent)
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
