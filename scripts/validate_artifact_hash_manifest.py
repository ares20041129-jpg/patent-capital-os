#!/usr/bin/env python3
"""Validate artifact-hashes.json against current benchmark files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate(manifest_path: Path) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not manifest_path.exists():
        return False, [f"missing_file: {manifest_path}"], warnings

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"manifest_json_invalid: {exc}"], warnings
    if not isinstance(manifest, dict):
        return False, ["manifest_not_object"], warnings

    root = manifest_path.parent
    root_resolved = root.resolve()

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        return False, ["manifest_files_missing"], warnings

    seen_paths: set[str] = set()
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            errors.append(f"manifest_item_not_object: {index}")
            continue
        rel = item.get("path")
        expected_hash = item.get("sha256")
        expected_bytes = item.get("bytes")
        if not isinstance(rel, str) or not rel:
            errors.append(f"manifest_item_missing_or_invalid_path: {index}")
            continue
        if rel in seen_paths:
            errors.append(f"duplicate_artifact_path: {rel}")
        seen_paths.add(rel)

        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            errors.append(f"unsafe_artifact_path: {rel}")
            continue

        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
            errors.append("manifest_item_missing_path_or_sha256")
            continue
        bytes_valid = expected_bytes is None or (
            isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) and expected_bytes >= 0
        )
        if not bytes_valid:
            errors.append(f"invalid_byte_count: {rel}")
            continue

        path = (root / rel_path).resolve()
        if not is_relative_to(path, root_resolved):
            errors.append(f"artifact_path_outside_manifest_root: {rel}")
            continue
        if not path.exists():
            errors.append(f"missing_artifact: {rel}")
            continue
        if not path.is_file():
            errors.append(f"artifact_not_file: {rel}")
            continue
        data = path.read_bytes()
        actual_hash = "sha256:" + hashlib.sha256(data).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"hash_mismatch: {rel}")
        if expected_bytes is not None and len(data) != expected_bytes:
            errors.append(f"byte_count_mismatch: {rel}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors, warnings = validate(args.manifest)
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
