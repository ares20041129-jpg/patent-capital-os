# Case Intake Orchestration

Use this reference when raw invention materials should be processed in one offline command before drafting or filing.

## Purpose

Case intake orchestration joins:

- raw material packaging;
- source material hashing;
- invention disclosure scaffold generation;
- dry-run queue validation;
- intake orchestration reporting;
- artifact hash manifest creation.

Raw material packaging must reject symlinks or linked files and must copy only source files that resolve inside the raw input directory into package targets that resolve inside `00-intake/source-files`.

It is an intake and analysis control plane. It is not patent drafting, legal approval, filing-readiness approval, official submission, receipt capture, or application-number evidence.

## Command

```bash
python -X utf8 scripts/orchestrate_case_intake.py raw-input --case-id CASE-001 --received-from "R&D team" --output-dir out/case-intake --json
```

## Outputs

- `case-package/case-package-manifest.json`
- `case-package/01-normalized/source-material-manifest.json`
- `case-package/filing-status.json`
- `case-package/intake-report.md`
- `disclosure-normalization-scaffold/invention-disclosure-scaffold.json`
- `disclosure-normalization-scaffold/normalization-report.md`
- `case-queue.json`
- `batch-processor-result.json`
- `intake-orchestration-report.md`
- `artifact-hashes.json`

## Required Invariants

- Case status remains `intake_received`.
- Disclosure status remains `scaffold_pending_confirmation`.
- `legal_gate_mode=ai_self_filing_no_external_lawyer` is preserved on the case package, disclosure scaffold, queue item, and batch result row.
- `external_lawyer_involved=false` is preserved on the case package, disclosure scaffold, queue item, and batch result row.
- `filing_allowed=false`.
- `draft_generation_allowed=false`.
- `official_system_touched=false`.
- `official_submission_performed=false`.
- Inventor, applicant/ownership, no-copying, evidence, secrecy, and AI legal/compliance confirmations remain pending unless supplied as explicit structured evidence.
- Intake orchestration must not default to attorney, lawyer, counsel, patent-agent, or patent agent review wording in reports, source manifests, or disclosure scaffolds.

## Validator

Run:

```bash
python -X utf8 scripts/validate_case_intake_orchestration_benchmark.py benchmarks/case-package-orchestration-dry-run --json
```

Passing this validator means the intake workflow is auditable and locally validated. It does not mean the case can be drafted, filed, submitted, receipted, or docketed as an application.
