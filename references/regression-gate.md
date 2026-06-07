# Regression Gate

Use this reference before treating Patent Capital OS changes as locally verified.

## Purpose

The regression gate turns scattered manual checks into one local, repeatable quality gate. It does not log in, upload, sign, pay, submit, touch an official system, capture a real receipt, or create a real application number.

## Command

```bash
python -X utf8 scripts/run_regression_gate.py --json
```

For an auditable local evidence bundle:

```bash
python -X utf8 scripts/run_regression_gate.py --output-dir out/regression-gate --json
python -X utf8 scripts/validate_artifact_hash_manifest.py out/regression-gate/artifact-hashes.json --json
```

The bundle writes `regression-gate-result.json`, `regression-gate-report.md`, and `artifact-hashes.json`. Keep the bundle outside `benchmarks/` unless it is intentionally promoted to a static benchmark fixture.

## Checks

- Runs every benchmark folder validator registered in `build_case_queue.FOLDER_VALIDATORS`.
- Validates every benchmark `artifact-hashes.json`, including relative in-root artifact paths, exact lowercase `sha256:<64 hex>` values, duplicate path rejection, and byte-count consistency.
- Compiles every script from source without writing `.pyc` files.
- Parses JSON artifacts under `assets/`, `benchmarks/`, `schemas/`, and `test-prompts.json`.
- Parses YAML artifacts under `assets/`, `benchmarks/`, and `schemas/`.
- Scans positive structured benchmark JSON/YAML files for descriptive `sha256:*` placeholders; intentional negative fixtures are excluded.
- Scans positive structured benchmark JSON/YAML files for dangerous `true` booleans such as generator-side official action, external-lawyer involvement, credential leakage, or official-control bypass flags; intentional negative fixtures are excluded.
- Scans for unresolved placeholder markers, obvious secret assignments, and any external-lawyer true marker.

## Required Result

The gate must return:

- `ok=true`
- `official_system_touched=false`
- `official_submission_performed=false`
- `external_lawyer_involved=false`
- zero failed folder validators
- zero failed artifact manifests
- zero unsafe, duplicate, malformed-hash, or invalid-byte artifact manifest entries
- zero failed source-compile checks
- zero failed JSON parse checks
- zero failed YAML parse checks
- zero positive structured benchmark `sha256:*` placeholder matches
- zero positive structured benchmark dangerous `true` boolean matches
- zero failed forbidden scans
- if `--output-dir` is used, `evidence_bundle.ok=true` and the generated `artifact-hashes.json` validates

Warnings are allowed only when they are expected benchmark/mock/shape-test warnings and do not claim real official filing evidence.
