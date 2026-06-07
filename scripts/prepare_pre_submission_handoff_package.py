#!/usr/bin/env python3
"""Prepare a read-only pre-submission handoff package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import build_case_queue
import validate_pre_submission_handoff_package


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path.resolve(), root.resolve()).replace("\\", "/")


def require_file(path: Path, label: str) -> Path:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"missing_{label}: {path}")
    return path


def copy_evidence(
    *,
    source: Path,
    role: str,
    package_rel: str,
    output_dir: Path,
    source_root: Path,
    entries: list[dict[str, Any]],
) -> Path:
    require_file(source, role)
    destination = output_dir / package_rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    source_hash = sha256_file(source)
    package_hash = sha256_file(destination)
    entries.append(
        {
            "role": role,
            "source_path": rel(source, source_root),
            "source_sha256": source_hash,
            "package_path": package_rel.replace("\\", "/"),
            "sha256": package_hash,
            "bytes": destination.stat().st_size,
        }
    )
    return destination


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


def render_report(package: dict[str, Any]) -> str:
    lines = [
        "# Pre-Submission Handoff Package",
        "",
        f"Case ID: {package['case_id']}",
        f"Status: {package['status']}",
        f"Decision: {package['decision']}",
        f"Legal gate mode: {package['legal_gate_mode']}",
        f"External lawyer involved: {'yes' if package['external_lawyer_involved'] else 'no'}",
        f"Lifecycle gate: {package['pre_submission_lifecycle_gate']}",
        f"Lifecycle trace hash: {package['lifecycle_trace_hash']}",
        "",
        "## Boundary",
        "",
        "This handoff package is not a filing, not a submission receipt, and not an application-number evidence artifact.",
        f"Official system touched: {'yes' if package['official_system_touched'] else 'no'}",
        f"Official submission performed: {'yes' if package['official_submission_performed'] else 'no'}",
        f"Adapter execution performed: {'yes' if package['adapter_execution_performed'] else 'no'}",
        f"Automatic submission performed: {'yes' if package['automatic_submission_performed'] else 'no'}",
        "",
        "## Evidence Files",
        "",
    ]
    for item in package.get("evidence_files", []):
        lines.append(f"- {item['role']}: `{item['package_path']}` `{item['sha256']}`")
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            package["next_action"],
            "",
        ]
    )
    return "\n".join(lines)


def build_package(source_dir: Path, output_dir: Path) -> dict[str, Any]:
    source_root = source_dir.resolve()
    result_path = require_file(source_root / "pre-submission-pipeline-result.json", "pre_submission_result")
    result = load_json(result_path)
    case_id = str(result.get("case_id") or source_root.name)

    materials_dir = source_root / "application-materials-pipeline" / "application-materials"
    application_materials_path = require_file(materials_dir / "application-materials.json", "application_materials")
    application_materials = load_json(application_materials_path)

    final_package_dir = source_root / "ai-self-filing-package-validation"
    approved_dir = source_root / "ai-self-filing-approved-adapter-preflight"
    official_ready_dir = source_root / "ai-self-filing-official-ready"
    lifecycle_dir = source_root / "case-lifecycle-trace"

    evidence_files: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    copy_evidence(
        source=result_path,
        role="pre_submission_result",
        package_rel="evidence/control/pre-submission-pipeline-result.json",
        output_dir=output_dir,
        source_root=source_root,
        entries=evidence_files,
    )
    copy_evidence(
        source=source_root / "pre-submission-pipeline-report.md",
        role="pre_submission_report",
        package_rel="evidence/control/pre-submission-pipeline-report.md",
        output_dir=output_dir,
        source_root=source_root,
        entries=evidence_files,
    )
    copy_evidence(
        source=application_materials_path,
        role="application_materials",
        package_rel="evidence/application-materials/application-materials.json",
        output_dir=output_dir,
        source_root=source_root,
        entries=evidence_files,
    )
    for role, filename in [
        ("request_form_metadata", "request-form-metadata.json"),
        ("document_generation_plan", "document-generation-plan.json"),
        ("claims_material", "claims-material.md"),
        ("specification_material", "specification-material.md"),
        ("abstract_material", "abstract-material.md"),
        ("drawings_materials_plan", "drawings-materials-plan.md"),
        ("xml_readiness_checklist", "xml-readiness-checklist.json"),
    ]:
        copy_evidence(
            source=materials_dir / filename,
            role=role,
            package_rel=f"evidence/application-materials/{filename}",
            output_dir=output_dir,
            source_root=source_root,
            entries=evidence_files,
        )

    for role, filename in [
        ("final_claims_xml", "claims-ai-self-filing-final.xml"),
        ("final_specification_xml", "specification-ai-self-filing-final.xml"),
        ("final_abstract_xml", "abstract-ai-self-filing-final.xml"),
        ("final_drawings_pdf", "drawings-ai-self-filing-final.pdf"),
        ("final_request_metadata_xml", "request_metadata-ai-self-filing-final.xml"),
        ("filing_package_manifest", "filing-package-manifest.yaml"),
        ("ai_self_filing_authorization_packet", "ai-self-filing-authorization-packet.json"),
    ]:
        copy_evidence(
            source=final_package_dir / filename,
            role=role,
            package_rel=f"evidence/final-package/{filename}",
            output_dir=output_dir,
            source_root=source_root,
            entries=evidence_files,
        )

    for role, source in [
        ("official_channel_preflight", official_ready_dir / "official-channel-preflight.yaml"),
        ("receipt_capture_plan", official_ready_dir / "receipt-capture-plan.yaml"),
        ("approved_adapter_preflight", approved_dir / "approved-adapter-preflight.json"),
        ("filing_adapter_request", approved_dir / "filing-adapter-request.json"),
        ("audit_log_entry_plan", approved_dir / "audit-log-entry-plan.yaml"),
        ("docket_entry_plan", approved_dir / "docket-entry-plan.yaml"),
        ("case_lifecycle_trace", lifecycle_dir / "case-lifecycle-trace.json"),
        ("lifecycle_report", lifecycle_dir / "lifecycle-report.md"),
    ]:
        copy_evidence(
            source=source,
            role=role,
            package_rel=f"evidence/control/{source.name}",
            output_dir=output_dir,
            source_root=source_root,
            entries=evidence_files,
        )

    reference_delta_path = source_root / "reference-patent-delta" / "reference-patent-delta.json"
    if reference_delta_path.exists():
        copy_evidence(
            source=reference_delta_path,
            role="reference_patent_delta",
            package_rel="evidence/reference-patent-delta/reference-patent-delta.json",
            output_dir=output_dir,
            source_root=source_root,
            entries=evidence_files,
        )

    lifecycle_entry = next(item for item in evidence_files if item["role"] == "case_lifecycle_trace")
    lifecycle_trace = load_json(lifecycle_dir / "case-lifecycle-trace.json")
    package = {
        "case_id": case_id,
        "handoff_package_type": "pre_submission_approved_adapter_execution_handoff",
        "created_at": build_case_queue.utc_plus_8_now(),
        "source_pre_submission_dir": rel(source_root, output_dir),
        "source_pre_submission_hash": sha256_file(result_path),
        "status": "approved_for_adapter_execution",
        "decision": "handoff_ready_no_auto_submit",
        "legal_gate_mode": result.get("legal_gate_mode"),
        "external_lawyer_involved": False,
        "pre_submission_lifecycle_gate": result.get("pre_submission_lifecycle_gate"),
        "lifecycle_trace_hash": result.get("lifecycle_trace_hash"),
        "copied_lifecycle_trace_hash": lifecycle_entry["sha256"],
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "automatic_submission_performed": False,
        "final_package_hash": application_materials.get("final_package_hash"),
        "application_materials_hash": sha256_file(application_materials_path),
        "reference_patent_delta_hash": result.get("reference_patent_delta_hash", ""),
        "reference_delta_rows_count": lifecycle_trace.get("reference_delta_rows_count"),
        "reference_delta_claim_elements_count": lifecycle_trace.get("reference_delta_claim_elements_count"),
        "reference_delta_boundary_preserved": lifecycle_trace.get("reference_delta_boundary_preserved"),
        "official_material_inventory": application_materials.get("official_material_inventory", []),
        "evidence_files": evidence_files,
        "handoff_controls": {
            "read_only_handoff": True,
            "does_not_authorize_automatic_submission": True,
            "requires_separate_adapter_execution_result": True,
            "requires_receipt_capture_after_submission": True,
            "no_receipt_claimed": True,
            "no_application_number_claimed": True,
        },
        "next_action": "Use this read-only package only as approved-adapter execution input evidence; adapter execution, receipt capture, and application-number evidence remain separate gates.",
    }
    return package


def run(source_dir: Path, output_dir: Path) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        return {
            "ok": False,
            "errors": [f"output_dir_exists_and_is_not_empty: {output_dir}"],
            "warnings": [],
        }
    package = build_package(source_dir, output_dir)
    package_path = output_dir / "pre-submission-handoff-package.json"
    report_path = output_dir / "pre-submission-handoff-report.md"
    hashes_path = output_dir / "artifact-hashes.json"
    write_json(package_path, package)
    report_path.write_text(render_report(package), encoding="utf-8")

    evidence_paths = [output_dir / item["package_path"] for item in package["evidence_files"]]
    write_json(hashes_path, artifact_manifest(output_dir, package["case_id"], [package_path, report_path, *evidence_paths]))

    ok, errors, warnings = validate_pre_submission_handoff_package.validate(output_dir)
    return {
        "ok": ok,
        "case_id": package["case_id"],
        "output_dir": str(output_dir),
        "artifacts": {
            "handoff_package": str(package_path),
            "handoff_report": str(report_path),
            "artifact_hashes": str(hashes_path),
        },
        "official_system_touched": False,
        "official_submission_performed": False,
        "adapter_execution_performed": False,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_pre_submission_dir", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = run(args.source_pre_submission_dir.resolve(), args.output_dir.resolve())
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)], "warnings": []}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result.get("ok") else "FAIL")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
