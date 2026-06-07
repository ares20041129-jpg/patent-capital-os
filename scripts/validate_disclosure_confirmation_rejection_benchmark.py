#!/usr/bin/env python3
"""Validate rejection cases for disclosure confirmation packets."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import validate_artifact_hash_manifest
import validate_disclosure_confirmation_packet

PATH_TOKEN_RE = re.compile(r"([A-Za-z0-9_]+)(?:\[(\d+)\])?")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def path_tokens(dotted: str) -> list[tuple[str, int | None]]:
    tokens: list[tuple[str, int | None]] = []
    for part in dotted.split("."):
        match = PATH_TOKEN_RE.fullmatch(part)
        if not match:
            raise ValueError(f"invalid_mutation_path: {dotted}")
        index = int(match.group(2)) if match.group(2) is not None else None
        tokens.append((match.group(1), index))
    return tokens


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur: Any = data
    tokens = path_tokens(dotted)
    for key, index in tokens[:-1]:
        if not isinstance(cur, dict):
            raise ValueError(f"mutation_parent_not_object: {dotted}")
        cur = cur.setdefault(key, [] if index is not None else {})
        if index is not None:
            if not isinstance(cur, list) or index >= len(cur):
                raise ValueError(f"mutation_index_out_of_range: {dotted}")
            cur = cur[index]
    key, index = tokens[-1]
    if not isinstance(cur, dict):
        raise ValueError(f"mutation_target_parent_not_object: {dotted}")
    if index is None:
        cur[key] = value
        return
    target = cur.setdefault(key, [])
    if not isinstance(target, list) or index >= len(target):
        raise ValueError(f"mutation_index_out_of_range: {dotted}")
    target[index] = value


def remove_path(data: dict[str, Any], dotted: str) -> None:
    cur: Any = data
    tokens = path_tokens(dotted)
    for key, index in tokens[:-1]:
        if not isinstance(cur, dict) or key not in cur:
            return
        cur = cur[key]
        if index is not None:
            if not isinstance(cur, list) or index >= len(cur):
                return
            cur = cur[index]
    key, index = tokens[-1]
    if not isinstance(cur, dict) or key not in cur:
        return
    if index is None:
        cur.pop(key, None)
        return
    target = cur.get(key)
    if isinstance(target, list) and index < len(target):
        target.pop(index)


def apply_case(base: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    packet = copy.deepcopy(base)
    for dotted in case.get("remove_paths", []):
        remove_path(packet, str(dotted))
    mutations = case.get("mutations") if isinstance(case.get("mutations"), dict) else {}
    for dotted, value in mutations.items():
        set_path(packet, str(dotted), value)
    set_operations = case.get("set_operations") if isinstance(case.get("set_operations"), list) else []
    for operation in set_operations:
        if not isinstance(operation, dict):
            raise ValueError("set_operation_must_be_object")
        set_path(packet, str(operation.get("path") or ""), operation.get("value"))
    return packet


def resolve_path(base_dir: Path, value: Any) -> Path:
    path = Path(str(value or ""))
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path


def validate(benchmark_dir: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    spec_path = benchmark_dir / "rejection-cases.json"
    hashes_path = benchmark_dir / "artifact-hashes.json"
    if not spec_path.exists():
        return False, [f"missing_file: {spec_path}"], warnings

    spec = load_json(spec_path)
    base_packet_path = resolve_path(benchmark_dir, spec.get("base_packet"))
    scaffold_path = resolve_path(benchmark_dir, spec.get("scaffold"))
    expected_hash = sha256_file(scaffold_path) if scaffold_path.exists() else ""
    if not scaffold_path.exists():
        errors.append(f"missing_scaffold: {scaffold_path}")

    if not base_packet_path.exists():
        errors.append(f"missing_base_packet: {base_packet_path}")
        base_packet: dict[str, Any] = {}
    else:
        base_packet = load_json(base_packet_path)
        base_ok, base_errors, base_warnings = validate_disclosure_confirmation_packet.validate(base_packet, expected_hash)
        if not base_ok:
            errors.extend([f"base_packet_should_pass: {item}" for item in base_errors])
        warnings.extend([f"base_packet: {item}" for item in base_warnings])

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
        try:
            packet = apply_case(base_packet, case)
        except Exception as exc:
            errors.append(f"{case_id}: mutation_failed: {exc}")
            continue
        ok, case_errors, case_warnings = validate_disclosure_confirmation_packet.validate(packet, expected_hash)
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
