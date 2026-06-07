#!/usr/bin/env python3
"""Validate source material provenance before patent generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_packet(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("YAML input requires PyYAML. Use JSON or install PyYAML.") from exc
        loaded = yaml.safe_load(text)
        return loaded or {}
    raise RuntimeError("Unsupported input format. Use .json, .yaml, or .yml")


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def require_hash(value: Any, label: str, errors: list[str]) -> None:
    if is_blank(value):
        errors.append(f"missing_required_field: {label}")
    elif not SHA256_RE.fullmatch(str(value)):
        errors.append(f"{label}_must_be_sha256_64_hex")


def material_search_roots(base_dir: Path) -> list[Path]:
    base = base_dir.resolve()
    roots = [base]
    if base.name == "01-normalized":
        roots.append(base.parent.resolve())
    unique: list[Path] = []
    for root in roots:
        if root not in unique:
            unique.append(root)
    return unique


def resolve_material_path(base_dir: Path, raw_path: Any) -> Path:
    raw = str(raw_path or "")
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe_material_filename")
    roots = material_search_roots(base_dir)
    for root in roots:
        candidate = (root / path).resolve()
        if not is_relative_to(candidate, root):
            raise ValueError("material_path_outside_base_dir")
        if candidate.exists():
            return candidate
    return (roots[0] / path).resolve()


def is_reference_or_prior_art(item: dict[str, Any]) -> bool:
    material_type = str(item.get("type") or "").lower()
    return "prior_art" in material_type or "reference" in material_type


def compute_source_package_hash(rows: list[tuple[str, str, int]]) -> str:
    payload = "\n".join(f"{filename}\t{file_hash}\t{byte_count}" for filename, file_hash, byte_count in sorted(rows))
    return sha256_bytes(payload.encode("utf-8"))


def validate(data: dict[str, Any], base_dir: Path | None = None) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    materials_by_id: dict[str, dict[str, Any]] = {}
    package_hash_rows: list[tuple[str, str, int]] = []

    for key in ["case_id", "received_at", "received_from", "confidentiality_marker", "source_package_hash"]:
        if is_blank(data.get(key)):
            errors.append(f"missing_required_field: {key}")
    require_hash(data.get("source_package_hash"), "source_package_hash", errors)

    materials = data.get("materials")
    if not isinstance(materials, list) or not materials:
        errors.append("missing_required_field: materials")
    else:
        seen_ids: set[str] = set()
        for index, item in enumerate(materials, start=1):
            if not isinstance(item, dict):
                errors.append(f"material_{index}_must_be_object")
                continue
            for key in ["material_id", "filename", "type", "received_at", "hash", "source_owner", "confidentiality"]:
                if is_blank(item.get(key)):
                    errors.append(f"material_{index}_missing_required_field: {key}")
            material_id = str(item.get("material_id") or "")
            if material_id in seen_ids:
                errors.append(f"duplicate_material_id: {material_id}")
            seen_ids.add(material_id)
            if material_id:
                materials_by_id[material_id] = item
            if is_reference_or_prior_art(item) and item.get("usable_for_claim_support") is True:
                errors.append(f"material_{index}_prior_art_must_not_be_usable_for_claim_support")
            if item.get("usable_for_claim_support") is not True:
                warnings.append(f"material_{index}_not_marked_usable_for_claim_support")
            item_hash = item.get("hash")
            require_hash(item_hash, f"material_{index}.hash", errors)
            if base_dir is not None and not is_blank(item.get("filename")) and not is_blank(item_hash):
                try:
                    path = resolve_material_path(base_dir.resolve(), item.get("filename"))
                except ValueError as exc:
                    errors.append(f"material_{index}_{exc}")
                    continue
                if not path.exists():
                    errors.append(f"material_{index}_file_not_found: {item.get('filename')}")
                elif sha256_file(path) != item_hash:
                    errors.append(f"material_{index}_hash_mismatch: {item.get('filename')}")
                elif SHA256_RE.fullmatch(str(item_hash)):
                    package_hash_rows.append((str(item.get("filename")), str(item_hash), path.stat().st_size))

        if (
            base_dir is not None
            and len(package_hash_rows) == len(materials)
            and SHA256_RE.fullmatch(str(data.get("source_package_hash") or ""))
        ):
            if compute_source_package_hash(package_hash_rows) != data.get("source_package_hash"):
                errors.append("source_package_hash_mismatch")

    chain = data.get("chain_of_custody")
    if not chain:
        warnings.append("chain_of_custody_missing")
    elif isinstance(chain, list):
        for index, item in enumerate(chain, start=1):
            if isinstance(item, dict):
                for key in ["input_hash", "output_hash"]:
                    if not is_blank(item.get(key)):
                        require_hash(item.get(key), f"chain_of_custody_{index}.{key}", errors)
    else:
        errors.append("chain_of_custody_must_be_list")

    links = data.get("claim_support_links")
    if isinstance(links, list):
        for index, item in enumerate(links, start=1):
            if isinstance(item, dict):
                material_id = str(item.get("material_id") or "")
                material = materials_by_id.get(material_id)
                if not material_id:
                    errors.append(f"claim_support_link_{index}_missing_material_id")
                elif material is None:
                    errors.append(f"claim_support_link_{index}_unknown_material_id: {material_id}")
                elif material.get("usable_for_claim_support") is not True:
                    errors.append(f"claim_support_link_{index}_material_not_usable_for_claim_support: {material_id}")
                if not is_blank(item.get("evidence_hash")):
                    require_hash(item.get("evidence_hash"), f"claim_support_link_{index}.evidence_hash", errors)

    return len(errors) == 0, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--base-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        manifest_path = args.manifest.resolve()
        base_dir = args.base_dir.resolve() if args.base_dir else manifest_path.parent
        ok, errors, warnings = validate(load_packet(manifest_path), base_dir=base_dir)
    except Exception as exc:
        ok, errors, warnings = False, [str(exc)], []

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
