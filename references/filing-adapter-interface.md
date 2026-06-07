# Filing Adapter Interface

Use this reference when a workflow reaches `ready_for_authorized_filing`.

## Adapter Boundary

A filing adapter is an execution boundary, not a legal decision maker. It may run only after:

- Submission authorization packet passed.
- Filing package manifest passed.
- Official-channel preflight passed.
- Official session authorization passed with no credential material or official-control bypass.
- Receipt capture plan exists.
- Status is `ready_for_authorized_filing`.

## Allowed Adapter Request Fields

- `case_id`
- `execution_mode`: `dry_run`, `handoff`, or approved adapter name.
- `official_system`
- `account_role`
- `authorization_evidence`
- `signature_authority_evidence`
- `payment_authority_evidence`
- `final_package_hash`
- `reviewed_package_hash`
- `package_manifest`
- `receipt_capture_destination`
- `human_only_steps`
- `approved_adapter_preflight`
- `approved_adapter_preflight_hash`
- `adapter_security_review_hash`
- `adapter_production_readiness_packet`
- `adapter_production_readiness_hash`
- `official_session_authorization_packet`
- `official_session_authorization_hash`
- `official_session_reference_hash`
- `requested_action`

## Required Approved-Adapter Response Evidence

When `execution_mode=approved_adapter` and the response claims `submitted_pending_receipt`, the response must include:

- `approved_adapter_preflight_hash`
- `adapter_production_readiness_hash`
- `official_session_authorization_hash`
- `official_session_reference_hash`
- `adapter_execution_result`
- `adapter_execution_result_hash`
- `official_system_touched=true`
- `official_submission_performed=true`
- `next_status=submitted_pending_receipt`

Validate the detailed execution evidence with `scripts/validate_adapter_execution_result.py`. A submitted-pending response is not a receipt and is not an application number.

## Forbidden Adapter Request Fields

- Raw password.
- Private signing key.
- Captcha bypass instruction.
- Multi-factor secret.
- Cookie/session token.
- Any instruction to bypass official controls.
- Any instruction to change final package contents after counsel approval.

## Adapter Response States

| State | Meaning |
| --- | --- |
| dry_run_ok | Request is structurally valid; no official system touched |
| handoff_required | Human-only official step or no approved adapter |
| submitted_pending_receipt | Lawful official action completed; receipt pending |
| blocked | Adapter refused action |

## Production Rule

Use `dry_run` or `handoff` until a real adapter has been separately implemented, passed strict production adapter readiness, passed strict official session authorization, security-reviewed, authorized by the account owner, and passed `scripts/validate_approved_adapter_preflight.py`. Do not infer a submission from an adapter plan or approved preflight.

When `execution_mode=approved_adapter`, run `scripts/validate_filing_adapter_contract.py request filing-adapter-request.json --json` from the request folder. The validator must require exact lowercase `sha256:<64 hex>` values, recompute the referenced approved-adapter preflight hash, production adapter readiness packet hash, and official session authorization packet hash, and compare the request's case, package, security-review, readiness, session-authorization, and session-reference hashes against the referenced approved preflight before the request can be treated as executable.

For a submitted-pending response, run `scripts/validate_filing_adapter_contract.py response filing-adapter-response.json --json` from the response folder. The validator must require exact lowercase `sha256:<64 hex>` values, recompute `adapter_execution_result_hash` from the referenced `adapter-execution-result.json`, and compare response hashes against the referenced execution result before the response can advance any status.

For batch evidence intake after a lawful adapter has already returned evidence, `scripts/run_case_queue.py` may run an `approved_adapter` queue only when `approved_adapter_evidence_mode=true`. That mode is local evidence validation only: it runs validators such as `validate_generated_adapter_execution_result_benchmark`, keeps runner and generator official-action flags false, and does not log in, upload, sign, pay, submit, or execute an adapter.
