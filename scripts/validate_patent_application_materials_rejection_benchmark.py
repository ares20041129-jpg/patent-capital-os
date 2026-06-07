#!/usr/bin/env python3
"""Validate rejection cases for malformed patent application materials."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_patent_application_materials


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if not isinstance(cur, dict):
            raise ValueError(f"mutation_parent_not_object: {dotted}")
        cur = cur.setdefault(part, {})
    if not isinstance(cur, dict):
        raise ValueError(f"mutation_target_parent_not_object: {dotted}")
    cur[parts[-1]] = value


def remove_path(data: dict[str, Any], dotted: str) -> None:
    cur: Any = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if not isinstance(cur, dict) or part not in cur:
            return
        cur = cur[part]
    if isinstance(cur, dict):
        cur.pop(parts[-1], None)


def remove_document_type(data: dict[str, Any], list_name: str, doc_type: str) -> None:
    items = data.get(list_name)
    if isinstance(items, list):
        data[list_name] = [item for item in items if not (isinstance(item, dict) and item.get("type") == doc_type)]


def mutate_document_type(data: dict[str, Any], list_name: str, doc_type: str, updates: dict[str, Any]) -> None:
    items = data.get(list_name)
    if not isinstance(items, list):
        return
    for item in items:
        if isinstance(item, dict) and item.get("type") == doc_type:
            item.update(updates)


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def material_fixtures(case: dict[str, Any], benchmark_dir: Path, materials_dir: Path, errors: list[str]) -> list[Path]:
    created: list[Path] = []
    fixtures = case.get("material_fixtures")
    if not isinstance(fixtures, list):
        return created

    for index, fixture in enumerate(fixtures, start=1):
        if not isinstance(fixture, dict):
            errors.append(f"material_fixture_{index}_must_be_object")
            continue
        raw_target = Path(str(fixture.get("path") or ""))
        raw_source = Path(str(fixture.get("source") or ""))
        if raw_target.is_absolute() or ".." in raw_target.parts or not raw_target.name:
            errors.append(f"material_fixture_{index}_unsafe_target_path")
            continue
        if raw_source.is_absolute() or ".." in raw_source.parts or not raw_source.name:
            errors.append(f"material_fixture_{index}_unsafe_source_path")
            continue
        source = (benchmark_dir / raw_source).resolve()
        target = (materials_dir / raw_target).resolve()
        if not is_relative_to(target, materials_dir.resolve()):
            errors.append(f"material_fixture_{index}_target_outside_materials_root")
            continue
        if not source.exists() or not is_relative_to(source, benchmark_dir.resolve()):
            errors.append(f"material_fixture_{index}_source_not_found")
            continue
        if target.exists():
            errors.append(f"material_fixture_{index}_target_already_exists")
            continue
        target.write_bytes(source.read_bytes())
        created.append(target)

    return created


def apply_case(base: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    materials = copy.deepcopy(base)
    for dotted in case.get("remove_paths", []):
        remove_path(materials, str(dotted))
    for item in case.get("remove_document_types", []):
        if isinstance(item, dict):
            remove_document_type(materials, str(item.get("list") or ""), str(item.get("type") or ""))
    for item in case.get("mutate_document_types", []):
        if isinstance(item, dict) and isinstance(item.get("updates"), dict):
            mutate_document_type(
                materials,
                str(item.get("list") or ""),
                str(item.get("type") or ""),
                item["updates"],
            )
    mutations = case.get("mutations") if isinstance(case.get("mutations"), dict) else {}
    for dotted, value in mutations.items():
        set_path(materials, str(dotted), value)
    return materials


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    spec_path = benchmark_dir / "rejection-cases.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    if not spec_path.exists():
        return False, [f"missing_file: {spec_path}"], warnings

    spec = load_json(spec_path)
    base_path = Path(str(spec.get("base_materials") or ""))
    if not base_path.is_absolute():
        base_path = (benchmark_dir / base_path).resolve()
    if not base_path.exists():
        errors.append(f"missing_base_materials: {base_path}")
        base_materials: dict[str, Any] = {}
    else:
        base_materials = load_json(base_path)
        base_ok, base_errors, base_warnings = validate_patent_application_materials.validate(
            base_materials,
            base_path.parent,
        )
        if not base_ok:
            errors.extend([f"base_materials_should_pass: {item}" for item in base_errors])
        warnings.extend([f"base_materials: {item}" for item in base_warnings])

    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("rejection_cases_missing")
        cases = []

    for case in cases:
        if not isinstance(case, dict):
            errors.append("rejection_case_must_be_object")
            continue
        case_id = str(case.get("id") or "unnamed_case")
        expected_error = str(case.get("expected_error") or "")
        materials = apply_case(base_materials, case)
        fixture_errors: list[str] = []
        created_fixtures = material_fixtures(case, benchmark_dir, base_path.parent, fixture_errors)
        if fixture_errors:
            errors.extend([f"{case_id}: {item}" for item in fixture_errors])
        ok, case_errors, case_warnings = validate_patent_application_materials.validate(materials, base_path.parent)
        for path in created_fixtures:
            try:
                path.unlink()
            except OSError as exc:
                errors.append(f"{case_id}: material_fixture_cleanup_failed: {exc}")
        warnings.extend([f"{case_id}: {item}" for item in case_warnings])
        if ok:
            errors.append(f"{case_id}: rejection_case_unexpectedly_passed")
        if expected_error and not any(expected_error in item for item in case_errors):
            errors.append(f"{case_id}: expected_error_not_found: {expected_error}")
        if not expected_error:
            errors.append(f"{case_id}: expected_error_missing")

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
