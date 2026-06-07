#!/usr/bin/env python3
"""Create an invention disclosure scaffold from a standard case package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_case_package_manifest
import validate_invention_disclosure_scaffold


CN_PATENT_RE = re.compile(r"\bCN\d{8,}[A-Z]?\b", re.IGNORECASE)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def first_labeled_value(text: str, labels: list[str]) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        for label in labels:
            prefix = label.lower() + ":"
            if stripped.lower().startswith(prefix):
                return stripped[len(label) + 1 :].strip()
    return ""


def read_material_text(package_root: Path, source_files: list[dict[str, Any]]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for item in source_files:
        rel_path = item.get("relative_path")
        material_id = item.get("material_id")
        if not rel_path or not material_id:
            continue
        path = package_root / str(rel_path)
        if not path.exists() or not path.is_file():
            continue
        try:
            texts[str(material_id)] = path.read_text(encoding="utf-8", errors="replace")[:20000]
        except Exception:
            texts[str(material_id)] = ""
    return texts


def sentence_list(value: str) -> list[str]:
    value = value.strip()
    return [value] if value else []


def extract_scaffold(case_manifest: dict[str, Any], package_root: Path) -> dict[str, Any]:
    case_id = str(case_manifest.get("case_id") or "")
    source_files = case_manifest.get("source_files") if isinstance(case_manifest.get("source_files"), list) else []
    texts = read_material_text(package_root, source_files)
    joined_text = "\n".join(texts.values())

    title = first_labeled_value(joined_text, ["Title"]) or f"{case_id} invention disclosure scaffold"
    problem = first_labeled_value(joined_text, ["Problem"]) or "Technical problem pending inventor confirmation."
    solution = first_labeled_value(joined_text, ["Technical idea", "Technical solution"]) or "Technical solution pending inventor confirmation."
    evidence = first_labeled_value(joined_text, ["Evidence"]) or "Evidence mapping pending."

    drawing_notes = []
    prototypes = []
    experiments = []
    logs = []
    source_hashes = []
    known_prior_art: list[dict[str, str]] = []
    for item in source_files:
        material_type = str(item.get("type") or "")
        filename = str(item.get("filename") or "")
        material_hash = str(item.get("sha256") or "")
        if material_hash:
            source_hashes.append(material_hash)
        if material_type == "drawing":
            drawing_notes.append(filename)
        if material_type == "prototype_log":
            prototypes.append(filename)
            logs.append(material_hash)
        if material_type == "experiment":
            experiments.append(filename)
        if material_type == "prior_art":
            text = texts.get(str(item.get("material_id")), "")
            refs = sorted(set(match.upper() for match in CN_PATENT_RE.findall(text)))
            if refs:
                for ref in refs:
                    known_prior_art.append({"publication": ref, "relevance": "Extracted from prior-art material; relevance pending analysis."})
            else:
                known_prior_art.append({"publication": filename, "relevance": "Prior-art material received; publication identifier pending extraction."})

    technical_effects = []
    if evidence and evidence != "Evidence mapping pending.":
        technical_effects.append({"effect": "Potential technical effect pending confirmation.", "evidence": evidence})

    return {
        "case_id": case_id,
        "disclosure_status": "scaffold_pending_confirmation",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "normalized_at": build_case_queue.utc_plus_8_now(),
        "source_material_manifest": str(case_manifest.get("source_material_manifest") or ""),
        "source_package_hash": str(case_manifest.get("source_package_hash") or ""),
        "invention_disclosure": {
            "case_id": case_id,
            "title": title,
            "jurisdiction_plan": {
                "first_filing": str(case_manifest.get("jurisdiction") or "CN"),
                "later_foreign_or_pct": None,
            },
            "business_goal": "Normalize raw intake into a disclosure scaffold for inventor, applicant, and AI legal/compliance confirmation.",
            "applicant_context": {
                "applicant_name": "TBD",
                "product_or_project": title,
                "actual_r_and_d_basis": "Raw source materials received; actual R&D basis requires inventor confirmation.",
            },
            "inventor_input": {
                "inventors": [],
                "contribution_confirmed": False,
            },
            "technical_problem": problem,
            "technical_solution": {
                "required_features": sentence_list(solution),
                "optional_features": [],
            },
            "technical_effects": technical_effects,
            "embodiments": [
                {
                    "name": "Implementation scaffold pending confirmation",
                    "implementation_steps": sentence_list(solution),
                    "components": [],
                    "parameters": [],
                }
            ],
            "drawings_needed": drawing_notes or ["Drawing requirements pending review."],
            "known_prior_art": known_prior_art,
            "similarity_control": {
                "uses_reference_patents": bool(known_prior_art),
                "no_copying_or_synonym_substitution_confirmed": False,
                "real_technical_contribution_summary": "Pending inventor and AI legal/compliance confirmation.",
            },
            "data_and_evidence": {
                "prototypes": prototypes,
                "experiments": experiments,
                "logs_or_measurements": logs,
                "source_hashes": source_hashes,
            },
            "secrecy": {
                "invention_completed_in_china": None,
                "foreign_or_pct_planned": None,
                "secrecy_review_status": "unknown",
            },
            "ai_legal_compliance_questions": [
                "Confirm inventor names and contributions.",
                "Confirm applicant and ownership basis.",
                "Confirm no copying or synonym substitution from reference patents.",
                "Confirm technical effects and supporting evidence.",
                "Confirm secrecy review and filing jurisdiction plan.",
            ],
        },
        "scaffold_controls": {
            "inventor_confirmation_pending": True,
            "legal_gate_pending": True,
            "legal_gate_mode": "ai_self_filing_no_external_lawyer",
            "external_lawyer_involved": False,
            "no_copying_confirmation_pending": True,
            "filing_allowed": False,
            "draft_generation_allowed": False,
        },
    }


def render_report(scaffold: dict[str, Any]) -> str:
    disclosure = scaffold["invention_disclosure"]
    lines = [
        "# Invention Disclosure Normalization Report",
        "",
        f"Case ID: {scaffold.get('case_id')}",
        "Disclosure status: scaffold_pending_confirmation",
        "Filing allowed: no",
        "Draft generation allowed: no",
        "",
        "## Extracted Fields",
        "",
        f"- Title: {disclosure.get('title')}",
        f"- Technical problem: {disclosure.get('technical_problem')}",
        f"- Required features: {len(disclosure.get('technical_solution', {}).get('required_features', []))}",
        f"- Known prior art items: {len(disclosure.get('known_prior_art', []))}",
        f"- Source hashes: {len(disclosure.get('data_and_evidence', {}).get('source_hashes', []))}",
        "",
        "## Pending Confirmations",
        "",
        "- Inventor contribution confirmation.",
        "- Applicant and ownership basis.",
        "- AI legal/compliance gate confirmation.",
        "- No-copying and no-synonym-substitution confirmation.",
        "- Technical effects and evidence mapping.",
    ]
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


def normalize(case_package: Path, output_dir: Path | None = None) -> tuple[dict[str, Any], int]:
    package_root = case_package.resolve()
    manifest_path = package_root / "case-package-manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(f"missing_case_package_manifest: {manifest_path}")
    case_manifest = load_json(manifest_path)
    package_ok, package_errors, package_warnings = validate_case_package_manifest.validate(case_manifest, root=package_root)

    output_root = output_dir.resolve() if output_dir else package_root / "01-normalized"
    output_root.mkdir(parents=True, exist_ok=True)
    scaffold = extract_scaffold(case_manifest, package_root)
    scaffold_path = output_root / "invention-disclosure-scaffold.json"
    report_path = output_root / "normalization-report.md"
    write_json(scaffold_path, scaffold)
    report_path.write_text(render_report(scaffold), encoding="utf-8")
    manifest = artifact_manifest(output_root, scaffold["case_id"], [scaffold_path, report_path])
    artifact_path = output_root / "artifact-hashes.json"
    write_json(artifact_path, manifest)

    scaffold_ok, scaffold_errors, scaffold_warnings = validate_invention_disclosure_scaffold.validate(scaffold)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(artifact_path)
    ok = package_ok and scaffold_ok and hash_ok
    response = {
        "ok": ok,
        "case_id": scaffold["case_id"],
        "output_dir": str(output_root),
        "artifacts": {
            "invention_disclosure_scaffold": str(scaffold_path),
            "normalization_report": str(report_path),
            "artifact_hashes": str(artifact_path),
        },
        "package_errors": package_errors,
        "package_warnings": package_warnings,
        "scaffold_errors": scaffold_errors,
        "scaffold_warnings": scaffold_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "filing_allowed": False,
        "draft_generation_allowed": False,
    }
    return response, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_package", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = normalize(args.case_package, args.output_dir)
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
            "filing_allowed": False,
            "draft_generation_allowed": False,
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
