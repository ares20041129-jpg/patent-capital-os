#!/usr/bin/env python3
"""Validate rejection cases for malformed pre-submission handoff packages."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_pre_submission_handoff_package


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur.setdefault(part, {})
    last = parts[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


def remove_evidence_roles(package: dict[str, Any], roles: list[str]) -> None:
    evidence = package.get("evidence_files")
    if not isinstance(evidence, list):
        return
    role_set = set(roles)
    package["evidence_files"] = [
        item for item in evidence if not (isinstance(item, dict) and item.get("role") in role_set)
    ]


def apply_case(case_dir: Path, case: dict[str, Any]) -> None:
    package_path = case_dir / "pre-submission-handoff-package.json"
    package = load_json(package_path)
    mutated = copy.deepcopy(package)

    mutations = case.get("package_mutations") if isinstance(case.get("package_mutations"), dict) else {}
    for dotted, value in mutations.items():
        set_path(mutated, str(dotted), value)

    roles = case.get("remove_evidence_roles")
    if isinstance(roles, list):
        remove_evidence_roles(mutated, [str(role) for role in roles])

    write_json(package_path, mutated)

    tamper_files = case.get("tamper_files")
    if isinstance(tamper_files, list):
        for raw_rel in tamper_files:
            rel = Path(str(raw_rel))
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"unsafe_tamper_file: {raw_rel}")
            target = (case_dir / rel).resolve()
            try:
                target.relative_to(case_dir.resolve())
            except ValueError as exc:
                raise ValueError(f"tamper_file_outside_case_dir: {raw_rel}") from exc
            if not target.exists() or not target.is_file():
                raise FileNotFoundError(f"tamper_file_missing: {raw_rel}")
            target.write_text(target.read_text(encoding="utf-8", errors="replace") + "\nTAMPERED\n", encoding="utf-8")


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    spec_path = benchmark_dir / "rejection-cases.json"
    report_path = benchmark_dir / "handoff-rejection-report.md"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    if not spec_path.exists():
        return False, [f"missing_file: {spec_path}"], warnings

    spec = load_json(spec_path)
    base_folders = spec.get("base_handoff_folders")
    if not isinstance(base_folders, dict) or not base_folders:
        errors.append("base_handoff_folders_missing")
        base_folders = {}

    resolved_bases: dict[str, Path] = {}
    for label, raw_path in base_folders.items():
        path = Path(str(raw_path))
        if not path.is_absolute():
            path = (benchmark_dir / path).resolve()
        if not path.exists() or not path.is_dir():
            errors.append(f"missing_base_handoff_folder: {label}")
            continue
        ok, errs, warns = validate_pre_submission_handoff_package.validate(path)
        if not ok:
            errors.extend([f"base_handoff_invalid_{label}: {item}" for item in errs])
        warnings.extend([f"base_handoff_{label}: {item}" for item in warns])
        resolved_bases[str(label)] = path

    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("rejection_cases_missing")
        cases = []

    with tempfile.TemporaryDirectory(prefix="pre-submission-handoff-rejection-") as tmp:
        tmp_root = Path(tmp)
        for index, case in enumerate(cases, start=1):
            if not isinstance(case, dict):
                errors.append(f"case_{index}_must_be_object")
                continue
            case_id = str(case.get("id") or "")
            base_label = str(case.get("base") or "")
            expected = case.get("expected_error_fragments")
            if is_blank(case_id):
                errors.append(f"case_{index}_missing_required_field: id")
                continue
            if base_label not in resolved_bases:
                errors.append(f"{case_id}: base_not_found: {base_label}")
                continue
            if not isinstance(expected, list) or not expected:
                errors.append(f"{case_id}: expected_error_fragments_missing")
                continue

            case_dir = tmp_root / case_id
            shutil.copytree(resolved_bases[base_label], case_dir)
            try:
                apply_case(case_dir, case)
            except Exception as exc:
                errors.append(f"{case_id}: mutation_failed: {exc}")
                continue

            ok, rejection_errors, rejection_warnings = validate_pre_submission_handoff_package.validate(case_dir)
            warnings.extend([f"{case_id}: {item}" for item in rejection_warnings])
            if ok:
                errors.append(f"{case_id}: rejection_case_unexpectedly_passed")
                continue
            for fragment in expected:
                if not any(str(fragment) in item for item in rejection_errors):
                    errors.append(f"{case_id}: expected_error_not_found: {fragment}")

    if report_path.exists():
        text = report_path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in [
            "handoff rejection gate",
            "lifecycle hash mismatch must fail",
            "official action flag mutation must fail",
            "missing evidence role must fail",
            "copied evidence tamper must fail",
            "reference-delta boundary mutation must fail",
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
