# Case Package Protocol

Use this reference when raw invention materials arrive from a user, email, API, or batch import.

## Purpose

The case package protocol standardizes raw materials before drafting, AI legal/compliance confirmation, filing package generation, or submission planning. It creates a stable directory layout, source material manifest, intake report, initial filing status, and artifact hash manifest.

## Standard Folders

- `00-intake/source-files`
- `01-normalized`
- `02-draft`
- `03-legal`
- `04-package`
- `05-official-preflight`
- `06-adapter`
- `07-receipts`
- `08-docket`
- `09-portfolio`
- `audit`

## Command

```bash
python -X utf8 scripts/prepare_case_package.py raw-input --case-id CASE-001 --received-from "R&D team" --output-dir cases/CASE-001 --json
```

## Outputs

- `case-package-manifest.json`
- `01-normalized/source-material-manifest.json`
- `filing-status.json`
- `intake-report.md`
- `artifact-hashes.json`

## Source Material File Binding

- Raw intake copying must reject symlinks or linked files. Every copied source file must resolve inside the raw input directory, and every package target path must resolve inside `00-intake/source-files`.
- Every received source material must carry an exact lowercase `sha256:<64 hex>` hash.
- Every source material filename must be a safe relative path inside the case package/source-material base. Reject absolute paths, `..` traversal, and resolved paths outside the allowed intake root.
- `source_package_hash`, material hashes, chain-of-custody hashes, and claim-support evidence hashes must use exact lowercase `sha256:<64 hex>` values, not descriptive placeholders.
- `source_package_hash` must equal the SHA-256 of sorted `filename<TAB>hash<TAB>bytes` rows for all referenced material files when local files are available.
- When a local base directory is available, `scripts/validate_source_material_manifest.py` must recompute each referenced source file hash and reject missing or mismatched files.
- Reference-patent or prior-art files may be retained for novelty comparison, but they must not be marked as applicant-owned claim support.
- Claim-support links must point to known materials that are allowed for claim support; links to prior-art/reference materials must fail.

## Boundaries

- Intake packages are `intake_received` only.
- Filing is not allowed at intake.
- `filing-status.json` preserves `legal_gate_mode=ai_self_filing_no_external_lawyer` and `external_lawyer_involved=false`.
- Legal gate defaults to the AI self-filing no-external-lawyer route and remains pending until AI legal/compliance gate confirmation plus applicant authorization exist, or until a separate reviewed-package route supplies counsel/patent-agent review.
- Intake reports and source manifests must not default to attorney, lawyer, counsel, patent-agent, or patent agent review wording.
- Official system touch, submission, receipt capture, and application number are all false.

## Validators

Run:

```bash
python -X utf8 scripts/validate_case_package_manifest.py case-package-manifest.json --json
python -X utf8 scripts/validate_source_material_manifest.py 01-normalized/source-material-manifest.json --base-dir . --json
```

For benchmark folders, run `scripts/validate_case_package_benchmark.py`.

For source-material rejection coverage, run:

```bash
python -X utf8 scripts/validate_source_material_file_binding_rejection_benchmark.py benchmarks/source-material-file-binding-rejection --json
```

This benchmark must reject missing source files, unsafe material filenames, mismatched material hashes, source-package hash mismatches, malformed SHA-256 fields, unknown claim-support material IDs, and prior-art/reference material used as own claim support.
