#!/usr/bin/env python3
"""Generate draft-only patent application artifacts from a confirmed disclosure."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_claim_support_map
import validate_filing_status_transition
import validate_invention_disclosure
import validate_patent_application_draft
import validate_reference_patent_delta


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def rel_any(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def copy_reference_delta_support_files(reference_delta: dict[str, Any], source_base: Path, output_root: Path) -> list[Path]:
    copied: list[Path] = []
    seen: set[Path] = set()
    for element in as_list(reference_delta.get("claim_elements")):
        if not isinstance(element, dict):
            continue
        raw_path = str(element.get("support_path") or "")
        if not raw_path:
            continue
        path = Path(raw_path)
        if path.is_absolute() or ".." in path.parts:
            continue
        source_path = (source_base / path).resolve()
        target_path = (output_root / path).resolve()
        if not source_path.exists() or not source_path.is_file():
            continue
        if target_path in seen:
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path != target_path:
            target_path.write_bytes(source_path.read_bytes())
        copied.append(target_path)
        seen.add(target_path)
    return copied


def clean(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def first_hash(disclosure: dict[str, Any]) -> str:
    evidence = disclosure.get("data_and_evidence", {})
    if isinstance(evidence, dict):
        for key in ["logs_or_measurements", "source_hashes"]:
            values = evidence.get(key)
            if isinstance(values, list):
                for item in values:
                    text = str(item)
                    if text.startswith("sha256:"):
                        return text
    return sha256_text(json.dumps(disclosure, ensure_ascii=False, sort_keys=True))


def render_prior_art_table(disclosure: dict[str, Any]) -> list[str]:
    rows = ["| Reference | Relevance | Claim risk |", "| --- | --- | --- |"]
    prior_art = as_list(disclosure.get("known_prior_art"))
    if not prior_art:
        rows.append("| Prior art pending | Closest references require AI legal/compliance prior-art diligence | Unknown |")
        return rows
    for item in prior_art:
        if not isinstance(item, dict):
            continue
        publication = clean(item.get("publication"), "Reference pending")
        relevance = clean(item.get("relevance"), "Relevance pending")
        rows.append(f"| {publication} | {relevance} | Requires element-level review |")
    return rows


def render_effect_table(disclosure: dict[str, Any]) -> list[str]:
    rows = ["| Effect | Evidence | Source material ID | Confidence |", "| --- | --- | --- | --- |"]
    for index, item in enumerate(as_list(disclosure.get("technical_effects")), start=1):
        if not isinstance(item, dict):
            continue
        rows.append(
            f"| {clean(item.get('effect'), 'Effect pending')} | "
            f"{clean(item.get('evidence'), 'Evidence pending')} | E-{index:03d} | draft |"
        )
    if len(rows) == 2:
        rows.append("| Technical effect pending | Evidence mapping required | E-000 | blocked |")
    return rows


def render_drawing_table(disclosure: dict[str, Any]) -> list[str]:
    rows = ["| Figure | Description | Required for claim support? |", "| --- | --- | --- |"]
    drawings = as_list(disclosure.get("drawings_needed"))
    if not drawings:
        drawings = ["System architecture", "Control flow", "Embodiment details"]
    for index, drawing in enumerate(drawings, start=1):
        rows.append(f"| Fig. {index} | {clean(drawing, 'Drawing pending')} | yes |")
    return rows


def render_numbered(items: list[Any], fallback: str) -> list[str]:
    values = [clean(item) for item in items if clean(item)]
    if not values:
        values = [fallback]
    return [f"{index}. {value}" for index, value in enumerate(values, start=1)]


def reference_delta_rows(reference_delta: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(reference_delta, dict):
        return []
    rows = reference_delta.get("delta_rows")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def reference_delta_elements(reference_delta: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(reference_delta, dict):
        return []
    elements = reference_delta.get("claim_elements")
    return [item for item in elements if isinstance(item, dict)] if isinstance(elements, list) else []


def supported_claim_features(disclosure: dict[str, Any], reference_delta: dict[str, Any] | None = None) -> list[str]:
    elements = reference_delta_elements(reference_delta)
    if elements:
        return [clean(item.get("text")) for item in elements if clean(item.get("text"))]
    return [clean(item) for item in as_list(disclosure.get("technical_solution", {}).get("required_features")) if clean(item)]


def main_claim(disclosure: dict[str, Any], reference_delta: dict[str, Any] | None = None) -> str:
    features = supported_claim_features(disclosure, reference_delta)
    title = clean(disclosure.get("title"), "the invention")
    if not features:
        return f"1. A method for implementing {title}, comprising confirmed technical features set out in the invention disclosure."
    clauses = "; ".join(clean(feature).rstrip(".") for feature in features if clean(feature))
    return f"1. A technical method for {title}, comprising: {clauses}."


def dependent_claims(disclosure: dict[str, Any], reference_delta: dict[str, Any] | None = None) -> list[str]:
    optional = as_list(disclosure.get("technical_solution", {}).get("optional_features"))
    embodiments = as_list(disclosure.get("embodiments"))
    claims: list[str] = []
    next_no = 2
    for row in reference_delta_rows(reference_delta)[:4]:
        fallback = clean(row.get("fallback_position"))
        if fallback:
            claims.append(f"{next_no}. The method of claim 1, wherein {fallback.rstrip('.')}.")
            next_no += 1
    for feature in optional[:4]:
        claims.append(f"{next_no}. The method of claim 1, wherein {clean(feature).rstrip('.')}.")
        next_no += 1
    for embodiment in embodiments[:2]:
        if isinstance(embodiment, dict):
            components = [clean(item) for item in as_list(embodiment.get("components")) if clean(item)]
            if components:
                claims.append(f"{next_no}. A system comprising {', '.join(components)}, configured to perform the method of claim 1.")
                next_no += 1
    if not claims:
        claims.append("2. The method of claim 1, wherein at least one implementation parameter is selected according to confirmed embodiment evidence.")
    return claims


def render_embodiments(disclosure: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    embodiments = as_list(disclosure.get("embodiments"))
    if not embodiments:
        embodiments = [{"name": "Embodiment 1", "implementation_steps": ["Implement the confirmed required features."]}]
    for index, embodiment in enumerate(embodiments, start=1):
        if not isinstance(embodiment, dict):
            continue
        lines.extend([f"### Embodiment {index}", "", "Components:", ""])
        for item in as_list(embodiment.get("components")) or ["Components pending final drawing confirmation."]:
            lines.append(f"- {clean(item)}")
        lines.extend(["", "Steps:", ""])
        lines.extend(render_numbered(as_list(embodiment.get("implementation_steps")), "Implement the confirmed required features."))
        lines.extend(["", "Parameters:", ""])
        for item in as_list(embodiment.get("parameters")) or ["Parameter ranges require inventor and AI legal/compliance confirmation before filing readiness."]:
            lines.append(f"- {clean(item)}")
        lines.extend(
            [
                "",
                "Alternatives:",
                "",
                "- Equivalent components or control sequences may be used only if supported by the confirmed disclosure.",
                "",
                "Failure handling:",
                "",
                "- Features lacking evidence must be removed, narrowed, or escalated to the AI legal/compliance gate before filing readiness.",
                "",
            ]
        )
    return lines


def render_reference_delta_strategy(reference_delta: dict[str, Any] | None) -> list[str]:
    rows = reference_delta_rows(reference_delta)
    if not rows:
        return [
            "Reference-patent delta: not supplied.",
            "",
            "Cited patents remain prior-art context only and must not be used as applicant claim support.",
        ]
    lines = [
        f"Reference delta status: {reference_delta.get('status')}",
        "Reference patents are boundary evidence only and do not supply applicant claim support.",
        "",
        "| Element | Known In Prior Art | Distinguishing Feature | Claim Strategy | Fallback |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    clean(row.get("element_id")),
                    clean(row.get("known_in_prior_art")),
                    clean(row.get("applicant_distinguishing_feature")),
                    clean(row.get("claim_strategy")),
                    clean(row.get("fallback_position")),
                ]
            )
            + " |"
        )
    return lines


def render_draft(
    disclosure: dict[str, Any],
    disclosure_hash: str,
    manifest_ref: str,
    version: str,
    reference_delta: dict[str, Any] | None = None,
) -> str:
    required = supported_claim_features(disclosure, reference_delta)
    optional = as_list(disclosure.get("technical_solution", {}).get("optional_features"))
    abstract_features = "; ".join(clean(item).rstrip(".") for item in required[:3] if clean(item))
    if not abstract_features:
        abstract_features = clean(disclosure.get("technical_problem"), "the confirmed technical solution")
    lines = [
        "# Patent Application Draft",
        "",
        f"Case ID: {disclosure.get('case_id')}  ",
        f"Draft version: {version}  ",
        f"Source material manifest: {manifest_ref}  ",
        f"Disclosure hash: {disclosure_hash}  ",
        "Draft status: ai_self_filing_authorization_needed",
        "",
        "## Title",
        "",
        clean(disclosure.get("title"), "Confirmed invention draft") + ".",
        "",
        "## Technical Field",
        "",
        "The draft relates to the technical field reflected in the confirmed invention disclosure, including the disclosed apparatus, method, control logic, data processing, and implementation embodiments.",
        "",
        "## Background",
        "",
        "Known references and products may disclose parts of the field. This draft uses them only as prior-art context and does not copy claims, wording, or effects not backed by evidence.",
        "",
        "Closest known references:",
        "",
        *render_prior_art_table(disclosure),
        "",
        "## Technical Problem",
        "",
        clean(disclosure.get("technical_problem"), "The technical problem requires inventor and AI legal/compliance confirmation."),
        "",
        "## Technical Solution",
        "",
        "Required features:",
        "",
        *render_numbered(required, "Confirmed required feature pending final AI legal/compliance wording."),
        "",
        "Optional features:",
        "",
        *render_numbered(optional, "Optional fallback features require AI legal/compliance selection."),
        "",
        "## Reference Patent Delta Strategy",
        "",
        *render_reference_delta_strategy(reference_delta),
        "",
        "## Beneficial Technical Effects",
        "",
        *render_effect_table(disclosure),
        "",
        "## Brief Description Of Drawings",
        "",
        *render_drawing_table(disclosure),
        "",
        "## Detailed Embodiments",
        "",
        *render_embodiments(disclosure),
        "## Claims Draft",
        "",
        "### Independent Claim Candidates",
        "",
        main_claim(disclosure, reference_delta),
        "",
        "### Dependent Claim Ladder",
        "",
        *dependent_claims(disclosure, reference_delta),
        "",
        "## Abstract",
        "",
        f"A technical solution is disclosed for {clean(disclosure.get('title'), 'the confirmed invention')}. The solution includes {abstract_features}. The draft is generated only from confirmed disclosure facts and remains subject to AI self-filing legal/compliance authorization.",
        "",
        "## Claim Support Map Link",
        "",
        "See claim-support-map.md for limitation-level support and evidence hashes.",
        "",
        "## AI Legal/Compliance Questions",
        "",
    ]
    questions = (
        as_list(disclosure.get("ai_legal_compliance_questions"))
        or ["Confirm claim breadth, terminology, and filing strategy before AI self-filing package validation."]
    )
    lines.extend([f"- {clean(question)}" for question in questions])
    lines.extend(
        [
            "",
            "## Filing Gate",
            "",
            "Do not file this draft. The legal gate for filing has not passed because final AI self-filing legal/compliance authorization, applicant filing authorization, final package hash, fee authority, and official-channel preflight are not validated.",
            "",
        ]
    )
    return "\n".join(lines)


def render_claim_support_map(
    disclosure: dict[str, Any],
    disclosure_hash: str,
    version: str,
    reference_delta: dict[str, Any] | None = None,
) -> str:
    features = supported_claim_features(disclosure, reference_delta)
    elements = reference_delta_elements(reference_delta)
    rows_by_element = {clean(row.get("element_id")): row for row in reference_delta_rows(reference_delta)}
    effects = as_list(disclosure.get("technical_effects"))
    effect_text = clean(effects[0].get("effect") if effects and isinstance(effects[0], dict) else "", "Technical effect pending final AI legal/compliance wording")
    evidence_hash = first_hash(disclosure)
    rows = [
        "# Claim Support Map",
        "",
        f"Case ID: {disclosure.get('case_id')}  ",
        f"Version: {version}  ",
        f"Source package hash: {disclosure_hash}  ",
        "Reviewer: Patent Capital OS draft generator  ",
        f"Review timestamp: {build_case_queue.utc_plus_8_now()}  ",
        "Gate status: draft",
        "",
        "## Claim Map",
        "",
        "| Claim | Limitation | Required? | Disclosure support | Figure / embodiment | Prior-art delta | Technical effect | Fallback position | Evidence hash | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not features:
        features = ["Confirmed required feature pending AI legal/compliance wording."]
    for index, feature in enumerate(features, start=1):
        element_id = clean(elements[index - 1].get("element_id")) if index - 1 < len(elements) else ""
        delta = rows_by_element.get(element_id, {})
        prior_art_delta = clean(delta.get("applicant_distinguishing_feature"), "Requires full prior-art element comparison before filing.")
        technical_effect = clean(delta.get("technical_effect_evidence"), effect_text)
        fallback = clean(delta.get("fallback_position"), "Narrow to embodiment-supported wording if needed.")
        rows.append(
            f"| 1 | {clean(feature).rstrip('.')} | yes | Confirmed invention disclosure required feature {index}. | "
            f"Fig. {min(index, 5)} / Embodiment 1 | {prior_art_delta} | "
            f"{technical_effect} | {fallback} | {evidence_hash} | draft_supported |"
        )
    rows.extend(
        [
            "",
            "## Readiness Rules",
            "",
            "- This support map is adequate for draft-only AI self-filing legal/compliance authorization.",
            "- Full source evidence, final drawings, and prior-art claim comparison remain required before filing readiness.",
            "- Filing is blocked until legal authorization and official-channel preflight pass.",
            "",
            "## Reviewer Decision",
            "",
            "Decision: revise",
            "",
            "Required revisions:",
            "",
            "- Confirm claim breadth through the AI legal/compliance gate.",
            "- Replace draft wording with package-bound claim language validated by the AI self-filing authorization packet.",
            "- Validate final filing package hashes before official-channel preflight.",
            "",
            "Approval evidence:",
            "",
            "- None. Draft-only generation package.",
            "",
        ]
    )
    return "\n".join(rows)


def render_report(
    case_id: str,
    disclosure_hash: str,
    draft_ok: bool,
    claim_ok: bool,
    warnings: list[str],
    reference_delta: dict[str, Any] | None = None,
) -> str:
    lines = [
        "# Draft Package Generation Report",
        "",
        f"Case ID: {case_id}",
        f"Disclosure hash: {disclosure_hash}",
        f"Patent draft validation: {'pass' if draft_ok else 'fail'}",
        f"Claim support map validation: {'pass' if claim_ok else 'fail'}",
        "Draft generation allowed: yes",
        "Filing allowed: no",
        "Legal gate for filing: failed",
        "Official system touched: no",
        "Official submission performed: no",
        f"Reference patent delta used: {'yes' if reference_delta else 'no'}",
        "",
        "## Boundary",
        "",
        "This package is for AI self-filing legal/compliance authorization preparation and drafting only. It is not a filing package, official-channel preflight, submission, receipt, or application-number record.",
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


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


def generate(
    disclosure_path: Path,
    output_dir: Path,
    source_manifest: str = "invention-disclosure.json",
    reference_delta_path: Path | None = None,
) -> tuple[dict[str, Any], int]:
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    disclosure = load_json(disclosure_path)
    disclosure_hash = sha256_file(disclosure_path)
    disclosure_ok, disclosure_errors, disclosure_warnings = validate_invention_disclosure.validate(disclosure)
    if not disclosure_ok:
        return {
            "ok": False,
            "case_id": disclosure.get("case_id"),
            "output_dir": str(output_root),
            "disclosure_errors": disclosure_errors,
            "disclosure_warnings": disclosure_warnings,
            "draft_generation_allowed": False,
            "filing_allowed": False,
            "external_lawyer_involved": False,
            "official_system_touched": False,
            "official_submission_performed": False,
        }, 1

    case_id = str(disclosure.get("case_id") or "")
    version = "draft-package-" + build_case_queue.utc_plus_8_now().replace(":", "").replace("+", "plus")
    disclosure_copy_path = output_root / "invention-disclosure.json"
    draft_path = output_root / "patent-application-draft.md"
    claim_map_path = output_root / "claim-support-map.md"
    status_path = output_root / "filing-status.json"
    report_path = output_root / "draft-package-report.md"
    artifact_path = output_root / "artifact-hashes.json"
    reference_delta_copy_path = output_root / "reference-patent-delta.json"

    reference_delta: dict[str, Any] | None = None
    reference_delta_errors: list[str] = []
    reference_delta_warnings: list[str] = []
    copied_reference_delta_files: list[Path] = []
    if reference_delta_path:
        reference_delta_path = reference_delta_path.resolve()
        reference_delta = load_json(reference_delta_path)
        delta_ok, reference_delta_errors, reference_delta_warnings = validate_reference_patent_delta.validate(
            reference_delta,
            reference_delta_path.parent,
        )
        if not delta_ok:
            return {
                "ok": False,
                "case_id": case_id,
                "output_dir": str(output_root),
                "reference_delta_errors": reference_delta_errors,
                "reference_delta_warnings": reference_delta_warnings,
                "draft_generation_allowed": False,
                "filing_allowed": False,
                "external_lawyer_involved": False,
                "official_system_touched": False,
                "official_submission_performed": False,
            }, 1
        if reference_delta.get("case_id") != case_id:
            return {
                "ok": False,
                "case_id": case_id,
                "output_dir": str(output_root),
                "reference_delta_errors": ["reference_delta_case_id_must_match_disclosure_case_id"],
                "reference_delta_warnings": reference_delta_warnings,
                "draft_generation_allowed": False,
                "filing_allowed": False,
                "external_lawyer_involved": False,
                "official_system_touched": False,
                "official_submission_performed": False,
            }, 1

    write_json(disclosure_copy_path, disclosure)
    if reference_delta_path:
        if reference_delta_path != reference_delta_copy_path.resolve():
            delta_for_output = json.loads(json.dumps(reference_delta, ensure_ascii=False))
            source_input = delta_for_output.get("source_input") if isinstance(delta_for_output.get("source_input"), dict) else {}
            if source_input.get("path"):
                raw_source_path = Path(str(source_input.get("path")))
                original_source_path = raw_source_path if raw_source_path.is_absolute() else (reference_delta_path.parent / raw_source_path).resolve()
                source_input["path"] = rel_any(original_source_path, output_root)
            write_json(reference_delta_copy_path, delta_for_output)
            reference_delta = delta_for_output
        if reference_delta:
            copied_reference_delta_files = copy_reference_delta_support_files(reference_delta, reference_delta_path.parent, output_root)
    draft_path.write_text(render_draft(disclosure, disclosure_hash, source_manifest, version, reference_delta), encoding="utf-8")
    claim_map_path.write_text(render_claim_support_map(disclosure, disclosure_hash, version, reference_delta), encoding="utf-8")
    filing_status = {
        "case_id": case_id,
        "status": "draft_only",
        "legal_gate": "failed",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "failed_gates": [
            "G1 final_ai_self_filing_legal_compliance_authorization_absent",
            "G2 applicant_filing_authorization_absent",
            "G6 agency_and_signature_authority_absent",
            "G7 fee_authority_absent",
            "G9 official_channel_preflight_absent",
        ],
        "decision": "do_not_file",
        "draft_generation_allowed": True,
        "filing_allowed": False,
        "external_lawyer_involved": False,
        "final_package_hash": "",
        "reviewed_package_hash": "",
        "official_receipt_hash": "",
        "application_number": "",
        "official_system_touched": False,
        "official_submission_performed": False,
        "updated_at": build_case_queue.utc_plus_8_now(),
    }
    write_json(status_path, filing_status)

    draft_ok, draft_errors, draft_warnings = validate_patent_application_draft.validate(draft_path)
    claim_ok, claim_errors, claim_warnings = validate_claim_support_map.validate(claim_map_path, allow_draft=True)
    status_ok, status_errors, status_warnings = validate_filing_status_transition.validate(filing_status)
    report_path.write_text(
        render_report(
            case_id,
            disclosure_hash,
            draft_ok,
            claim_ok,
            draft_warnings + claim_warnings + status_warnings + reference_delta_warnings,
            reference_delta,
        ),
        encoding="utf-8",
    )
    manifest_files = [disclosure_copy_path, draft_path, claim_map_path, status_path, report_path]
    if reference_delta_path:
        manifest_files.append(reference_delta_copy_path)
        manifest_files.extend(copied_reference_delta_files)
    manifest = artifact_manifest(output_root, case_id, manifest_files)
    write_json(artifact_path, manifest)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(artifact_path)

    ok = draft_ok and claim_ok and status_ok and hash_ok
    response = {
        "ok": ok,
        "case_id": case_id,
        "output_dir": str(output_root),
        "artifacts": {
            "patent_application_draft": str(draft_path),
            "invention_disclosure": str(disclosure_copy_path),
            "claim_support_map": str(claim_map_path),
            "filing_status": str(status_path),
            "draft_package_report": str(report_path),
            "artifact_hashes": str(artifact_path),
            **({"reference_patent_delta": str(reference_delta_copy_path)} if reference_delta_path else {}),
        },
        "disclosure_hash": disclosure_hash,
        "disclosure_errors": disclosure_errors,
        "disclosure_warnings": disclosure_warnings,
        "draft_errors": draft_errors,
        "draft_warnings": draft_warnings,
        "claim_errors": claim_errors,
        "claim_warnings": claim_warnings,
        "status_errors": status_errors,
        "status_warnings": status_warnings,
        "reference_delta_errors": reference_delta_errors,
        "reference_delta_warnings": reference_delta_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "draft_generation_allowed": True,
        "filing_allowed": False,
        "external_lawyer_involved": False,
        "official_system_touched": False,
        "official_submission_performed": False,
    }
    return response, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("invention_disclosure", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source-manifest", default="invention-disclosure.json")
    parser.add_argument("--reference-delta", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = generate(args.invention_disclosure, args.output_dir, args.source_manifest, args.reference_delta)
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "draft_generation_allowed": False,
            "filing_allowed": False,
            "external_lawyer_involved": False,
            "official_system_touched": False,
            "official_submission_performed": False,
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
