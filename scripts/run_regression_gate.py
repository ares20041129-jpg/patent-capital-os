#!/usr/bin/env python3
"""Run the Patent Capital OS local regression gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import build_case_queue
import validate_artifact_hash_manifest


SCAN_ROOTS = ["scripts", "assets", "benchmarks", "references", "SKILL.md", "test-prompts.json"]
PLACEHOLDER_OR_SECRET_PATTERN = "|".join(
    [
        "TO" + "DO",
        "FIX" + "ME",
        "pass" + r"word\s*=",
        "session" + r"_token\s*=",
        "private" + r"_key\s*=",
    ]
)
FORBIDDEN_SCANS = [
    (
        "placeholder_or_secret_assignment",
        re.compile(PLACEHOLDER_OR_SECRET_PATTERN, re.IGNORECASE),
    ),
    (
        "external_lawyer_true",
        re.compile(r'external_lawyer_involved"\s*:\s*true|external_lawyer_involved:\s*true', re.IGNORECASE),
    ),
]
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
STRUCTURED_SHA256_EXTENSIONS = {".json", ".yaml", ".yml"}
INTENTIONAL_NON_EXACT_SHA256_FILES = {
    "rejection-cases.json",
}
INTENTIONAL_NEGATIVE_FIXTURE_MARKERS = {
    "rejection",
    "unsafe-rejection",
    "mock-rejection",
    "readiness-bypass-rejection",
}
DANGEROUS_TRUE_FIELDS = {
    "bypasses_access_controls",
    "captcha_bypass",
    "external_lawyer_involved",
    "generator_adapter_execution_performed",
    "generator_official_submission_performed",
    "generator_official_system_touched",
    "mfa_secret_in_request",
    "private_keys_in_request",
    "raw_credentials_in_request",
    "session_token_in_request",
    "stores_credentials",
}


def rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_item(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_manifest(output_dir: Path, files: list[Path]) -> dict[str, Any]:
    return {
        "case_id": "regression-gate",
        "generated_at": build_case_queue.utc_plus_8_now(),
        "files": [sha256_item(path, output_dir) for path in files],
    }


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for raw in SCAN_ROOTS:
        path = root / raw
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(
                item
                for item in path.rglob("*")
                if item.is_file()
                and "__pycache__" not in item.parts
                and item.suffix.lower() in {".py", ".json", ".md", ".yaml", ".yml", ".tsv", ".txt"}
            )
    return sorted(set(files))


def run_folder_validators(root: Path) -> dict[str, Any]:
    sys.path.insert(0, str((root / "scripts").resolve()))
    results: list[dict[str, Any]] = []
    benchmark_root = root / "benchmarks"
    for folder_name, module_name in sorted(build_case_queue.FOLDER_VALIDATORS.items()):
        folder = benchmark_root / folder_name
        if not folder.exists():
            results.append(
                {
                    "folder": folder_name,
                    "module": module_name,
                    "ok": False,
                    "errors": [f"missing_folder: {folder}"],
                    "warnings": [],
                }
            )
            continue
        module = importlib.import_module(module_name)
        ok, errors, warnings = module.validate(folder)
        results.append(
            {
                "folder": folder_name,
                "module": module_name,
                "ok": ok,
                "errors": errors,
                "warnings": warnings,
            }
        )
    failed = [item for item in results if not item["ok"]]
    return {
        "ok": not failed,
        "total": len(results),
        "failed": len(failed),
        "warning_count": sum(len(item["warnings"]) for item in results),
        "failures": failed,
    }


def run_artifact_manifests(root: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for path in sorted((root / "benchmarks").rglob("artifact-hashes.json")):
        ok, errors, warnings = validate_artifact_hash_manifest.validate(path)
        results.append(
            {
                "path": rel(path, root),
                "ok": ok,
                "errors": errors,
                "warnings": warnings,
            }
        )
    failed = [item for item in results if not item["ok"]]
    return {
        "ok": not failed,
        "total": len(results),
        "failed": len(failed),
        "warning_count": sum(len(item["warnings"]) for item in results),
        "failures": failed,
    }


def run_source_compile(root: Path) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    scripts = sorted((root / "scripts").glob("*.py"))
    for script in scripts:
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except Exception as exc:
            failures.append({"script": rel(script, root), "error": str(exc)})
    return {
        "ok": not failures,
        "total": len(scripts),
        "failed": len(failures),
        "failures": failures,
        "mode": "source_compile_no_pyc",
    }


def run_json_parse(root: Path) -> dict[str, Any]:
    paths = [root / "test-prompts.json"]
    for folder in ["assets", "benchmarks", "schemas"]:
        paths.extend(sorted((root / folder).rglob("*.json")))
    failures: list[dict[str, str]] = []
    for path in sorted(set(paths)):
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            failures.append({"path": rel(path, root), "error": str(exc)})
    return {"ok": not failures, "total": len(set(paths)), "failed": len(failures), "failures": failures}


def run_yaml_parse(root: Path) -> dict[str, Any]:
    paths: list[Path] = []
    for folder in ["assets", "benchmarks", "schemas"]:
        for suffix in ["*.yaml", "*.yml"]:
            paths.extend(sorted((root / folder).rglob(suffix)))
    failures: list[dict[str, str]] = []
    for path in sorted(set(paths)):
        try:
            load_structured_file(path)
        except Exception as exc:
            failures.append({"path": rel(path, root), "error": str(exc)})
    return {"ok": not failures, "total": len(set(paths)), "failed": len(failures), "failures": failures}


def load_structured_file(path: Path) -> Any:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8-sig"))
    if path.suffix.lower() in {".yaml", ".yml"}:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise RuntimeError(f"unsupported_structured_file: {path}")


def collect_non_exact_sha256(value: Any, trail: str, matches: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            collect_non_exact_sha256(child, f"{trail}.{key}" if trail else str(key), matches)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            collect_non_exact_sha256(child, f"{trail}[{index}]", matches)
    elif isinstance(value, str) and value.startswith("sha256:") and not SHA256_RE.fullmatch(value):
        matches.append({"field": trail, "value": value})


def is_intentional_negative_fixture(path: Path) -> bool:
    if path.name in INTENTIONAL_NON_EXACT_SHA256_FILES:
        return True
    return any(any(marker in part for marker in INTENTIONAL_NEGATIVE_FIXTURE_MARKERS) for part in path.parts)


def run_structured_sha256_placeholder_scan(root: Path) -> dict[str, Any]:
    """Reject descriptive sha256 placeholders in positive structured benchmarks."""

    benchmark_root = root / "benchmarks"
    matches: list[dict[str, str]] = []
    warnings: list[str] = []
    total = 0
    for path in sorted(benchmark_root.rglob("*")):
        if (
            not path.is_file()
            or path.suffix.lower() not in STRUCTURED_SHA256_EXTENSIONS
            or is_intentional_negative_fixture(path)
        ):
            continue
        total += 1
        try:
            data = load_structured_file(path)
        except Exception as exc:
            warnings.append(f"{rel(path, root)}: structured_load_skipped: {exc}")
            continue
        before = len(matches)
        collect_non_exact_sha256(data, "", matches)
        for item in matches[before:]:
            item["path"] = rel(path, root)

    return {
        "ok": not matches,
        "total": total,
        "failed": len(matches),
        "warning_count": len(warnings),
        "matches": matches,
        "warnings": warnings,
    }


def collect_dangerous_true_fields(value: Any, trail: str, matches: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_trail = f"{trail}.{key}" if trail else str(key)
            if key in DANGEROUS_TRUE_FIELDS and child is True:
                matches.append({"field": child_trail, "value": "true"})
            collect_dangerous_true_fields(child, child_trail, matches)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            collect_dangerous_true_fields(child, f"{trail}[{index}]", matches)


def run_structured_dangerous_true_scan(root: Path) -> dict[str, Any]:
    """Reject dangerous true booleans in positive structured benchmarks."""

    benchmark_root = root / "benchmarks"
    matches: list[dict[str, str]] = []
    warnings: list[str] = []
    total = 0
    for path in sorted(benchmark_root.rglob("*")):
        if (
            not path.is_file()
            or path.suffix.lower() not in STRUCTURED_SHA256_EXTENSIONS
            or is_intentional_negative_fixture(path)
        ):
            continue
        total += 1
        try:
            data = load_structured_file(path)
        except Exception as exc:
            warnings.append(f"{rel(path, root)}: structured_load_skipped: {exc}")
            continue
        before = len(matches)
        collect_dangerous_true_fields(data, "", matches)
        for item in matches[before:]:
            item["path"] = rel(path, root)

    return {
        "ok": not matches,
        "total": total,
        "failed": len(matches),
        "warning_count": len(warnings),
        "matches": matches,
        "warnings": warnings,
    }


def run_forbidden_scans(root: Path) -> dict[str, Any]:
    files = iter_text_files(root)
    results: list[dict[str, Any]] = []
    for label, pattern in FORBIDDEN_SCANS:
        matches: list[str] = []
        for path in files:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                matches.append(f"{rel(path, root)}: read_error: {exc}")
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                if path.name == "run_regression_gate.py" and "re.compile" in line:
                    continue
                if pattern.search(line):
                    matches.append(f"{rel(path, root)}:{line_number}:{line.strip()}")
        results.append({"label": label, "ok": not matches, "matches": matches})
    failed = [item for item in results if not item["ok"]]
    return {"ok": not failed, "total": len(results), "failed": len(failed), "results": results}


def run(root: Path) -> dict[str, Any]:
    checks = {
        "folder_validators": run_folder_validators(root),
        "artifact_manifests": run_artifact_manifests(root),
        "source_compile": run_source_compile(root),
        "json_parse": run_json_parse(root),
        "yaml_parse": run_yaml_parse(root),
        "structured_sha256_placeholders": run_structured_sha256_placeholder_scan(root),
        "structured_dangerous_true_fields": run_structured_dangerous_true_scan(root),
        "forbidden_scans": run_forbidden_scans(root),
    }
    return {
        "ok": all(item["ok"] for item in checks.values()),
        "checks": checks,
        "official_system_touched": False,
        "official_submission_performed": False,
        "external_lawyer_involved": False,
    }


def render_report(result: dict[str, Any]) -> str:
    checks = result.get("checks") if isinstance(result.get("checks"), dict) else {}
    rows = []
    for name, check in checks.items():
        if not isinstance(check, dict):
            continue
        rows.append(
            "| {name} | {ok} | {total} | {failed} | {warnings} |".format(
                name=name,
                ok="pass" if check.get("ok") else "fail",
                total=check.get("total", 0),
                failed=check.get("failed", 0),
                warnings=check.get("warning_count", 0),
            )
        )

    lines = [
        "# Regression Gate Evidence Report",
        "",
        f"Gate result: {'pass' if result.get('ok') else 'fail'}",
        f"Official system touched: {'yes' if result.get('official_system_touched') else 'no'}",
        f"Official submission performed: {'yes' if result.get('official_submission_performed') else 'no'}",
        f"External lawyer involved: {'yes' if result.get('external_lawyer_involved') else 'no'}",
        "AI self-filing legal gate boundary preserved: yes",
        "",
        "## Check Summary",
        "",
        "| Check | Result | Total | Failed | Warnings |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
        "## Boundary",
        "",
        "This local evidence bundle records regression verification only. It does not log in, upload, sign, pay, submit, capture a real receipt, or create a real application number.",
        "",
        "## Generated Artifacts",
        "",
        "- regression-gate-result.json",
        "- regression-gate-report.md",
        "- artifact-hashes.json",
        "",
        "`artifact-hashes.json` is the authoritative hash manifest for this evidence bundle.",
    ]
    return "\n".join(lines) + "\n"


def write_evidence_bundle(result: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "regression-gate-result.json"
    report_path = output_dir / "regression-gate-report.md"
    manifest_path = output_dir / "artifact-hashes.json"

    write_json(result_path, result)
    report_path.write_text(render_report(result), encoding="utf-8")
    final_manifest = build_manifest(output_dir, [result_path, report_path])
    write_json(manifest_path, final_manifest)
    manifest_ok, manifest_errors, manifest_warnings = validate_artifact_hash_manifest.validate(manifest_path)

    return {
        "ok": manifest_ok,
        "output_dir": str(output_dir),
        "artifacts": {
            "regression_gate_result": str(result_path),
            "regression_gate_report": str(report_path),
            "artifact_hashes": str(manifest_path),
        },
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run(args.root.resolve())
    gate_ok = result["ok"]
    exit_ok = gate_ok
    if args.output_dir:
        bundle = write_evidence_bundle(result, args.output_dir.resolve())
        exit_ok = gate_ok and bundle["ok"]
        result = {**result, "gate_ok": gate_ok, "ok": exit_ok, "evidence_bundle": bundle}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if exit_ok else "FAIL")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if exit_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
