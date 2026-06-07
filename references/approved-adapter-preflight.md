# Approved Adapter Preflight

Use this reference only after a case is already `ready_for_authorized_filing`.

## Purpose

The approved-adapter preflight is the final machine-checkable gate before a real filing adapter may attempt an official action. It does not submit, sign, pay, or claim receipt. It proves that the next execution attempt is authorized, scoped, auditable, and credential-safe.

## Required Evidence

- Submission authorization packet and counsel-reviewed package hash, or AI self-filing authorization packet and AI-reviewed package hash.
- Account-owner authorization for the specific adapter.
- Signature and payment authority evidence.
- Two-person approval from distinct legal/compliance and filing-operations approvers. In AI self-filing mode, the legal/compliance approver is the AI self-filing gate, not an external lawyer.
- Official-channel preflight with automation allowed and no access-control bypass.
- Strict production adapter readiness packet validated with `scripts/validate_production_adapter_readiness.py`, bound by packet hash to the approved-adapter preflight.
- Strict official session authorization packet validated with `scripts/validate_official_session_authorization.py`, bound by packet hash and session-reference hash to the approved-adapter preflight, adapter request, and filing status.
- Adapter registry entry, dry-run result, and passed security review.
- Receipt capture plan, audit log plan, and docket entry plan.
- Credential-handling statement proving no raw passwords, private keys, MFA secrets, session tokens, cookies, or captcha bypass instructions are passed to the adapter.
- When the official-ready preflight includes application materials with `reference_patent_delta_hash`, the approved-adapter preflight must preserve the application-materials hash, reference-patent delta hash, positive reference-delta row and claim-element counts, and `reference_delta_boundary_preserved=true`.
- The adapter request, filing status, audit input hashes, and adapter boundary report must carry or cite the same reference-patent delta evidence as boundary evidence only. It must not become applicant claim support, legal advice, filing authorization, official submission evidence, receipt evidence, or application-number evidence.

All approved-adapter preflight hash fields must use exact lowercase `sha256:<64 hex>` values. When the preflight includes a local path for authorization packet, official-channel preflight, package manifest, receipt plan, audit plan, docket plan, production adapter readiness packet, or official session authorization packet, the validator must recompute the referenced file hash and reject mismatches.

Audit and docket plans must not contain descriptive `sha256:*` placeholders. Known upstream inputs should be recorded as exact hashes; downstream artifacts that cannot be known without creating a circular hash dependency must use a plain non-hash pending marker such as `pending`.

## Decision States

| State | Meaning |
| --- | --- |
| approved_for_adapter_execution | All pre-execution gates pass; the next step may be an approved adapter attempt |
| handoff_required | Human-only official step or non-delegable control exists |
| blocked | Required evidence is missing, inconsistent, or outside authorization scope |

## Stop Conditions

Stop and do not call a real adapter when:

- Final package hash differs from the counsel-reviewed or AI-reviewed package hash.
- Adapter security review is missing or failed.
- Production adapter readiness evidence is missing, shape-test only, mock/benchmark/placeholder evidence, hash-mismatched, or not strict `production_adapter_readiness`.
- Official session authorization evidence is missing, shape-test only, mock/benchmark/placeholder evidence, packet/session-reference hash-mismatched, or not strict `official_session_authorization`.
- Account-owner adapter authorization is missing.
- Human-only steps are present.
- Automation bypasses official access controls.
- Any raw credential, private key, MFA secret, cookie, session token, or captcha bypass is requested.
- Receipt capture, audit logging, or docket plan is missing.

## Validator

Run:

```bash
python -X utf8 scripts/validate_approved_adapter_preflight.py approved-adapter-preflight.json --json
```

Passing this validator permits only an adapter execution attempt. It is not evidence that filing occurred.

## Generator

When the case is already `ready_for_authorized_filing`, use:

```bash
python -X utf8 scripts/prepare_approved_adapter_preflight.py ready-for-authorized-filing-dir validated-package-dir approved-adapter-source.json --output-dir official-ready-to-approved-adapter-preflight --json
```

The `approved-adapter-source.json` must be independently supplied. Do not infer adapter registry approval, production adapter readiness, official session authorization, dry-run result, security review, account-owner adapter authorization, two-person approval, credential handling, or allowed execution actions from the ready status alone.

The generator outputs:

- `approved-adapter-preflight.json`
- `filing-adapter-request.json`
- `filing-status.json`
- `adapter-boundary-report.md`
- `audit-log-entry-plan.yaml`
- `docket-entry-plan.yaml`
- `artifact-hashes.json`

The generated status may be `approved_for_adapter_execution` only. It must not mark official submission, adapter execution, receipt, acceptance, fee payment, or application-number receipt.
