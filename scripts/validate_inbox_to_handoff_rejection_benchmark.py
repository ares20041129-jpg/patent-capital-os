#!/usr/bin/env python3
"""Validate rejection cases for unsafe inbox-to-handoff inputs."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import orchestrate_inbox_to_handoff
import validate_artifact_hash_manifest
import validate_inbox_to_handoff_benchmark


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def mutate_config(inbox_dir: Path, case_name: str, updates: dict[str, Any]) -> None:
    config_path = inbox_dir / case_name / "case-config.json"
    config = load_json(config_path)
    config.update(updates)
    write_json(config_path, config)


def run_case(
    case: dict[str, Any],
    base_inbox: Path,
    output_root: Path,
    confirmation_template: Path,
    ai_source_template: Path,
    official_preflight_template: Path,
) -> tuple[dict[str, Any], int]:
    case_id = str(case.get("id") or "")
    inbox_dir = output_root / case_id / "inbox"
    output_dir = output_root / case_id / "output"
    operation = str(case.get("operation") or "")

    if operation == "empty_inbox":
        inbox_dir.mkdir(parents=True, exist_ok=True)
    else:
        shutil.copytree(base_inbox, inbox_dir)

    if operation == "mutate_config":
        case_name = str(case.get("case_name") or "")
        updates = case.get("updates")
        if not case_name or not isinstance(updates, dict):
            raise ValueError(f"{case_id}: mutate_config_missing_case_name_or_updates")
        mutate_config(inbox_dir, case_name, updates)
    elif operation == "missing_raw_input":
        target = inbox_dir / str(case.get("case_name") or "") / str(case.get("remove_dir") or "")
        if target.exists() and target.is_dir():
            shutil.rmtree(target)
    elif operation == "existing_output":
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(output_dir / "inbox-to-handoff-result.json", {"stale": True})
    elif operation == "empty_inbox":
        pass
    else:
        raise ValueError(f"{case_id}: unknown_operation: {operation}")

    return orchestrate_inbox_to_handoff.orchestrate(
        inbox_dir=inbox_dir,
        output_dir=output_dir,
        inbox_id=f"{case_id.upper()}-INBOX",
        confirmation_packet_template=confirmation_template,
        ai_self_filing_source_template=ai_source_template,
        official_preflight_source_template=official_preflight_template,
        queue_owner="Patent Capital OS rejection benchmark",
        scripts_dir=Path(__file__).resolve().parent,
    )


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    spec_path = benchmark_dir / "rejection-cases.json"
    report_path = benchmark_dir / "inbox-rejection-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    if not spec_path.exists():
        return False, [f"missing_file: {spec_path}"], warnings

    spec = load_json(spec_path)
    base_folder = Path(str(spec.get("base_inbox_to_handoff_folder") or ""))
    if not base_folder.is_absolute():
        base_folder = (benchmark_dir / base_folder).resolve()
    base_inbox = base_folder / "inbox"
    if not base_folder.exists() or not base_folder.is_dir():
        errors.append(f"missing_base_inbox_to_handoff_folder: {base_folder}")
    else:
        ok, errs, warns = validate_inbox_to_handoff_benchmark.validate(base_folder)
        if not ok:
            errors.extend([f"base_inbox_to_handoff: {item}" for item in errs])
        warnings.extend([f"base_inbox_to_handoff: {item}" for item in warns])
    if not base_inbox.exists() or not base_inbox.is_dir():
        errors.append(f"missing_base_inbox: {base_inbox}")

    confirmation_template = (benchmark_dir / str(spec.get("confirmation_packet_template") or "")).resolve()
    ai_source_template = (benchmark_dir / str(spec.get("ai_self_filing_source_template") or "")).resolve()
    official_preflight_template = (benchmark_dir / str(spec.get("official_preflight_source_template") or "")).resolve()
    for label, path in [
        ("confirmation_packet_template", confirmation_template),
        ("ai_self_filing_source_template", ai_source_template),
        ("official_preflight_source_template", official_preflight_template),
    ]:
        if not path.exists() or not path.is_file():
            errors.append(f"missing_{label}: {path}")

    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("rejection_cases_must_be_nonempty_list")
        cases = []

    if errors:
        return False, errors, warnings

    with tempfile.TemporaryDirectory(prefix="inbox-to-handoff-rejection-") as tmp:
        tmp_root = Path(tmp)
        for index, case in enumerate(cases, start=1):
            if not isinstance(case, dict):
                errors.append(f"case_{index}_must_be_object")
                continue
            case_id = str(case.get("id") or "")
            expected = case.get("expected_error_fragments")
            if is_blank(case_id):
                errors.append(f"case_{index}_missing_required_field: id")
                continue
            if not isinstance(expected, list) or not expected:
                errors.append(f"{case_id}: expected_error_fragments_missing")
                continue

            try:
                response, exit_code = run_case(
                    case,
                    base_inbox,
                    tmp_root,
                    confirmation_template,
                    ai_source_template,
                    official_preflight_template,
                )
            except Exception as exc:
                response, exit_code = {
                    "ok": False,
                    "errors": [str(exc)],
                    "official_system_touched": False,
                    "official_submission_performed": False,
                    "adapter_execution_performed": False,
                    "external_lawyer_involved": False,
                }, 1
            if exit_code == 0 or response.get("ok") is True:
                errors.append(f"{case_id}: rejection_case_unexpectedly_passed")
                continue
            haystack = " | ".join(str(item) for item in response.get("errors", []))
            for fragment in expected:
                if str(fragment) not in haystack:
                    errors.append(f"{case_id}: expected_error_not_found: {fragment}")
            for field in ["official_system_touched", "official_submission_performed", "adapter_execution_performed", "external_lawyer_involved"]:
                if response.get(field) is not False:
                    errors.append(f"{case_id}: {field}_must_be_false")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "inbox rejection gate",
            "path traversal must fail",
            "missing raw input must fail",
            "empty inbox must fail",
            "existing output must fail",
            "no official action",
        ]:
            if needle not in text:
                errors.append(f"report_missing_text: {needle}")
    else:
        errors.append(f"missing_file: {report_path}")

    if hashes_path.exists():
        ok, errs, warns = validate_artifact_hash_manifest.validate(hashes_path)
        if not ok:
            errors.extend([f"artifact_hashes: {item}" for item in errs])
        warnings.extend([f"artifact_hashes: {item}" for item in warns])
    else:
        errors.append(f"missing_file: {hashes_path}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.benchmark_dir)
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
