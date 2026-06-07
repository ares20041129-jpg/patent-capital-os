# Adapter Execution Result

Use this reference after `approved_for_adapter_execution` when an approved adapter returns an execution result.

## Purpose

The adapter execution result is the only evidence that may advance a case from `approved_for_adapter_execution` to `submitted_pending_receipt`. It proves a submission action was attempted or completed by an approved adapter, but it does not prove that an official receipt or application number exists.

## Required Evidence

- Adapter request reference and hash.
- Approved-adapter preflight reference and hash.
- Production adapter readiness hash inherited from the approved-adapter preflight.
- Official session authorization hash inherited from the approved-adapter preflight and adapter request.
- Official session reference hash inherited from the official session authorization packet, approved-adapter preflight, adapter request, and approved status.
- Adapter name, version, start time, and completion time.
- Official system and official action.
- Final package hash, reviewed package hash, and submitted package hash.
- Official status snapshot hash and submitted file-list hash.
- Receipt capture plan and status `submitted_pending_receipt`.
- Audit log entry and docket entry.
- Fee/payment status.
- When the approved-adapter preflight includes application materials with `reference_patent_delta_hash`, the adapter execution result, filing-adapter response, filing status, audit input hashes, and report must preserve the same application-materials hash, reference-patent delta hash, positive delta row and claim-element counts, and `reference_delta_boundary_preserved=true`.
- Reference-patent delta evidence remains boundary and claim-strategy evidence only. It is not applicant claim support, legal advice, filing authorization, official submission evidence, receipt evidence, or application-number evidence.

## Stop Conditions

Stop and do not mark `submitted_pending_receipt` when:

- Final package hash, reviewed package hash, or submitted package hash differ.
- Adapter execution result is missing.
- Production adapter readiness hash is missing or does not match the approved-adapter preflight/request chain.
- Official session authorization hash is missing or does not match the approved-adapter preflight/request/status chain.
- Official session reference hash is missing or does not match the approved-adapter preflight/request/status chain.
- Official status snapshot hash is missing.
- Reference-delta metadata is missing or mismatched after it appeared in the approved-adapter preflight.
- Receipt capture plan is missing.
- Audit or docket evidence is missing.
- The result includes an official receipt hash or application number before receipt capture.
- Any raw credential, private key, MFA secret, session token, cookie, or captcha bypass appears in the result.

## Validator

Run:

```bash
python -X utf8 scripts/validate_adapter_execution_result.py adapter-execution-result.json --json
```

Run this command from the folder that contains `adapter-execution-result.json`. The validator must recompute the referenced adapter request hash, approved-adapter preflight hash, receipt-capture plan hash, audit-log-entry hash, and docket-entry hash before `submitted_pending_receipt` can be accepted.

If this passes, run `scripts/validate_filing_status_transition.py` on the updated filing status. The next required gate is receipt capture.

## Evidence Processor

When an approved adapter has already returned execution evidence, use:

```bash
python -X utf8 scripts/prepare_adapter_execution_result.py approved-adapter-preflight-dir adapter-execution-source.json --output-dir submitted-pending-receipt-dir --json
```

This script is an evidence processor. It must not log in, upload, sign, pay, submit, solve captchas, bypass access controls, or touch the official system. It only converts an independently supplied adapter execution source into:

- `adapter-execution-result.json`
- `filing-adapter-response.json`
- `receipt-capture-pending.yaml`
- `filing-status.json`
- `adapter-execution-report.md`
- `audit-log-entry.yaml`
- `docket-entry.yaml`
- `artifact-hashes.json`

For benchmark or simulated evidence, `execution.benchmark_mock=true` is mandatory and every report must say it is not a real filing, not a real receipt, and not a real application number.
