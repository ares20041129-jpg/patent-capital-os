# Filing Execution Boundary

Use this reference before any official filing, payment, signature, or receipt-capture action.

## Default Rule

Default to ready-to-submit handoff. Execute official submission only through a dedicated filing adapter or authorized RPA path that has passed all gates below.

## Required Preflight Artifacts

- Submission authorization packet matching `schemas/submission-authorization.schema.json`.
- Official channel preflight using `assets/templates/official-channel-preflight.yaml`.
- Pre-submission handoff package using `scripts/prepare_pre_submission_handoff_package.py` when the full local pre-submission pipeline is used.
- Receipt capture plan using `assets/templates/receipt-capture.yaml`.
- Audit log entry using `assets/templates/audit-log-entry.yaml`.
- Docket entry plan using `assets/templates/docket-entry.yaml`.

## Adapter Boundary

A filing adapter may only receive:

- Case ID.
- Final package location.
- Final package hash.
- Read-only pre-submission handoff package location and hash, when available.
- Official channel identifier.
- Authorized account role.
- Signature authority evidence reference.
- Payment authority evidence reference.
- Receipt capture destination.

A filing adapter must not receive or store raw passwords, private signature keys, or bypass instructions.

## Human-Only Steps

If an official system requires human-only confirmation, captcha, multi-factor approval, electronic signature ceremony, or non-delegable review, stop automation and produce a handoff. Record:

- Exact step.
- Package hash.
- Required account role.
- Deadline.
- Risk if delayed.

## Stop Conditions

Stop before filing or payment when:

- Authorization packet is missing or fails validation.
- Official channel preflight is incomplete.
- Pre-submission handoff package validation fails when that package is used as adapter input evidence.
- Automation permission is absent.
- Final package hash differs from reviewed hash.
- Human-only step appears.
- Receipt capture destination is missing.
- User requests bypass of official controls.

## Success Evidence

Submission is not complete until the system records:

- Official receipt or official status evidence.
- Timestamp.
- Official file list.
- Fee status or payment receipt.
- Application number, if issued.
- Docket entry.
