# Workflow Orchestration

Use this reference when received case folders should be processed in one offline command. For raw invention materials that have not yet been packaged, use `references/case-intake-orchestration.md` first.

## Purpose

Workflow orchestration joins queue creation, local validation execution, report generation, and artifact hashing. It is a local control-plane command. It does not submit, sign, pay, touch an official system, capture a real receipt, or create an application number.

## Command

```bash
python -X utf8 scripts/orchestrate_case_workflow.py --queue-id CASE-QUEUE-001 --output-dir out/case-queue case-folder-a case-folder-b --json
```

For the AI self-filing path after package validation, generate local application materials and run the independent quality gate with:

```bash
python -X utf8 scripts/orchestrate_application_materials_pipeline.py benchmarks/ai-self-filing-package-validation --draft-package-dir benchmarks/draft-package-generation --provenance-dir benchmarks/ai-self-filing-draft-evidence-provenance --output-dir benchmarks/application-materials-pipeline --json
```

For the full local pre-submission path through local official-channel preflight readiness, approved-adapter preflight, and the pre-submission lifecycle audit gate, but before any adapter execution or automatic submission, run:

```bash
python -X utf8 scripts/orchestrate_pre_submission_pipeline.py raw-input --confirmation-packet-template disclosure-confirmation-packet.json --ai-self-filing-source-template ai-self-filing-source.json --output-dir out/pre-submission-pipeline --case-id CASE-001 --received-from "Applicant" --json
```

When cited patents should shape the draft as boundary evidence, add a reference-delta source:

```bash
python -X utf8 scripts/orchestrate_pre_submission_pipeline.py raw-input --confirmation-packet-template disclosure-confirmation-packet.json --ai-self-filing-source-template ai-self-filing-source.json --reference-delta-source reference-delta-source.json --output-dir out/pre-submission-pipeline-reference-delta --case-id CASE-001 --received-from "Applicant" --json
```

After the full pre-submission pipeline passes, prepare a read-only execution handoff package:

```bash
python -X utf8 scripts/prepare_pre_submission_handoff_package.py out/pre-submission-pipeline --output-dir out/pre-submission-handoff-package --json
```

For one offline command that runs the full pre-submission pipeline and then prepares the read-only handoff package, run:

```bash
python -X utf8 scripts/orchestrate_pre_submission_to_handoff.py raw-input --confirmation-packet-template disclosure-confirmation-packet.json --ai-self-filing-source-template ai-self-filing-source.json --output-dir out/pre-submission-to-handoff --case-id CASE-001 --received-from "Applicant" --json
```

For an inbox of received raw material folders, where each child folder is one case and may include `case-config.json`, run:

```bash
python -X utf8 scripts/orchestrate_inbox_to_handoff.py inbox --output-dir out/inbox-to-handoff --inbox-id INBOX-001 --confirmation-packet-template disclosure-confirmation-packet.json --ai-self-filing-source-template ai-self-filing-source.json --json
```

After inbox-to-handoff passes, generate the final read-only handoff index:

```bash
python -X utf8 scripts/prepare_inbox_handoff_index.py out/inbox-to-handoff --output-dir out/inbox-handoff-index --index-id INBOX-HANDOFF-INDEX-001 --json
```

After the handoff index exists, generate the local skill completion audit:

```bash
python -X utf8 scripts/prepare_skill_completion_audit.py --skill-root . --output-dir out/skill-completion-audit --json
```

## Outputs

- `case-queue.json`
- `batch-processor-result.json`
- `orchestration-report.md`
- `artifact-hashes.json`

The application-materials pipeline outputs:

- `application-materials/`
- `application-materials-quality-gate/`
- `application-materials-pipeline-result.json`
- `application-materials-pipeline-report.md`
- `artifact-hashes.json`

The pre-submission pipeline outputs:

- `raw-input/`
- `case-package/`
- `disclosure-normalization-scaffold/`
- `scaffold-confirmation-to-disclosure/`
- `reference-patent-delta/` when `--reference-delta-source` is supplied
- `draft-package-generation/`
- `draft-evidence-provenance-gate/`
- `abnormal-filing-risk-gate/`
- `ai-self-filing-package-validation/`
- `application-materials-pipeline/`
- `ai-self-filing-official-ready/`
- `ai-self-filing-approved-adapter-preflight/`
- `case-lifecycle-trace/`
- `pre-submission-pipeline-result.json`
- `pre-submission-pipeline-report.md`
- `artifact-hashes.json`

The pre-submission handoff package outputs:

- `pre-submission-handoff-package.json`
- `pre-submission-handoff-report.md`
- `evidence/` copied final package, application materials, official preflight, approved-adapter, lifecycle, audit, docket, and receipt-plan evidence
- `artifact-hashes.json`

The pre-submission-to-handoff orchestration outputs:

- `pre-submission-pipeline/`
- `pre-submission-handoff-package/`
- `pre-submission-to-handoff-result.json`
- `pre-submission-to-handoff-report.md`
- `artifact-hashes.json`

The inbox-to-handoff orchestration outputs:

- `processed-cases/` with one validated pre-submission-to-handoff folder per received case
- `case-queue.json`
- `batch-processor-result.json`
- `inbox-to-handoff-result.json`
- `inbox-to-handoff-report.md`
- `artifact-hashes.json`

The inbox handoff index outputs:

- `inbox-handoff-index.json`
- `inbox-handoff-index.md`
- `artifact-hashes.json`

The skill completion audit outputs:

- `skill-completion-audit.json`
- `skill-completion-audit.md`
- `artifact-hashes.json`

## Required Invariants

- `official_submission_allowed=false` on the queue.
- `official_system_touch_allowed=false` on the queue.
- Every queue item carries `legal_gate_mode`.
- Every queue item has `external_lawyer_involved=false` for the default AI self-filing dry-run path.
- `official_system_touched=false` on the batch result.
- `official_submission_performed=false` on the batch result.
- Every case result preserves `legal_gate_mode` and `external_lawyer_involved=false`.
- Every case result includes validators, errors, warnings, decision, outcome, owner, and next action.
- The artifact hash manifest validates against generated outputs.
- The application-materials pipeline must stop at `package_valid_official_preflight_pending`; official-channel preflight remains a separate gate.
- The pre-submission pipeline must keep `automatic_submission_performed=false`, `adapter_execution_performed=false`, run only local official-channel readiness plus local approved-adapter preflight, and stop at `approved_for_adapter_execution`; adapter execution remains a separate gate.
- The pre-submission pipeline must generate and validate `case-lifecycle-trace/`, set `pre_submission_lifecycle_gate=passed`, and bind `lifecycle_trace_hash` to the actual lifecycle trace file before the case can be treated as approved for adapter execution.
- The pre-submission handoff package must copy and hash-bind the final official documents, source-bound application materials, official preflight, approved-adapter preflight, filing-adapter request, lifecycle trace, receipt plan, audit plan, and docket plan; it must remain read-only and must not claim adapter execution, submission, receipt, or application number.
- The pre-submission-to-handoff orchestration must validate both nested stages, bind the source pre-submission result hash and handoff package hash, remain at `approved_for_adapter_execution`, and still perform no adapter execution, official-system touch, submission, receipt capture, or application-number claim.
- The inbox-to-handoff orchestration must process every child case folder through the pre-submission-to-handoff gate, run a dry-run queue over the generated case outputs, include at least one reference-delta configured case in the benchmark, and preserve `external_lawyer_involved=false` plus no official action flags at both per-case and inbox levels.
- The inbox handoff index must read the inbox result, queue, batch result, and every per-case pre-submission-to-handoff result; it must preserve case status, decision, quality score, reference-delta fields, handoff package hashes, next action, and no official action flags.
- The skill completion audit must cover reference-patent delta, application-materials generation, AI legal/compliance gate, no-external-lawyer mode, batch inbox processing, unsafe inbox rejection, hash binding, read-only handoff, handoff index, runbook, regression gate contract, and official boundary without claiming official submission.
- If `--reference-delta-source` is supplied, `reference_patent_delta_hash` must remain hash-bound through the reference-delta stage, draft package, provenance, abnormal-filing risk, AI self-filing source, application materials, and pre-submission result while reference patents remain boundary evidence only.

## Validator

Run:

```bash
python -X utf8 scripts/validate_workflow_orchestration_benchmark.py benchmarks/workflow-orchestration-dry-run --json
python -X utf8 scripts/validate_application_materials_pipeline_benchmark.py benchmarks/application-materials-pipeline --json
python -X utf8 scripts/validate_pre_submission_pipeline_benchmark.py benchmarks/pre-submission-pipeline --json
python -X utf8 scripts/validate_pre_submission_pipeline_benchmark.py benchmarks/pre-submission-pipeline-reference-delta --json
python -X utf8 scripts/validate_pre_submission_handoff_package.py benchmarks/pre-submission-handoff-package --json
python -X utf8 scripts/validate_pre_submission_handoff_package.py benchmarks/pre-submission-handoff-package-reference-delta --json
python -X utf8 scripts/validate_pre_submission_to_handoff_benchmark.py benchmarks/pre-submission-to-handoff --json
python -X utf8 scripts/validate_pre_submission_to_handoff_benchmark.py benchmarks/pre-submission-to-handoff-reference-delta --json
python -X utf8 scripts/validate_inbox_to_handoff_benchmark.py benchmarks/inbox-to-handoff --json
python -X utf8 scripts/validate_inbox_handoff_index_benchmark.py benchmarks/inbox-handoff-index --json
python -X utf8 scripts/validate_skill_completion_audit_benchmark.py benchmarks/skill-completion-audit --json
python -X utf8 scripts/validate_inbox_to_handoff_rejection_benchmark.py benchmarks/inbox-to-handoff-rejection --json
python -X utf8 scripts/validate_pre_submission_handoff_rejection_benchmark.py benchmarks/pre-submission-handoff-rejection --json
```

This validates the benchmark shape. Production orchestration outputs should additionally run the per-case validators listed in the generated queue.
For pre-submission queue items, the generated queue must run `validate_pre_submission_pipeline_benchmark`, which consumes the nested lifecycle trace hard gate instead of treating `approved_for_adapter_execution` as sufficient by itself.
For pre-submission handoff package queue items, the generated queue must run `validate_pre_submission_handoff_package`, which revalidates the source pre-submission pipeline and the copied read-only handoff evidence.
For pre-submission-to-handoff queue items, the generated queue must run `validate_pre_submission_to_handoff_benchmark`, which validates the nested pipeline, nested handoff package, wrapper result, and top-level manifest without advancing beyond approved-adapter execution readiness.
For inbox-to-handoff queue items, the generated queue must run `validate_inbox_to_handoff_benchmark`, which validates every processed case, the nested queue result, the inbox result, and the top-level manifest without advancing beyond approved-adapter execution readiness.
For inbox-handoff-index queue items, the generated queue must run `validate_inbox_handoff_index_benchmark`, which validates the source inbox, per-case index rows, handoff hashes, quality gate fields, reference-delta preservation, next actions, and boundary flags.
For skill-completion-audit queue items, the generated queue must run `validate_skill_completion_audit_benchmark`, which validates the local closure evidence without running official submission or adapter execution.
For inbox-to-handoff rejection queue items, the generated queue must run `validate_inbox_to_handoff_rejection_benchmark`, proving unsafe inbox config paths, missing raw inputs, empty inboxes, and stale output reuse are blocked before pre-submission generation.
For pre-submission handoff rejection queue items, the generated queue must run `validate_pre_submission_handoff_rejection_benchmark`, proving malformed handoff packages are blocked before adapter execution.
