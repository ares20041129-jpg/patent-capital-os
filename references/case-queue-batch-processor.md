# Case Queue Batch Processor

Use this reference when receiving multiple patent cases in one batch.

## Principle

Batch processing coordinates cases; it does not weaken gates. Each case keeps its own artifacts, hashes, legal status, and next allowed state.

## Queue Rules

- Every queue item must have a unique `case_id`.
- Queue execution mode is `dry_run`, `handoff`, or `approved_adapter`.
- `dry_run` and `handoff` queues must not submit, sign, pay, or touch official systems.
- `approved_adapter` queues are evidence-only in the offline runner: they must set `approved_adapter_evidence_mode=true`, must not allow official system touch or submission, and may only validate independently supplied adapter execution evidence already at `submitted_pending_receipt`.
- `dry_run` lifecycle audits may inspect completed submission/receipt/application-number states only when `expected_outcome=lifecycle_audit` and `current_status == target_status`.
- A failed case must not block reporting on other cases, but it must not be silently skipped.
- Every case output must include decision, status, validators, errors/warnings, next action, and owner.
- Queue items and case results must preserve `legal_gate_mode`.
- The default AI self-filing queue path must carry `external_lawyer_involved=false`.
- Batch summary counts must match item results.

## Queue Item Outcomes

| Outcome | Meaning |
| --- | --- |
| case_package_intake | Raw materials are normalized into a standard case package |
| disclosure_scaffold | Case package has been normalized into a pending-confirmation invention disclosure scaffold |
| case_intake_orchestration | Raw materials have been packaged, scaffolded, validated, reported, and hashed offline |
| confirmed_disclosure | Inventor, ownership, no-copying, evidence, secrecy, and draft-only legal review confirmations support draft generation only |
| draft_package | Draft application and claim support map are generated for AI self-filing legal/compliance authorization only |
| draft_only | Draft artifacts may be produced; legal filing blocked |
| deficiency | Missing evidence or gate failure |
| package_validation | Legal packet exists; package validation is next |
| patent_application_materials | Validated package has generated source-bound claims, specification, abstract, drawings, request metadata, and XML readiness materials |
| official_preflight | Package valid; official-channel preflight is next |
| approved_adapter_preflight | Approved adapter pre-execution gate is next or passed |
| adapter_execution | Approved adapter execution result is next or pending receipt |
| application_number | Official receipt and application-number evidence are present |
| lifecycle_audit | End-to-end case lifecycle trace is ready for audit |
| workflow_orchestration | Queue build, local run, report, and hash manifest are ready for audit |
| inbox_to_handoff | Received raw-material case inbox has produced read-only handoff packages for all cases |
| inbox_handoff_index | Received raw-material case inbox has a final read-only handoff index for production control-plane consumption |
| inbox_to_handoff_rejection | Unsafe inbox-to-handoff inputs are rejected before pre-submission generation |
| skill_completion_audit | The local skill loop has completion evidence for no-auto-submit handoff |
| pre_submission_to_handoff | Full pre-submission pipeline plus read-only handoff package are ready for audit |
| pre_submission_handoff_package | Read-only pre-submission execution handoff package is ready for audit |
| pre_submission_handoff_rejection | Malformed pre-submission handoff packages are rejected before adapter execution |
| handoff | Ready for authorized human action |
| dry_run_ok | Adapter contract validates without touching official system |
| blocked | Cannot proceed until errors are cured |

## Stop Conditions

Stop a case when:

- Required validator fails.
- Target state exceeds authorization.
- Queue asks for official submission in dry-run or handoff mode.
- Case attempts to share artifacts or hashes with another case without explicit linkage.
- Any request includes forbidden adapter fields.

## Required Batch Output

- Queue ID.
- Execution mode.
- Total cases and per-outcome counts.
- Per-case result rows.
- Batch-level errors and warnings.
- Whether any official system was touched.
- Whether any official submission was performed.
- Artifact hash manifest.

## Offline Runner

Use `scripts/build_case_queue.py` to create a queue from received case folders:

```bash
python -X utf8 scripts/build_case_queue.py --queue-id CASE-QUEUE-001 --queue-owner "Patent Capital OS" --execution-mode dry_run --output case-queue.json case-a case-b case-c
```

Builder constraints:

- It reads existing `case-record.json` or `filing-status.json` when present.
- It infers case status, expected outcome, owner, and local validators.
- It preserves or infers `legal_gate_mode` and defaults missing cases to the AI self-filing no-external-lawyer route.
- It writes `external_lawyer_involved=false` unless a source record explicitly says otherwise; AI self-filing dry-run benchmarks must reject any true value.
- It always sets `official_submission_allowed=false`.
- It always sets `official_system_touch_allowed=false`.
- It does not validate official credentials, submit, sign, pay, or claim a receipt.

Use `scripts/run_case_queue.py` to execute a queue locally:

```bash
python -X utf8 scripts/run_case_queue.py benchmarks/case-queue-batch-processor/case-queue.json --json
```

Runner constraints:

- It runs only local validators listed in `required_validators`.
- Validator names must resolve to scripts inside `scripts/`.
- Case folders resolve relative to the queue file.
- `approved_adapter` mode requires `approved_adapter_evidence_mode=true` and validates returned adapter evidence only; it does not execute an adapter.
- Official system touch and official submission fields remain `false`.
- Generator official-system, submission, and adapter-execution fields remain `false`.
- A validator failure blocks only that case and is reported in the batch result.
