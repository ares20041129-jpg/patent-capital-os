#!/usr/bin/env python3
"""Prepare a standard Patent Capital OS case package from raw intake files."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest
import validate_case_package_manifest
import validate_source_material_manifest


FOLDERS = {
    "intake": "00-intake",
    "source_files": "00-intake/source-files",
    "normalized": "01-normalized",
    "draft": "02-draft",
    "legal": "03-legal",
    "filing_package": "04-package",
    "official_preflight": "05-official-preflight",
    "adapter": "06-adapter",
    "receipts": "07-receipts",
    "docket": "08-docket",
    "portfolio": "09-portfolio",
    "audit": "audit",
}


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def material_type(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if "prior" in name or "patent" in name:
        return "prior_art"
    if "draw" in name or suffix in {".png", ".jpg", ".jpeg", ".svg", ".pdf"}:
        return "drawing"
    if "experiment" in name or "test" in name:
        return "experiment"
    if "prototype" in name or "log" in name:
        return "prototype_log"
    if "transcript" in name:
        return "transcript"
    if "email" in name or suffix in {".eml", ".msg"}:
        return "email"
    if "disclosure" in name or "invention" in name:
        return "invention_disclosure"
    return "other"


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def source_package_hash(items: list[dict[str, Any]]) -> str:
    payload = "\n".join(
        f"{item['relative_path']}\t{item['sha256']}\t{item['bytes']}"
        for item in sorted(items, key=lambda item: item["relative_path"])
    ).encode("utf-8")
    return sha256_bytes(payload)


def ensure_safe_paths(source_dir: Path, output_dir: Path) -> None:
    source = source_dir.resolve()
    output = output_dir.resolve()
    if not source.exists() or not source.is_dir():
        raise RuntimeError(f"source_dir_not_found_or_not_directory: {source}")
    if source == output or source in output.parents:
        raise RuntimeError("output_dir_must_not_be_inside_source_dir")
    if output.exists() and any(output.iterdir()):
        raise RuntimeError("output_dir_exists_and_is_not_empty")


def copy_sources(source_dir: Path, package_root: Path, received_from: str, received_at: str) -> list[dict[str, Any]]:
    source_root = source_dir.resolve()
    target_root = package_root / FOLDERS["source_files"]
    materials: list[dict[str, Any]] = []
    source_files: list[Path] = []
    for source_path in sorted(source_root.rglob("*")):
        if source_path.is_symlink():
            raise RuntimeError(f"source_file_is_symlink: {source_path}")
        if not source_path.is_file():
            continue
        resolved_source = source_path.resolve()
        if not is_relative_to(resolved_source, source_root):
            raise RuntimeError(f"source_file_resolves_outside_source_dir: {source_path}")
        source_files.append(source_path)

    for index, source_path in enumerate(source_files, start=1):
        rel_source = source_path.relative_to(source_root)
        target_path = (target_root / rel_source).resolve()
        if not is_relative_to(target_path, target_root.resolve()):
            raise RuntimeError(f"target_file_resolves_outside_source_files_dir: {rel_source}")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        file_hash = sha256_file(target_path)
        materials.append(
            {
                "material_id": f"M-{index:03d}",
                "relative_path": rel(target_path, package_root),
                "filename": target_path.name,
                "type": material_type(target_path),
                "received_at": received_at,
                "sha256": file_hash,
                "hash": file_hash,
                "bytes": target_path.stat().st_size,
                "source_owner": received_from,
                "confidentiality": "confidential",
                "usable_for_claim_support": material_type(target_path) != "prior_art",
                "notes": "Copied into standard case package intake folder.",
            }
        )
    if not materials:
        raise RuntimeError("source_dir_contains_no_files")
    return materials


def build_source_manifest(case_id: str, received_from: str, received_at: str, materials: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "received_at": received_at,
        "received_from": received_from,
        "confidentiality_marker": "confidential",
        "source_package_hash": source_package_hash(materials),
        "materials": [
            {
                "material_id": item["material_id"],
                "filename": item["relative_path"],
                "type": item["type"],
                "received_at": item["received_at"],
                "hash": item["hash"],
                "source_owner": item["source_owner"],
                "confidentiality": item["confidentiality"],
                "usable_for_claim_support": item["usable_for_claim_support"],
                "notes": item["notes"],
            }
            for item in materials
        ],
        "chain_of_custody": [
            {
                "actor": "prepare_case_package.py",
                "action": "received",
                "timestamp": received_at,
                "input_hash": source_package_hash(materials),
                "output_hash": source_package_hash(materials),
            }
        ],
        "claim_support_links": [],
        "missing_materials": [
            "inventor confirmation",
            "ownership confirmation",
            "AI legal/compliance gate confirmation",
            "applicant filing authorization",
        ],
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_artifact_manifest(package_root: Path, case_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [
            {
                "path": rel(path, package_root),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
    }


def render_report(case_id: str, materials: list[dict[str, Any]]) -> str:
    lines = [
        "# Case Package Intake Report",
        "",
        f"Case ID: {case_id}",
        "Package status: intake_received",
        "Official system touched: no",
        "Official submission performed: no",
        "Filing allowed: no",
        "",
        "## Materials",
        "",
        "| Material | Type | Bytes | Hash |",
        "| --- | --- | --- | --- |",
    ]
    for item in materials:
        lines.append(f"| {item['material_id']} | {item['type']} | {item['bytes']} | {item['sha256']} |")
    lines.extend(
        [
            "",
            "## Missing Legal Items",
            "",
            "- AI legal/compliance gate confirmation.",
            "- Applicant filing authorization.",
            "- Inventor and ownership confirmation.",
            "- Secrecy or foreign-filing review.",
        ]
    )
    return "\n".join(lines) + "\n"


def prepare_package(
    source_dir: Path,
    output_dir: Path,
    case_id: str,
    received_from: str,
    jurisdiction: str,
    intake_mode: str,
) -> tuple[dict[str, Any], int]:
    ensure_safe_paths(source_dir, output_dir)
    package_root = output_dir.resolve()
    package_root.mkdir(parents=True, exist_ok=True)
    for folder in FOLDERS.values():
        (package_root / folder).mkdir(parents=True, exist_ok=True)

    received_at = build_case_queue.utc_plus_8_now()
    materials = copy_sources(source_dir, package_root, received_from, received_at)
    source_manifest = build_source_manifest(case_id, received_from, received_at, materials)
    source_manifest_path = package_root / "01-normalized" / "source-material-manifest.json"
    write_json(source_manifest_path, source_manifest)

    source_manifest_hash = sha256_file(source_manifest_path)
    case_manifest = {
        "case_id": case_id,
        "package_id": f"{case_id}-PKG-001",
        "jurisdiction": jurisdiction,
        "package_status": "intake_received",
        "received_at": received_at,
        "received_from": received_from,
        "intake_mode": intake_mode,
        "confidentiality_marker": "confidential",
        "source_package_hash": source_manifest["source_package_hash"],
        "folders": {key: value for key, value in FOLDERS.items() if key != "source_files"},
        "source_material_manifest": "01-normalized/source-material-manifest.json",
        "source_material_manifest_hash": source_manifest_hash,
        "source_files": [
            {
                "material_id": item["material_id"],
                "relative_path": item["relative_path"],
                "filename": item["filename"],
                "type": item["type"],
                "sha256": item["sha256"],
                "bytes": item["bytes"],
                "source_owner": item["source_owner"],
                "confidentiality": item["confidentiality"],
                "usable_for_claim_support": item["usable_for_claim_support"],
            }
            for item in materials
        ],
        "legal_gate": {
            "status": "pending",
            "legal_gate_mode": "ai_self_filing_no_external_lawyer",
            "ai_legal_compliance_confirmation_present": False,
            "external_lawyer_involved": False,
            "applicant_authorization_present": False,
            "inventor_confirmation_present": False,
            "ownership_confirmation_present": False,
            "secrecy_review_status": "unknown",
            "filing_allowed": False,
        },
        "official_actions": {
            "official_system_touched": False,
            "official_submission_performed": False,
            "receipt_captured": False,
            "application_number_received": False,
        },
        "next_action": "normalize_invention_disclosure",
        "notes": "Prepared by prepare_case_package.py. Intake only; no filing action performed.",
    }
    case_manifest_path = package_root / "case-package-manifest.json"
    write_json(case_manifest_path, case_manifest)

    filing_status = {
        "case_id": case_id,
        "status": "intake_received",
        "legal_gate": "pending",
        "legal_gate_mode": "ai_self_filing_no_external_lawyer",
        "external_lawyer_involved": False,
        "decision": "intake_only_do_not_file",
        "official_submission_performed": False,
        "official_system_touched": False,
        "official_receipt_hash": "",
        "application_number": "",
        "updated_at": received_at,
    }
    filing_status_path = package_root / "filing-status.json"
    write_json(filing_status_path, filing_status)

    report_path = package_root / "intake-report.md"
    report_path.write_text(render_report(case_id, materials), encoding="utf-8")

    generated_files = [case_manifest_path, source_manifest_path, filing_status_path, report_path]
    artifact_manifest = build_artifact_manifest(package_root, case_id, generated_files)
    artifact_manifest_path = package_root / "artifact-hashes.json"
    write_json(artifact_manifest_path, artifact_manifest)

    package_ok, package_errors, package_warnings = validate_case_package_manifest.validate(case_manifest, root=package_root)
    source_ok, source_errors, source_warnings = validate_source_material_manifest.validate(source_manifest, base_dir=package_root)
    hash_ok, hash_errors, hash_warnings = validate_artifact_hash_manifest.validate(artifact_manifest_path)
    ok = package_ok and source_ok and hash_ok
    response = {
        "ok": ok,
        "case_id": case_id,
        "package_root": str(package_root),
        "artifacts": {
            "case_package_manifest": str(case_manifest_path),
            "source_material_manifest": str(source_manifest_path),
            "filing_status": str(filing_status_path),
            "intake_report": str(report_path),
            "artifact_hashes": str(artifact_manifest_path),
        },
        "package_errors": package_errors,
        "package_warnings": package_warnings,
        "source_errors": source_errors,
        "source_warnings": source_warnings,
        "hash_errors": hash_errors,
        "hash_warnings": hash_warnings,
        "official_system_touched": False,
        "official_submission_performed": False,
    }
    return response, 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--received-from", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--jurisdiction", default="CN")
    parser.add_argument("--intake-mode", choices=["manual_upload", "email", "api", "batch_import"], default="manual_upload")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        response, exit_code = prepare_package(
            source_dir=args.source_dir,
            output_dir=args.output_dir,
            case_id=args.case_id,
            received_from=args.received_from,
            jurisdiction=args.jurisdiction,
            intake_mode=args.intake_mode,
        )
    except Exception as exc:
        response, exit_code = {
            "ok": False,
            "errors": [str(exc)],
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
