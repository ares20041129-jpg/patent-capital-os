#!/usr/bin/env python3
"""Prepare an abnormal filing risk assessment for a draft patent package."""

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
import validate_draft_evidence_provenance
import validate_filing_status_transition
import validate_invention_disclosure
import validate_patent_application_draft
import validate_reference_patent_delta
import validate_source_material_manifest


SHA_RE = re.compile(r"sha256:[0-9a-f]{64}")
SHA256_FULL_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
RANDOM_OR_COPY_PATTERNS = [
    "random computer generation",
    "randomly generated",
    "generate many",
    "bulk generated",
    "copy and rewrite",
    "simple replacement",
    "simply replaced",
    "synonym substitution",
    "fabricated technical effect",
    "fabricated data",
]
BATCH_PATTERNS = [
    "batch filing",
    "batch filings",
    "mass filing",
    "maliciously distributed",
    "many patent applications",
    "portfolio spam",
    "duplicate filing",
]
DEGRADATION_PATTERNS = [
    "unreasonable degradation",
    "non-necessary narrowing",
    "worse performance",
    "narrow only",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def copy_file(source: Path, target: Path) -> None:
    if source.resolve() == target.resolve():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


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


def contains_any(text: str, patterns: list[str]) -> list[str]:
    lower = text.lower()
    return [pattern for pattern in patterns if pattern in lower]


def disclosure_text(disclosure: dict[str, Any]) -> str:
    parts = [
        disclosure.get("title"),
        disclosure.get("business_goal"),
        get_path(disclosure, "applicant_context.actual_r_and_d_basis"),
        get_path(disclosure, "similarity_control.real_technical_contribution_summary"),
        disclosure.get("technical_problem"),
    ]
    return "\n".join(str(part) for part in parts if part)


def parse_claim_rows(claim_map_path: Path) -> list[dict[str, str]]:
    _, rows = validate_claim_support_map.parse_tables(claim_map_path.read_text(encoding="utf-8", errors="replace"))
    return rows


def feature_complexity(features: list[Any], claim_rows: list[dict[str, str]]) -> int:
    text = " ".join(str(item) for item in features)
    if not text:
        text = " ".join(str(row.get("Limitation") or "") for row in claim_rows)
    connectors = [" and ", ",", ";", " plus ", " with ", " using "]
    score = len([item for item in features if str(item).strip()])
    score += sum(text.lower().count(connector) for connector in connectors)
    return score


def check_row(
    check_id: str,
    result: str,
    evidence: str,
    risk_if_ignored: str,
    required_cure: str,
    owner: str = "Patent Capital OS abnormal filing risk gate",
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "result": result,
        "evidence": evidence,
        "risk_if_ignored": risk_if_ignored,
        "required_cure": required_cure,
        "owner": owner,
    }


def source_material_hashes(manifest: dict[str, Any]) -> tuple[set[str], set[str]]:
    own_hashes: set[str] = set()
    prior_hashes: set[str] = set()
    for material in as_list(manifest.get("materials")):
        if not isinstance(material, dict):
            continue
        material_hash = str(material.get("hash") or "")
        if not SHA256_FULL_RE.fullmatch(material_hash):
            continue
        material_type = str(material.get("type") or "").lower()
        is_prior = "prior" in material_type or material.get("confidentiality") == "public"
        if is_prior:
            prior_hashes.add(material_hash)
        elif material.get("usable_for_claim_support") is True:
            own_hashes.add(material_hash)
    return own_hashes, prior_hashes


def resolve_material_path(base_dir: Path, raw_path: Any) -> Path:
    return validate_source_material_manifest.resolve_material_path(base_dir, raw_path)


def copy_manifest_material_files(manifest: dict[str, Any], input_root: Path, output_root: Path) -> list[Path]:
    copied: list[Path] = []
    for item in as_list(manifest.get("materials")):
        if not isinstance(item, dict) or not item.get("filename"):
            continue
        raw_filename = str(item["filename"])
        try:
            source = resolve_material_path(input_root, raw_filename)
        except ValueError:
            continue
        if not source.exists() or not source.is_file():
            continue
        target = output_root / raw_filename
        copy_file(source, target)
        copied.append(target)
    return copied


def copy_reference_delta_support_files(reference_delta: dict[str, Any], input_root: Path, output_root: Path) -> list[Path]:
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
        source = (input_root / path).resolve()
        if not source.exists() or not source.is_file():
            continue
        target = output_root / path
        copy_file(source, target)
        copied.append(target)
    return copied


def build_assessment(
    disclosure: dict[str, Any],
    manifest: dict[str, Any],
    provenance: dict[str, Any],
    claim_rows: list[dict[str, str]],
    validation_errors: list[str],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    own_hashes, prior_hashes = source_material_hashes(manifest)
    disclosure_hashes = collect_sha256(disclosure)
    own_support_hashes = set(provenance.get("own_support_hashes") or []) or own_hashes

    prototypes = get_path(disclosure, "data_and_evidence.prototypes")
    experiments = get_path(disclosure, "data_and_evidence.experiments")
    logs = get_path(disclosure, "data_and_evidence.logs_or_measurements")
    source_hashes = get_path(disclosure, "data_and_evidence.source_hashes")
    inventor_confirmed = get_path(disclosure, "inventor_input.contribution_confirmed") is True
    has_r_and_d_evidence = not is_blank(prototypes) or not is_blank(experiments) or not is_blank(logs)
    if inventor_confirmed and has_r_and_d_evidence and not is_blank(source_hashes):
        checks.append(
            check_row(
                "real_inventive_activity",
                "pass",
                "Inventor contribution is confirmed and R&D evidence includes prototype, experiment, log, or source hashes.",
                "A filing without real inventive activity can be treated as abnormal and should not proceed.",
                "Collect inventor contribution confirmation and real R&D evidence before draft generation or filing.",
            )
        )
    else:
        checks.append(
            check_row(
                "real_inventive_activity",
                "fail",
                "Inventor confirmation, R&D evidence, or source hashes are missing.",
                "The case may be a fabricated or unsupported invention.",
                "Supply inventor-confirmed technical contribution and source evidence hashes.",
            )
        )

    suspicious_generation = contains_any(disclosure_text(disclosure), RANDOM_OR_COPY_PATTERNS)
    checks.append(
        check_row(
            "no_random_generation",
            "fail" if suspicious_generation else "pass",
            "Suspicious generation markers: " + ", ".join(suspicious_generation) if suspicious_generation else "No random-generation, simple-replacement, or synonym-substitution marker was found in core disclosure fields.",
            "Random computer generation, fabricated effects, or simple wording changes can make the filing abnormal.",
            "Replace generated or wording-only material with real technical contribution evidence and inventor confirmation.",
        )
    )

    provenance_rows = as_list(provenance.get("claim_support_rows"))
    unsupported_rows = as_list(provenance.get("unsupported_rows"))
    prior_support_rows = [
        row for row in provenance_rows if isinstance(row, dict) and row.get("evidence_role") == "reference_or_prior_art"
    ]
    no_copying_confirmed = get_path(disclosure, "similarity_control.no_copying_or_synonym_substitution_confirmed") is True
    if no_copying_confirmed and not unsupported_rows and not prior_support_rows:
        checks.append(
            check_row(
                "no_reference_copy_or_simple_replacement",
                "pass",
                "Similarity control is confirmed and provenance rows do not use prior-art/reference hashes as applicant claim support.",
                "Copying or simply replacing prior art can create abnormal-filing and invalidity risk.",
                "Remove copied material, rewrite claims from applicant evidence, and rerun provenance validation.",
            )
        )
    else:
        checks.append(
            check_row(
                "no_reference_copy_or_simple_replacement",
                "fail",
                "No-copy confirmation or applicant-only claim support provenance is incomplete.",
                "Reference patents may be misused as the applicant's own invention evidence.",
                "Cure similarity control and ensure every claim limitation is supported by applicant evidence.",
            )
        )

    reference_delta_hash = str(provenance.get("reference_patent_delta_hash") or "")
    reference_delta_rows_count = int(provenance.get("reference_delta_rows_count") or 0)
    if reference_delta_hash:
        if SHA256_FULL_RE.fullmatch(reference_delta_hash) and reference_delta_rows_count > 0 and not prior_support_rows:
            checks.append(
                check_row(
                    "reference_delta_boundary_preserved",
                    "pass",
                    "Reference-patent delta is hash-bound as boundary evidence and claim support rows remain applicant-evidence based.",
                    "A reference-delta strategy can be misused as copied or simply replaced prior art if it is not kept separate from applicant support.",
                    "Keep reference patents as boundary evidence only and rerun provenance if any row uses reference material as support.",
                )
            )
        else:
            checks.append(
                check_row(
                    "reference_delta_boundary_preserved",
                    "fail",
                    "Reference-patent delta hash/count is missing or claim support rows include reference evidence.",
                    "The case may be a copied, synonym-substituted, or patchwork filing from cited patents.",
                    "Validate and hash-bind the reference-patent delta and ensure all claim support rows use applicant-owned evidence.",
                )
            )

    effect_hashes = collect_sha256(disclosure.get("technical_effects", []))
    supported_effect_hashes = own_support_hashes.union(own_hashes).union(disclosure_hashes) - prior_hashes
    missing_effect_hashes = sorted(effect_hashes - supported_effect_hashes)
    has_effects = bool(as_list(disclosure.get("technical_effects")))
    if has_effects and effect_hashes and not missing_effect_hashes:
        checks.append(
            check_row(
                "technical_effects_supported",
                "pass",
                "All technical effects cite evidence hashes traceable to applicant disclosure or R&D material.",
                "Unsupported effects can be treated as fabricated technical effects.",
                "Tie each technical effect to applicant evidence and remove unsupported performance claims.",
            )
        )
    else:
        checks.append(
            check_row(
                "technical_effects_supported",
                "fail",
                "Missing effect evidence hashes: " + ", ".join(missing_effect_hashes) if missing_effect_hashes else "Technical effects are missing or do not cite evidence hashes.",
                "Unsupported or fabricated effects can block filing and weaken examination defense.",
                "Add evidence hashes for each effect or remove the effect from the draft.",
            )
        )

    required_features = as_list(get_path(disclosure, "technical_solution.required_features"))
    known_prior_art = as_list(disclosure.get("known_prior_art"))
    prior_delta_rows = [row for row in claim_rows if str(row.get("Prior-art delta") or "").strip()]
    if feature_complexity(required_features, claim_rows) > 1 and known_prior_art and prior_delta_rows:
        checks.append(
            check_row(
                "not_obvious_patchwork",
                "pass",
                "The draft has multiple required features, known prior-art references, and element-level prior-art delta rows.",
                "Obvious patchwork of references can be treated as low-quality abnormal filing and weak claim strategy.",
                "Build a feature-by-feature prior-art delta and remove unsupported combinations.",
            )
        )
    else:
        checks.append(
            check_row(
                "not_obvious_patchwork",
                "fail",
                "Required features, known prior art, or prior-art delta rows are insufficient.",
                "The case may be only a patchwork of references without a real contribution.",
                "Add closest-prior-art analysis and invention-specific feature deltas.",
            )
        )

    degradation_hits = contains_any(disclosure_text(disclosure), DEGRADATION_PATTERNS)
    checks.append(
        check_row(
            "not_unreasonable_degradation_or_nonessential_narrowing",
            "fail" if degradation_hits else "pass",
            "Risk markers: " + ", ".join(degradation_hits) if degradation_hits else "No unreasonable-degradation or non-essential-narrowing marker was found.",
            "Unreasonable degradation or non-essential narrowing can indicate a bad-faith filing pattern.",
            "Explain the technical purpose of narrowed features or remove artificial degradation language.",
        )
    )

    batch_hits = contains_any(disclosure_text(disclosure), BATCH_PATTERNS)
    checks.append(
        check_row(
            "no_malicious_batch_or_duplicate_pattern",
            "fail" if batch_hits else "pass",
            "Batch or duplicate filing markers: " + ", ".join(batch_hits) if batch_hits else "No maliciously distributed batch filing or duplicate filing marker was found in the case text.",
            "Maliciously distributed batch filings can trigger abnormal-filing handling.",
            "Provide legitimate portfolio purpose and distinct invention evidence for each case.",
        )
    )

    applicant_name = get_path(disclosure, "applicant_context.applicant_name")
    inventors = get_path(disclosure, "inventor_input.inventors")
    checks.append(
        check_row(
            "inventor_applicant_consistency",
            "pass" if not is_blank(applicant_name) and not is_blank(inventors) and inventor_confirmed else "fail",
            "Applicant, inventors, and contribution confirmation are present." if not is_blank(applicant_name) and not is_blank(inventors) and inventor_confirmed else "Applicant, inventor list, or contribution confirmation is incomplete.",
            "False or inconsistent inventor/applicant information can block legal gate and create abnormal-filing risk.",
            "Confirm applicant identity, inventor list/order, and real contribution before any filing package.",
        )
    )

    failed_checks = [item for item in checks if item["result"] == "fail"]
    warning_checks = [item for item in checks if item["result"] == "warn"]
    risk_level = "high" if failed_checks or validation_errors else "medium" if warning_checks else "low"
    case_id = str(disclosure.get("case_id") or manifest.get("case_id") or provenance.get("case_id") or "unknown-case")

    return {
        "case_id": case_id,
        "status": "abnormal_filing_risk_assessed",
        "decision": "draft_only_do_not_file_until_ai_self_filing_gate",
        "gate": "G8 Non-abnormal filing check",
        "risk_level": risk_level,
        "checks": checks,
        "input_validation_errors": validation_errors,
        **({"reference_patent_delta_hash": reference_delta_hash} if reference_delta_hash else {}),
        **({"reference_delta_rows_count": reference_delta_rows_count} if reference_delta_hash else {}),
        **({"reference_delta_claim_elements_count": int(provenance.get("reference_delta_claim_elements_count") or 0)} if reference_delta_hash else {}),
        "errors": [item["check_id"] for item in failed_checks] + validation_errors,
        "warnings": [item["check_id"] for item in warning_checks],
        "draft_generation_allowed": True,
        "filing_allowed": False,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }


def render_report(assessment: dict[str, Any]) -> str:
    lines = [
        "# Abnormal Filing Risk Assessment",
        "",
        f"Case ID: {assessment.get('case_id')}",
        f"Gate: {assessment.get('gate')}",
        f"Status: {assessment.get('status')}",
        f"Decision: {assessment.get('decision')}",
        f"Risk level: {assessment.get('risk_level')}",
        "Filing boundary: draft-only; do not file until the AI self-filing legal/compliance gate and official-channel gates pass.",
        "Official system touched: no",
        "Official submission performed: no",
        "",
        "## CNIPA Order 77 Risk Baseline",
        "",
        "This gate screens for random computer generation, fabricated technical effects, copied or simply replaced prior art, obvious patchwork, unreasonable degradation, non-necessary narrowing, maliciously distributed batch filings, false inventor/applicant changes, and other bad-faith indicators.",
        "",
        "## Reference Delta Boundary",
        "",
        "When reference-patent delta evidence is present, this gate treats it as a hash-bound boundary and claim-strategy artifact only. It must not become applicant claim support or a novelty/patentability guarantee.",
        "",
        "## Checks",
        "",
        "| Check | Result | Evidence | Required cure |",
        "| --- | --- | --- | --- |",
    ]
    for item in assessment.get("checks", []):
        lines.append(
            "| {check_id} | {result} | {evidence} | {required_cure} |".format(
                check_id=str(item.get("check_id", "")).replace("|", "/"),
                result=str(item.get("result", "")).replace("|", "/"),
                evidence=str(item.get("evidence", "")).replace("|", "/"),
                required_cure=str(item.get("required_cure", "")).replace("|", "/"),
            )
        )
    lines.extend(
        [
            "",
            "## Filing Boundary",
            "",
            "This is a draft-only abnormal-filing risk gate. It is not legal advice, not lawyer review, not patent-agent review, not filing package validation, not official-channel preflight, not an official submission, not a receipt, and not an application number.",
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


def prepare(draft_package_dir: Path, output_dir: Path) -> tuple[dict[str, Any], int]:
    input_root = draft_package_dir.resolve()
    output_root = output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    required_files = [
        "source-material-manifest.yaml",
        "invention-disclosure.json",
        "patent-application-draft.md",
        "claim-support-map.md",
        "filing-status.json",
        "draft-evidence-provenance.json",
    ]
    source_paths = {name: input_root / name for name in required_files}
    for path in source_paths.values():
        if not path.exists():
            raise RuntimeError(f"missing_required_file: {path}")

    copied_files: list[Path] = []
    for name, source in source_paths.items():
        target = output_root / name
        copy_file(source, target)
        copied_files.append(target)
    reference_delta_input = input_root / "reference-patent-delta.json"
    reference_delta: dict[str, Any] | None = None
    if reference_delta_input.exists():
        reference_delta_output = output_root / "reference-patent-delta.json"
        copy_file(reference_delta_input, reference_delta_output)
        copied_files.append(reference_delta_output)
        reference_delta = load_json(reference_delta_output)
        copied_files.extend(copy_reference_delta_support_files(reference_delta, input_root, output_root))

    manifest_path = output_root / "source-material-manifest.yaml"
    disclosure_path = output_root / "invention-disclosure.json"
    draft_path = output_root / "patent-application-draft.md"
    claim_map_path = output_root / "claim-support-map.md"
    status_path = output_root / "filing-status.json"
    provenance_path = output_root / "draft-evidence-provenance.json"

    manifest = validate_source_material_manifest.load_packet(manifest_path)
    disclosure = load_json(disclosure_path)
    status = load_json(status_path)
    provenance = load_json(provenance_path)
    copied_files.extend(copy_manifest_material_files(manifest, input_root, output_root))

    validation_errors: list[str] = []
    validator_calls = [
        ("source_manifest", lambda: validate_source_material_manifest.validate(manifest, base_dir=output_root)),
        ("invention_disclosure", lambda: validate_invention_disclosure.validate(disclosure)),
        ("patent_application_draft", lambda: validate_patent_application_draft.validate(draft_path)),
        ("claim_support_map", lambda: validate_claim_support_map.validate(claim_map_path, allow_draft=True)),
        ("filing_status", lambda: validate_filing_status_transition.validate(status)),
        ("draft_evidence_provenance", lambda: validate_draft_evidence_provenance.validate(provenance)),
    ]
    if reference_delta is not None:
        validator_calls.append(
            ("reference_patent_delta", lambda: validate_reference_patent_delta.validate(reference_delta, output_root))
        )
    for label, call in validator_calls:
        ok, errors, _warnings = call()
        if not ok:
            validation_errors.extend([f"{label}: {item}" for item in errors])

    claim_rows = parse_claim_rows(claim_map_path)
    assessment = build_assessment(disclosure, manifest, provenance, claim_rows, validation_errors)
    assessment_path = output_root / "abnormal-filing-risk-assessment.json"
    write_json(assessment_path, assessment)
    report_path = output_root / "abnormal-filing-risk-report.md"
    report_path.write_text(render_report(assessment), encoding="utf-8")

    hash_path = output_root / "artifact-hashes.json"
    manifest_files = copied_files + [assessment_path, report_path]
    write_json(hash_path, artifact_manifest(output_root, str(assessment["case_id"]), manifest_files))
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(hash_path)

    ok = assessment.get("risk_level") == "low" and not assessment.get("errors") and hash_ok
    return {
        "ok": ok,
        "case_id": assessment.get("case_id"),
        "output_dir": str(output_root),
        "artifacts": {
            "abnormal_filing_risk_assessment": str(assessment_path),
            "abnormal_filing_risk_report": str(report_path),
            "artifact_hashes": str(hash_path),
        },
        "errors": list(assessment.get("errors") or []),
        "warnings": list(assessment.get("warnings") or []),
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft_package_dir", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare(args.draft_package_dir, args.output_dir)
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
