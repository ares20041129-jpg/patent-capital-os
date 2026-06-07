# AI Self-Filing Gate

Use this reference when the default filing path must avoid external lawyers or patent agents while preserving a mandatory legal/compliance gate.

## Purpose

The AI self-filing gate converts a draft-only package into filing-readiness evidence for an applicant that is allowed to file through its own official account. It is not lawyer review, patent-agent review, legal advice, official submission, receipt evidence, or application-number evidence.

## Gate Mode

`legal_gate_mode=ai_self_filing_no_external_lawyer`

This mode may pass only when all of these are true:

- The applicant authorizes the specific filing, submission, and fee actions.
- The applicant can use a lawful self-filing route.
- No mandatory-agent condition is present.
- No agency-bypass request is present.
- No foreign, Hong Kong, Macau, or Taiwan applicant condition is present for this route.
- Inventor contribution and ownership are confirmed.
- Secrecy and foreign/PCT status are resolved.
- AI checks pass for no-copying, claim support, abnormal filing risk, and official format.
- Official account, signature authority, automation permission, fee authority, receipt capture, audit logging, and docketing are present before any official action.

## Required Packet

Use `assets/templates/ai-self-filing-source.json` and validate with:

```bash
python -X utf8 scripts/validate_ai_self_filing_authorization.py ai-self-filing-authorization-packet.json --json
```

When validation fails, generate a deficiency report instead of advancing:

```bash
python -X utf8 scripts/prepare_ai_self_filing_deficiency_report.py ai-self-filing-authorization-packet.json --output-dir deficiency-output --json
```

When cured evidence is later supplied, revalidate the cure before rebuilding any filing package:

```bash
python -X utf8 scripts/prepare_ai_self_filing_cure_revalidation.py deficiency-output cured-packet-or-cure-source.json --output-dir cure-output --json
```

The cure revalidation must preserve the source deficiency hash, source failed-packet hash, cured packet hash, prior validator errors, and empty post-validation errors. It may advance only from `legal_gate_failed` to `ready_for_package_validation`; package validation, official-channel preflight, signing, payment, submission, receipt capture, and application-number evidence remain separate gates.

Required evidence includes:

- `external_lawyer_involved=false`
- `self_filing_eligibility.self_filing_allowed=true`
- `self_filing_eligibility.mandatory_agent_required=false`
- `self_filing_eligibility.foreign_or_hmt_applicant=false`
- `self_filing_eligibility.agency_bypass_requested=false`
- AI compliance review fields tied to exact lowercase `sha256:<64 hex>` reviewed artifact hashes
- AI abnormal filing risk assessment fields tied to a same-case `abnormal-filing-risk-assessment.json` artifact path and exact lowercase `sha256:<64 hex>` artifact hash with `risk_level=low`; validators must recompute the file hash when the packet directory is available
- When the abnormal-filing assessment includes `reference_patent_delta_hash`, the AI self-filing authorization packet must preserve the same reference-delta hash, row count, claim-element count, and `reference_delta_boundary_preserved=true`; this remains boundary and claim-strategy evidence only, not applicant claim support
- Application materials fields tied to `application-materials.json`, request-form metadata, generated document materials, XML readiness, same-case `draft-evidence-provenance.json`, and same-case low-risk abnormal filing assessment before official-channel preflight
- AI legal gate review fields proving authorization scope, self-filing eligibility, inventor/ownership, secrecy, fee authority, and official-channel boundary checks passed
- AI legal gate review fields proving no legal advice, lawyer review, or patent-agent review is claimed
- Applicant allowed actions containing submit/file and, for automatic fee mode, pay
- Inventor, ownership, secrecy, official-channel, fee, and decision fields

## Allowed Progression

1. `draft_only`
2. `ready_for_package_validation`
3. `package_valid_official_preflight_pending`
4. Source-bound application materials generated while status remains `package_valid_official_preflight_pending`
5. `ready_for_authorized_filing`
6. `approved_for_adapter_execution`
7. `submitted_pending_receipt` only after independently supplied official action evidence
8. `official_receipt_received` only after independently supplied receipt evidence
9. `accepted_or_application_number_received` only after independently supplied application-number evidence

Do not skip official-channel preflight, adapter preflight, receipt capture, application-number evidence, audit logging, or docketing.

## Hard Stop Conditions

Stop and do not file when:

- A mandatory-agent condition exists.
- The applicant is outside the allowed self-filing route for this workflow.
- The request is to bypass an agency requirement.
- Official login, signature, payment, or captcha/MFA requires a human-only step with no lawful automation path.
- The applicant authorization is missing, ambiguous, expired, or does not cover the action.
- AI no-copying, support, abnormal-filing, or official-format checks fail.
- The abnormal-filing risk assessment artifact is missing, mismatched, not same-case, or not `risk_level=low`.
- The abnormal-filing risk assessment includes a reference-patent delta but the AI self-filing packet drops its hash/count metadata or lacks `reference_delta_boundary_preserved=true`.
- The application materials bundle is missing, cannot bind to the source draft hash, lacks request-form metadata, lacks generated claims/specification/abstract/drawings/XML readiness materials, or cannot prove claim-support provenance.
- AI legal gate review is missing, incomplete, claims legal advice, or claims lawyer/patent-agent review.
- Any technical, inventor, ownership, secrecy, fee, receipt, or official-channel fact is fabricated or unsupported.
- The final package hash differs from the AI-reviewed package hash.

When stopped, the required output is `legal_gate_failed`, `decision=do_not_file`, a structured deficiency report, `draft_only_work_allowed=true`, and `official_system_touched=false`.

## Production Boundary

This gate prepares evidence for lawful applicant self-filing. It must not claim that a lawyer reviewed the material, that a patent agent approved it, or that an official filing occurred. Real official status requires independently captured official evidence.

For benchmark or generated post-adapter artifacts, separate evidence-state fields from generator-action fields. A mock artifact may describe evidence that claims `official_system_touched=true`, but the local generator must persist `generator_official_system_touched=false`, `generator_official_submission_performed=false`, and explicit `benchmark_mock=true` so the benchmark cannot be confused with a real official filing.
