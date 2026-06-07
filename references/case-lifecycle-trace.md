# Case Lifecycle Trace

Use this reference when auditing a complete patent case from intake to final filing status.

## Purpose

The lifecycle trace ties together individual gates so a case cannot skip from draft to filing, from preflight to receipt, or from receipt to application number without evidence. It is an audit artifact, not a filing action.

In the full pre-submission pipeline, the trace is generated through the approved-adapter preflight stage and must pass before the pipeline result can report `pre_submission_lifecycle_gate=passed`. That pre-submission trace must not include adapter execution, receipt, or application-number stages.

## Required Sequence

1. Source intake.
2. Draft generation.
3. Legal authorization.
4. Filing package validation.
5. Official-channel preflight.
6. Approved-adapter preflight, when automation is used.
7. Adapter execution result or authorized human submission evidence.
8. Receipt capture.
9. Application-number or acceptance evidence.

## Invariants

- Legal gate is never skipped.
- Final, reviewed, and submitted package hashes stay consistent.
- Approved-adapter, adapter-execution, receipt, and application-number stages preserve the same official session authorization hash and official session-reference hash when automation is used.
- When a case uses cited-patent reference-delta drafting, every stage from legal authorization onward preserves the same `reference_patent_delta_hash`, positive row and claim-element counts, and `reference_delta_boundary_preserved=true`.
- When application materials are generated, every official-preflight or later stage preserves the same `application_materials_hash`.
- Each stage `artifact_hash` matches the actual referenced artifact file.
- Every lifecycle hash field uses exact lowercase `sha256:<64 hex>` values; descriptive `sha256:` placeholders are invalid lifecycle evidence.
- Receipt evidence does not appear before submission.
- Application number does not appear before receipt.
- Mock evidence is marked as mock and cannot be treated as production evidence.

## Validator

Run:

```bash
python -X utf8 scripts/validate_case_lifecycle_trace.py case-lifecycle-trace.json --json
```

For benchmark folders, run `scripts/validate_case_lifecycle_benchmark.py`.

For rejection benchmark folders, run `scripts/validate_case_lifecycle_rejection_benchmark.py`.

## Trace Generator

For the standard benchmark chain, use:

```bash
python -X utf8 scripts/prepare_case_lifecycle_trace.py --output-dir benchmarks/generated-case-lifecycle-trace --json
```

For the AI self-filing reference-delta benchmark chain, use:

```bash
python -X utf8 scripts/prepare_case_lifecycle_trace.py --route ai_self_filing_no_external_lawyer --reference-delta --output-dir benchmarks/ai-self-filing-lifecycle-trace-reference-delta --json
```

The generator creates:

- `case-lifecycle-trace.json`
- `lifecycle-report.md`
- `artifact-hashes.json`

This is an audit artifact only. It must not touch official systems, perform submission, capture live receipts, or claim a real application number. Benchmark traces must use `trace_type=benchmark_mock` and mark every stage with `benchmark_mock=true`.

## Rejection Gate

Use `benchmarks/case-lifecycle-rejection-gate/` to prove the lifecycle validator rejects:

- official session-reference mismatch;
- stage artifact hash mismatch;
- receipt evidence before submission evidence;
- submitted package hash mismatch.
