# Case Processor State Machine

Use this reference when processing a case folder or batch queue.

## Principle

The case processor orchestrates gates. It does not draft unsupported facts, approve legal review, sign, pay, bypass official controls, or claim official status without evidence.

## Case States

| State | Meaning | Required evidence before entering | Next allowed states |
| --- | --- | --- | --- |
| intake_received | Materials received only | source manifest or intake note | draft_only, legal_gate_failed, ready_for_package_validation |
| draft_only | Draft artifacts may exist; filing blocked | invention disclosure, draft, support map, legal gate failure or pending | legal_gate_failed, ready_for_package_validation |
| legal_gate_failed | Filing blocked by hard gate | failed gates and deficiency report | draft_only, ready_for_package_validation |
| ready_for_package_validation | Legal authorization exists; package not validated | submission authorization packet passes | package_valid_official_preflight_pending, legal_gate_failed |
| package_valid_official_preflight_pending | Package manifest, XML/doc checks, and source-bound application materials pass | filing package manifest and application materials validate | ready_for_authorized_filing, legal_gate_failed |
| ready_for_authorized_filing | Official-channel preflight and receipt plan pass | official-channel preflight, receipt plan, status transition | approved_for_adapter_execution, submitted_pending_receipt |
| approved_for_adapter_execution | Approved adapter preflight passes; no official action yet | adapter security review, account authorization, credential controls, audit/docket/receipt plans | submitted_pending_receipt |
| submitted_pending_receipt | Lawful submission action occurred; receipt not captured | adapter response or human log showing submission action | official_receipt_received |
| official_receipt_received | Official receipt captured | receipt evidence, file hash, filing date, docket entry | accepted_or_application_number_received |
| accepted_or_application_number_received | Official evidence includes application number or acceptance | receipt plus application number/status evidence | docketing and portfolio ops |

## Processor Rules

- Process one case at a time unless each case has isolated artifacts and hashes.
- Read the case record first.
- Validate the artifacts required for the target state.
- Use `validate_filing_status_transition.py` for status movement.
- Statuses before official action (`intake_received` through `approved_for_adapter_execution`) must explicitly keep `official_system_touched=false` and `official_submission_performed=false`.
- Statuses at or after `submitted_pending_receipt` must explicitly record official-action evidence with `official_system_touched=true` and `official_submission_performed=true`, while generator-side official-action fields remain false.
- Statuses at `ready_for_authorized_filing` or later must use exact lowercase `sha256:<64 hex>` values for both `final_package_hash` and `reviewed_package_hash`; descriptive placeholders are not valid filing-status hashes.
- AI self-filing statuses must keep `legal_gate_mode=ai_self_filing_no_external_lawyer` and `external_lawyer_involved=false`; the validator must reject any true external-lawyer flag.
- Use `validate_artifact_hash_manifest.py` when a manifest exists.
- Default filing execution mode is `handoff`.
- Adapter mode may run only when the adapter request validates and `execution_mode` is `dry_run` or an approved lawful adapter path.
- Never pass raw credentials, passwords, private keys, captcha bypass details, or signature secrets to an adapter.

## Required Processor Output

Each processor run must produce:

- Input case ID and previous status.
- Target status and decision.
- Validators run.
- Errors and warnings.
- Required human action, if any.
- Audit entry ID.
- Next allowed state.

## Stop Conditions

Stop when any validator fails, when evidence hashes mismatch, when an official system step is human-only, or when the requested action exceeds authorization.
