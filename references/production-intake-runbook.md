# Production Intake Runbook

Use this runbook when received invention materials should be processed through the local Patent Capital OS skill loop and stopped before automatic official submission.

## Scope

This runbook covers local intake through read-only handoff indexing:

- received raw material folders;
- optional cited-patent reference delta source;
- AI self-filing legal and compliance gate with no external lawyer in the default path;
- application materials generation and quality gate;
- approved-adapter execution readiness;
- read-only handoff package;
- inbox handoff index;
- skill completion audit.

It does not cover API service deployment, dashboard deployment, database operations, watcher services, official login, upload, signature, payment, adapter execution, receipt capture, or application-number evidence.

## Inbox Layout

Each child folder under the inbox is one case:

```text
inbox/
  case-a/
    raw-input/
      invention-notes.md
      drawings-notes.md
    case-config.json
  case-b/
    raw-input/
      invention-notes.md
    reference-delta-source.json
    case-config.json
```

`case-config.json` may include:

```json
{
  "case_id": "CASE-001",
  "received_from": "Applicant",
  "jurisdiction": "CN",
  "intake_mode": "batch_import",
  "raw_input_dir": "raw-input",
  "reference_delta_source": "reference-delta-source.json"
}
```

Path fields must be relative to the case folder. Absolute paths and path traversal are rejected before pre-submission generation.

## Commands

Run the inbox-to-handoff pipeline:

```bash
python -X utf8 scripts/orchestrate_inbox_to_handoff.py inbox --output-dir out/inbox-to-handoff --inbox-id INBOX-001 --confirmation-packet-template assets/templates/disclosure-confirmation-packet.json --ai-self-filing-source-template assets/templates/ai-self-filing-source.json --json
```

Generate the final handoff index:

```bash
python -X utf8 scripts/prepare_inbox_handoff_index.py out/inbox-to-handoff --output-dir out/inbox-handoff-index --index-id INBOX-HANDOFF-INDEX-001 --json
python -X utf8 scripts/validate_inbox_handoff_index_benchmark.py out/inbox-handoff-index --json
```

Generate the skill completion audit after the handoff index exists:

```bash
python -X utf8 scripts/prepare_skill_completion_audit.py --skill-root . --output-dir out/skill-completion-audit --json
python -X utf8 scripts/validate_skill_completion_audit_benchmark.py out/skill-completion-audit --json
```

Run the local regression gate before calling the skill verified:

```bash
python -X utf8 scripts/run_regression_gate.py --output-dir out/regression-gate --json
python -X utf8 scripts/validate_artifact_hash_manifest.py out/regression-gate/artifact-hashes.json --json
```

## Outputs

The inbox-to-handoff folder contains:

- `processed-cases/`;
- `case-queue.json`;
- `batch-processor-result.json`;
- `inbox-to-handoff-result.json`;
- `inbox-to-handoff-report.md`;
- `artifact-hashes.json`.

The handoff index folder contains:

- `inbox-handoff-index.json`;
- `inbox-handoff-index.md`;
- `artifact-hashes.json`.

The completion audit folder contains:

- `skill-completion-audit.json`;
- `skill-completion-audit.md`;
- `artifact-hashes.json`.

## Failure Handling

If inbox orchestration fails, inspect `inbox-to-handoff-result.json` and the per-case errors. Do not reuse a partially populated output directory; create a new output directory after curing the input.

If the index fails, verify the source inbox result, case queue, batch result, and every processed case handoff package still exist and hash-match.

If the audit fails, cure the blocked audit item shown in `skill-completion-audit.json`, then regenerate the audit.

If the regression gate fails, do not treat the skill as closed. Fix the failing validator, manifest, source compile, JSON/YAML parse, structured hash, dangerous-boolean, or forbidden-scan issue, then rerun the gate.

## Archive Rule

Archive the full inbox-to-handoff output, handoff index, completion audit, and regression evidence together. The `artifact-hashes.json` files are the local integrity records.

## Boundary

The closed skill loop stops at `approved_for_adapter_execution` and `handoff_ready_no_auto_submit`. It does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.
