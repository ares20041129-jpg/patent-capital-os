# Legal Gates

Use this reference before any filing-readiness or direct-submission workflow. The legal gate is mandatory. The default production route may be AI self-filing with applicant authorization; external lawyer or patent-agent review is a separate route, not a requirement for every case.

## Gate Modes

| Mode | Pass evidence | Stop condition |
|---|---|---|
| `counsel_or_agent_review` | Counsel or patent-agent approval tied to final version plus applicant authorization | No review, ambiguous review, or review covers older version |
| `ai_self_filing_no_external_lawyer` | Valid AI self-filing authorization packet, applicant self-filing eligibility, AI compliance review, final package hash, and applicant authorization | Mandatory-agent condition, foreign/HMT applicant condition for this route, agency-bypass request, unsupported AI checks, or missing applicant authority |

## Gate Levels

| Gate | Pass evidence | Stop condition |
|---|---|---|
| G0 Final version identity | Final documents and hashes match reviewed version | Hash mismatch or unclear final version |
| G1 Legal/compliance review mode | Counsel/agent review tied to final version, or validated AI self-filing gate tied to final package | Neither route is present, route evidence is ambiguous, or route evidence covers an older version |
| G2 Applicant authorization | Applicant or authorized representative approves filing action | Missing, expired, narrow, or conflicting authority |
| G3 Inventor confirmation | Inventor names, order, and contribution are confirmed | Missing inventor contribution, name/order conflict |
| G4 Ownership and chain of title | Employment, assignment, collaboration, commission, or internal approval evidence | Unresolved ownership dispute |
| G5 Confidentiality and secrecy review | China completion / foreign filing / secrecy review status resolved | Foreign/PCT path unresolved where secrecy review may be required |
| G6 Agency and signature authority | Agent appointment, account authority, electronic signature authority | Missing agency or signature permission |
| G7 Fee authority | Fee payer, reduction status, payment permission, deadline | No fee authority for automatic payment |
| G8 Non-abnormal filing check | Real invention basis and legitimate filing purpose | Fabricated invention, data, inventor, or batch low-quality filing |
| G9 Official-channel compliance | Filing uses authorized official channel and permissions | Request to bypass official controls |
| G10 Audit readiness | Log captures who approved what, when, and which version | Missing audit trail |

G8 may be evidenced at draft stage by `abnormal-filing-risk-assessment.json`, but that artifact is still draft-only evidence. It cannot replace AI self-filing legal/compliance authorization, applicant authorization, official-channel preflight, fee authority, or filing package validation.

## Submission Authorization Packet Fields

Minimum fields:

```yaml
case_id:
filing_type:
jurisdiction:
final_documents:
  claims:
  specification:
  abstract:
  drawings:
  request_metadata:
hashes:
  source_package:
  final_claims:
  final_specification:
  final_xml:
counsel_review:
  reviewer_name:
  reviewer_role:
  organization:
  approval_statement:
  reviewed_hash:
  timestamp:
applicant_authorization:
  applicant_name:
  authorized_person:
  authority_basis:
  allowed_actions:
  timestamp:
inventor_confirmation:
  inventors:
  contribution_confirmed:
ownership:
  basis:
  evidence:
secrecy_review:
  china_completed:
  foreign_or_pct_planned:
  status:
agency:
  agent_or_firm:
  appointment_evidence:
filing_channel:
  official_system:
  account_owner:
  signature_authority:
fees:
  payer:
  fee_reduction:
  auto_pay_authorized:
```

For AI self-filing without an external lawyer or patent agent, use `ai-self-filing-authorization-packet.json` instead of `counsel_review` and validate it with `scripts/validate_ai_self_filing_authorization.py`.

Minimum AI self-filing fields:

```yaml
external_lawyer_involved: false
self_filing_eligibility:
  self_filing_allowed: true
  mandatory_agent_required: false
  foreign_or_hmt_applicant: false
  agency_bypass_requested: false
ai_compliance_review:
  reviewed_artifacts_hash:
  no_copying_check: passed
  claim_support_check: passed
  abnormal_filing_risk: low
  abnormal_filing_risk_assessment:
    case_id:
    status: abnormal_filing_risk_assessed
    gate: G8 Non-abnormal filing check
    risk_level: low
    artifact_hash:
    artifact_path:
  official_format_check: passed
  legal_gate_review:
    review_record_hash:
    authorization_scope_check: passed
    self_filing_eligibility_check: passed
    inventor_ownership_check: passed
    secrecy_check: passed
    fee_authority_check: passed
    official_channel_boundary_check: passed
    legal_advice_claimed: false
    lawyer_or_agent_review_claimed: false
applicant_authorization:
  allowed_actions:
inventor_confirmation:
  contribution_confirmed: true
ownership:
  dispute_absent: true
filing_channel:
  official_account_registered: true
  automation_allowed: true
  bypasses_access_controls: false
fees:
  auto_pay_authorized: true
```

AI self-filing hash fields must use exact lowercase `sha256:<64 hex>` values. When `artifact_path` is available for the abnormal filing risk assessment, validators must resolve it relative to the packet directory and reject missing files or hash mismatches.

## Filing Status Language

Use precise status labels:

- `intake_received`: materials received only.
- `legal_gate_failed`: filing blocked.
- `ready_for_package_validation`: legal gate passed.
- `package_valid_official_preflight_pending`: filing package validates, but official-channel preflight and receipt plan are not complete.
- `ready_for_authorized_filing`: filing package valid but not submitted.
- `submitted_pending_receipt`: upload/submission action completed but official receipt not yet captured.
- `official_receipt_received`: official receipt/application data captured.
- `accepted_or_application_number_received`: use only when official evidence supports it.

## Mandatory Deficiency Report

When a gate fails, output:

- Failed gate ID.
- Missing or contradictory evidence.
- Filing risk if ignored.
- Required cure.
- Responsible owner.
- Whether the case can continue in draft-only mode.

## Do Not

- Do not infer legal review from a file name or user optimism.
- Do not infer AI self-filing eligibility from a file name or user optimism.
- Do not treat a draft package as authorized filing material.
- Do not submit if final package hash differs from reviewed hash.
- Do not bypass official system controls.
- Do not claim legal validity, patentability, or acceptance without official evidence.
