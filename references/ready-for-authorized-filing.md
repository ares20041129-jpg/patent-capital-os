# Ready For Authorized Filing

Use this reference when a validated filing package should pass official-channel preflight and become ready for authorized filing handoff.

## Purpose

This stage creates `ready_for_authorized_filing` evidence without touching an official system. It proves the package, account authority, signature authority, automation permission, fee authority, receipt-capture plan, and access-control boundary are ready for an authorized human filing action or a later approved adapter preflight.

## Required Inputs

- Validated package directory containing:
  - `submission-authorization-packet.json` for the counsel/agent route, or `ai-self-filing-authorization-packet.json` for the no-external-lawyer AI self-filing route
  - `filing-package-manifest.yaml`
  - `filing-status.json`
- For AI self-filing, a source-bound application materials bundle generated and validated with `scripts/prepare_patent_application_materials.py`, including request-form metadata, generated claims/specification/abstract/drawings materials, XML readiness, same-case draft evidence provenance, and same-case low-risk abnormal filing assessment.
- `official-preflight-source.json` with independently supplied:
  - checked-by operator;
  - account authorization evidence;
  - signature authority and whether any step is human-only;
  - automation allowance and adapter identity;
  - no access-control bypass confirmation;
  - payment method reference;
  - receipt-capture destination and owner;
  - planned docket entry and deadlines.

## Command

```bash
python -X utf8 scripts/prepare_ready_for_authorized_filing.py validated-package-dir official-preflight-source.json --output-dir validated-package-to-official-ready --json
```

## Outputs

- `official-channel-preflight.yaml`
- `receipt-capture-plan.yaml`
- `filing-status.json`
- `readiness-report.md`
- `artifact-hashes.json`

## Required Invariants

- `official-channel-preflight.yaml` passes `scripts/validate_official_channel_preflight.py`.
- `receipt-capture-plan.yaml` passes `scripts/validate_receipt_capture.py --allow-plan-only`.
- `status=ready_for_authorized_filing`.
- `legal_gate=passed`.
- `legal_gate_mode` is either `counsel_or_agent_review` or `ai_self_filing_no_external_lawyer`.
- `package_validation=passed`.
- `official_channel_preflight=passed`.
- `receipt_capture_plan=planned`.
- If the AI self-filing application materials include `reference_patent_delta_hash`, the generated official preflight, filing status, and readiness report must preserve the same reference delta hash, positive reference-delta row and claim-element counts, and `reference_delta_boundary_preserved=true`.
- Reference-patent delta evidence remains boundary and claim-strategy evidence only. It is not applicant claim support, legal advice, filing authorization, official submission evidence, receipt evidence, or application-number evidence.
- `official_system_touched=false`.
- `official_submission_performed=false`.
- No receipt hash or application number may appear.

## Validator

Run:

```bash
python -X utf8 scripts/validate_ready_for_authorized_filing_benchmark.py benchmarks/validated-package-to-official-ready --json
```

Passing this validator means the case is ready for authorized filing handoff or approved-adapter preflight. It does not mean the case has been uploaded, signed, paid, submitted, receipted, accepted, or assigned an application number.
