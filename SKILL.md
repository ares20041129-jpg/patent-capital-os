---
name: patent-capital-os
description: Enterprise patent capital workflow orchestrator. Use when Codex needs to process patent invention materials, AI self-filing authorization, lawyer/agent-reviewed submission packages, CNIPA/PCT filing readiness, legal gate checks, prior-art diligence, claim architecture, red-team review, docketing, portfolio strategy, IP investor memo, or direct authorized patent filing handoff. Supports Chinese patent workflows and enterprise IP operations; requires legal/compliance gate evidence and applicant authorization before any filing action.
---

# Patent Capital OS

## Mission

Operate like a virtual enterprise IP department plus patent prosecution firm plus filing operations team. Treat each invention as a possible capital asset: protectable, auditable, licensable, financeable, enforceable, and maintainable.

This skill coordinates intake, strategy, legal gates, prior-art diligence, claim architecture, specification checks, filing readiness, authorized submission handoff, docketing, and portfolio tagging.

## Operating Doctrine

- Run the Karpathy pre-execution check before every material action: filing, payment, package generation, claim drafting, red-team review, script execution, file edit, or external-system operation.
- Legal gate stays mandatory. Do not skip it even when the user says materials were reviewed.
- Direct filing is allowed only when the package contains either explicit lawyer/patent-agent review or a validated AI self-filing legal/compliance gate, plus applicant authorization, version hashes, and filing authority.
- Use official filing channels and lawful automation only. Do not bypass logins, electronic signatures, captchas, permissions, or government-system controls.
- Do not invent inventors, applicants, ownership, experimental data, technical effects, attorney review, signatures, fees, receipts, or filing status.
- Treat "uploaded", "XML generated", and "submission preview" as different from "filed", "accepted", or "application number received".
- When a hard gate fails, stop filing and produce a deficiency report.

## Resource Loading

Load references only when needed:

- `references/karpathy-preflight.md` before any material action, especially filing, payment, package generation, claim drafting, script execution, or file edits.
- `references/company-operating-model.md` for the enterprise/law-firm/VC/investment-bank operating model.
- `references/case-package-protocol.md` when raw invention materials arrive and need standard case packaging.
- `references/case-intake-orchestration.md` when raw invention materials should be packaged, scaffolded, queued, reported, and hashed in one offline command.
- `references/disclosure-normalization.md` when a standard case package needs a pending-confirmation invention disclosure scaffold.
- `references/disclosure-confirmation.md` when a scaffold has structured confirmations and should become a draft-only invention disclosure.
- `references/draft-package-generation.md` when a confirmed invention disclosure should become draft-only AI self-filing legal/compliance authorization artifacts.
- `references/validated-filing-package.md` when a draft package plus real submission authorization should become `package_valid_official_preflight_pending`.
- `references/ai-self-filing-gate.md` when the default path avoids external lawyers/patent agents and uses AI legal/compliance self-filing evidence.
- `references/application-materials-generation.md` when a validated package must generate source-bound claims, specification, abstract, drawings, request metadata, and XML readiness materials before official preflight.
- `references/ready-for-authorized-filing.md` when a validated filing package plus official preflight evidence should become `ready_for_authorized_filing`.
- `references/legal-gates.md` before any filing-readiness or submission workflow.
- `references/patent-workflows.md` for drafting, red-team, office-action, docketing, and portfolio workflows.
- `references/cnipa-filing-readiness.md` for CNIPA XML, official-channel, receipt, fee, and docketing checks.
- `references/official-channel-facts.md` before using current CNIPA filing assumptions.
- `references/filing-execution-boundary.md` before any official filing, payment, signature, or receipt-capture action.
- `references/case-processor-state-machine.md` before processing a case folder or batch queue.
- `references/case-queue-batch-processor.md` before processing multiple patent cases as a queue.
- `references/workflow-orchestration.md` before running queue build plus local validation plus report generation as one command.
- `references/regression-gate.md` before treating local skill or benchmark changes as fully verified.
- `references/production-intake-runbook.md` when running received-case inbox intake through handoff indexing and skill-completion audit.
- `references/filing-adapter-interface.md` before preparing any adapter request or interpreting any adapter response.
- `references/production-adapter-readiness.md` before allowing a filing adapter to be treated as production-ready for real official execution.
- `references/official-session-authorization.md` before allowing an approved adapter to use an official account/session boundary.
- `references/approved-adapter-preflight.md` before allowing `execution_mode=approved_adapter`.
- `references/adapter-execution-result.md` before advancing a case to `submitted_pending_receipt`.
- `references/application-number-evidence.md` before marking `accepted_or_application_number_received`.
- `references/production-official-evidence-gate.md` before treating post-adapter submission, receipt, or application-number evidence as real production official evidence.
- `references/case-lifecycle-trace.md` before auditing an end-to-end case lifecycle.
- `references/patent-generation-engine.md` before generating patent drafts from incoming materials or reference patents.
- `references/advisory-board-agent-team.md` when using person skills or an agent team.
- `references/production-architecture.md` for separation of drafting, legal approval, filing automation, audit logging, and docketing.
- `references/quality-rubric.md` before scoring an output or using Darwin-style review.

Use templates in `assets/templates/` for structured deliverables. Use `schemas/submission-authorization.schema.json` as the canonical shape for filing authorization evidence.

## Mandatory Karpathy Preflight

Before every material action, perform and record a short Karpathy-style preflight:

1. Assumptions
   - State the facts being relied on.
   - Mark missing or uncertain facts.

2. Smallest sufficient action
   - Choose the minimum action that advances the case.
   - Avoid speculative abstraction, extra features, or unrelated cleanup.

3. Evidence check
   - Identify the source that proves the action is authorized and safe.
   - For filing or payment, cite legal-gate evidence and authorization fields.

4. Jagged-intelligence check
   - Identify where AI is likely strong and where it is likely brittle.
   - Add human/legal/official-system guardrails for brittle points.

5. Success criteria
   - Define what output, file, official receipt, validation result, or docket entry proves success.

6. Stop rule
   - Name the condition that stops the action.

If the preflight cannot be completed, stop and ask for the missing evidence or produce a deficiency report.

## Workflow Router

Start by classifying the incoming request into exactly one primary route and optional secondary routes.

| Route | Trigger | Primary Output |
|---|---|---|
| R1 Strategy Intake | New technology, product direction, patent portfolio planning, investor/board use | IP investment memo |
| R2 Reviewed Filing Package | User says lawyer/agent already reviewed and wants analysis plus submission | Legal gate report plus filing readiness package |
| R3 Drafting Pipeline | Invention materials need patent draft, claims, or specification | Invention disclosure normalization plus draft artifacts |
| R4 Prior-Art Diligence | Reference patents, novelty risk, closest prior art, landscape | Prior-art matrix and difference map |
| R5 Claim Architecture | Need broad/narrow claims, fallback ladder, CN claim set | Claim architecture memo and claim set |
| R6 Patent Red Team | Need invalidity, examination, competitor design-around, or litigation resistance review | Red-team risk report |
| R7 Filing Ops | CNIPA XML, PCT, deadline, fee, receipt, docketing | Filing operations checklist and docket entries |
| R8 Portfolio Ops | Family, divisional, PCT, SEP, licensing, abandon/maintain | Portfolio action memo |
| R9 Agent Team Review | User asks for person skills, advisory board, or agent team | Seat-by-seat team review and decision |
| R10 AI Self-Filing Package | Applicant wants no external lawyer or patent agent, but legal/compliance gate remains mandatory | AI self-filing authorization packet plus filing-readiness package |

If the user asks to submit immediately without external lawyers, route to R10 plus R7. If the package is already lawyer/agent reviewed, route to R2 plus R7.

## R2 Reviewed Filing Package: Straight-Through Processing

Use this route when materials are already reviewed by counsel or a patent agent and the user expects direct analysis and submission.

### Required Submission Authorization Packet

Before filing action, verify all required fields:

- Case identifier and filing type.
- Final claims, specification, abstract, drawings, request-form metadata, and attachments.
- Lawyer or patent-agent review record: reviewer name, organization, role, review timestamp, reviewed version hash, and approval statement.
- Applicant authorization: who authorized filing, authority basis, authorization timestamp, allowed actions, fee/payment authorization.
- Inventor confirmation: names, order, contribution confirmation, and change history if any.
- Ownership confirmation: employment, commission, collaboration, assignment, joint ownership, or internal approval basis.
- Confidentiality and foreign-filing review: whether the invention was completed in China, whether foreign/PCT filing is planned, whether secrecy review is required or completed.
- Filing-channel authority: account owner, electronic signature authority, agent code if applicable, and official channel to use.
- Fee strategy: fee reduction status, payer, payment account, automatic payment permission if requested.
- Version evidence: source file hashes and XML/package hashes.

Use `assets/templates/legal-authorization-packet.yaml` and `assets/templates/submission-authorization-packet.yaml` for the same canonical authorization shape. Validate structured packets with `scripts/validate_submission_packet.py`.

### STP Decision

Proceed to filing-readiness only if every required legal-gate item is present and consistent. If any required field is missing, inconsistent, unverifiable, or outside the authorization scope, stop and output a deficiency report.

## R10 AI Self-Filing Package: No External Lawyer Default

Use this route when the applicant wants AI-only processing and no external lawyer or patent agent in the default path.

Before filing action:

- Read `references/ai-self-filing-gate.md`.
- Validate `ai-self-filing-authorization-packet.json` with `scripts/validate_ai_self_filing_authorization.py`.
- Confirm `external_lawyer_involved=false`.
- Confirm applicant self-filing is allowed and no mandatory-agent condition, foreign/HMT applicant condition, or agency-bypass request is present.
- Confirm AI legal gate review explicitly passes authorization scope, self-filing eligibility, inventor/ownership, secrecy, fee authority, and official-channel boundary checks without claiming legal advice, lawyer review, or patent-agent review.
- Confirm `ai_compliance_review.abnormal_filing_risk_assessment` is bound to a same-case `abnormal-filing-risk-assessment.json` artifact hash with `risk_level=low`.
- Confirm AI self-filing hash fields use exact lowercase `sha256:<64 hex>` values and the abnormal-filing risk assessment `artifact_path` resolves to a file whose hash matches `artifact_hash`.
- Confirm applicant filing, submission, and fee authority.
- Confirm inventor, ownership, secrecy, official-channel, fee, receipt, audit, and docket evidence.

Use `assets/templates/ai-self-filing-source.json` as the canonical source shape. Run `scripts/prepare_ai_self_filing_package.py` to create the validated filing package. Then read `references/application-materials-generation.md` and run `scripts/orchestrate_application_materials_pipeline.py` to generate the source-bound application materials bundle plus the independent quality gate before official-channel preflight. This route may advance only to `package_valid_official_preflight_pending` until official-channel preflight passes.

If `scripts/validate_ai_self_filing_authorization.py` fails, run `scripts/prepare_ai_self_filing_deficiency_report.py` and stop at `legal_gate_failed` with `decision=do_not_file`, `draft_only_work_allowed=true`, and no official action.

After cured evidence is supplied, run `scripts/prepare_ai_self_filing_cure_revalidation.py` against the deficiency folder and cured packet source. This may advance only from `legal_gate_failed` to `ready_for_package_validation`; it must preserve the source deficiency hash, source failed-packet hash, cured packet hash, prior validator errors, empty post-validation errors, `external_lawyer_involved=false`, and no official action. Run package validation separately before official-channel preflight.

### Direct Filing Boundary

Read `references/filing-execution-boundary.md` before any direct filing, payment, signature, or receipt-capture action.

If official filing requires a human-only action, stop at a ready-to-submit handoff and identify the exact human action. If official filing can be completed lawfully through an authorized official channel or approved RPA/API flow, generate a submission plan that includes official-channel preflight, login authority, package hash, timestamp, receipt capture, audit entry, docket entry, and rollback/escalation steps.

## Standard End-to-End Pipeline

0. Karpathy preflight
   - Read `references/karpathy-preflight.md`.
   - State assumptions, smallest sufficient action, evidence, brittle AI points, success criteria, and stop rule.
   - For fee or payment actions, verify fee authority before doing anything else.

1. Case intake
   - Identify route, jurisdiction, filing type, urgency, priority deadline, business goal, and materials received.
   - For a full local pre-submission run, use `scripts/orchestrate_pre_submission_pipeline.py` with raw input files, an AI disclosure-confirmation packet template, an AI self-filing source template, and optionally an official-preflight source template. Add `--reference-delta-source reference-delta-source.json` when cited patents should be turned into a reference-patent delta before drafting. This command runs intake, disclosure confirmation, optional reference-delta generation, draft generation, evidence provenance, abnormal-filing risk, AI self-filing package validation, application-materials generation, quality review, local official-channel preflight readiness, approved-adapter preflight, and a lifecycle audit hard gate, then stops at `approved_for_adapter_execution` before any adapter execution or automatic submission.
   - After the full pre-submission pipeline passes, run `scripts/prepare_pre_submission_handoff_package.py` to create a read-only execution handoff package that copies and hash-binds final official documents, application materials, official preflight, approved-adapter request, lifecycle trace, receipt plan, audit plan, and docket plan without executing the adapter or claiming submission.
   - For one offline command that performs both steps, run `scripts/orchestrate_pre_submission_to_handoff.py`; it creates nested `pre-submission-pipeline/` and `pre-submission-handoff-package/` folders, validates both, writes `pre-submission-to-handoff-result.json`, and still stops before adapter execution, login, upload, signature, payment, submission, receipt capture, or application-number evidence.
   - For a received case inbox, run `scripts/orchestrate_inbox_to_handoff.py`; each child folder is one case, optional `case-config.json` may set `case_id`, `raw_input_dir`, and `reference_delta_source`, and the command validates every generated handoff package plus a dry-run queue without advancing beyond approved-adapter execution readiness.
   - After inbox-to-handoff passes, run `scripts/prepare_inbox_handoff_index.py` to create `inbox-handoff-index.json`, `inbox-handoff-index.md`, and `artifact-hashes.json`; the index must preserve each case ID, status, decision, legal gate, quality gate, reference-delta evidence, handoff package hash, next action, and no-official-action flags.
   - After the handoff index validates, run `scripts/prepare_skill_completion_audit.py` to create `skill-completion-audit.json`, `skill-completion-audit.md`, and `artifact-hashes.json`; the audit must cover reference-patent delta, application-materials generation, AI legal/compliance gate, no-external-lawyer mode, batch inbox processing, unsafe inbox rejection, hash binding, read-only handoff, handoff index, runbook, regression gate contract, and official boundary without claiming submission.
   - Create a case record with missing information and assumptions.
   - For raw material folders, read `references/case-package-protocol.md` and run `scripts/prepare_case_package.py` to create a standard case package.
   - Raw material intake must reject symlinks or linked files; copied source files must resolve inside the raw input directory and package targets must resolve inside `00-intake/source-files`.
   - When the user wants one offline intake command, read `references/case-intake-orchestration.md` and run `scripts/orchestrate_case_intake.py`.
   - Validate `case-package-manifest.json` with `scripts/validate_case_package_manifest.py`.
   - Use `assets/templates/source-material-manifest.yaml` to record received files, safe relative material filenames, exact lowercase `sha256:<64 hex>` hashes, confidentiality, provenance, and claim-support links.
   - Run `scripts/validate_source_material_manifest.py` when a structured manifest is available; when files are local, validate with a base directory so material filenames are rejected if absolute or path-traversing and material file hashes are recomputed.

2. Invention disclosure normalization
   - For case-package-to-disclosure scaffolding, read `references/disclosure-normalization.md`.
   - Run `scripts/normalize_invention_disclosure.py` to create `invention-disclosure-scaffold.json`, `normalization-report.md`, and `artifact-hashes.json`.
   - Run `scripts/validate_invention_disclosure_scaffold.py` on the scaffold.
   - Keep scaffold status at `scaffold_pending_confirmation`, with `filing_allowed=false` and `draft_generation_allowed=false`, until inventor, applicant/ownership, no-copying, evidence, secrecy, and legal confirmations are supplied.
   - When structured confirmations arrive, read `references/disclosure-confirmation.md`, validate `assets/templates/disclosure-confirmation-packet.json` with `scripts/validate_disclosure_confirmation_packet.py`, and run `scripts/confirm_invention_disclosure.py`.
   - Treat confirmed `invention-disclosure.json` as draft-only input: `draft_generation_allowed=true`, `filing_allowed=false`, and filing legal gate remains failed until AI self-filing authorization plus applicant authorization pass on the no-external-lawyer route, or until counsel/agent review plus applicant authorization pass on the reviewed-package route.
   - For confirmed draft generation, read `references/patent-generation-engine.md`.
   - For generating draft-only review artifacts, read `references/draft-package-generation.md` and run `scripts/generate_draft_package.py`.
   - Use `assets/templates/invention-disclosure-form.yaml`.
   - Run `scripts/validate_invention_disclosure.py` when a structured disclosure is available.
   - Generate `assets/templates/patent-application-draft.md` only from supported disclosure facts.
   - Run `scripts/validate_patent_application_draft.py` before presenting a draft as review-ready.
   - Run `scripts/prepare_draft_evidence_provenance.py` when a draft package has source materials; every claim limitation evidence hash must be exact lowercase `sha256:<64 hex>`, trace to file-bound applicant/inventor/R&D source material, and reference/prior-art material must not be used as the applicant's own claim support. If the draft package includes `reference-patent-delta.json`, provenance must validate and hash-bind it as boundary evidence only.
   - Run `scripts/prepare_abnormal_filing_risk_assessment.py` after draft evidence provenance; it must preserve exact source-material hashes and document G8 non-abnormal filing checks for real inventive activity, no random generation, no simple replacement of prior art, supported effects, no patchwork, no malicious batch pattern, and inventor/applicant consistency.
   - Stop in draft-only mode if the case appears copied, randomly generated, unsupported, or lacks real technical contribution evidence.
   - After final counsel or patent-agent filing review and applicant authorization are supplied as `submission-authorization-packet.json`, read `references/validated-filing-package.md` and run `scripts/prepare_validated_filing_package.py`.
   - If no external lawyer or patent agent is used, read `references/ai-self-filing-gate.md`, validate `ai-self-filing-authorization-packet.json`, and run `scripts/prepare_ai_self_filing_package.py`.
   - Filing package validation must use exact lowercase `sha256:<64 hex>` values and bind source draft, authorization packet, and every final document listed in `final_documents`/`documents` to local file hashes before official-channel preflight.
   - After a package validates, read `references/application-materials-generation.md` and run `scripts/prepare_patent_application_materials.py` to generate claims, specification, abstract, drawings plan, request-form metadata, XML readiness checklist, and hash-bound material inventory before official-channel preflight.
   - Application materials validation must use exact lowercase `sha256:<64 hex>` values for source package hashes, provenance hashes, abnormal-risk hashes, generated material file hashes, request metadata, document generation plan, XML readiness, own-support/prohibited-reference hashes, and official inventory hashes; generated material paths must be relative, stay inside the materials bundle, and recompute against local copied provenance/risk files and generated artifacts.
   - Claims, specification, abstract, and drawing-plan materials must not contain missing-source-section placeholders; hash-correct files still fail if their content is only a "section not found in source draft" substitute.
   - After application materials validate, run `scripts/prepare_application_materials_quality_review.py`; `application-materials-quality-review.json` must recompute the materials hash, include the exact expected check IDs for every quality dimension, derive each dimension score from those checks, score at least 85 overall with every dimension at least 7, keep official-action flags false, and pass `scripts/validate_application_materials_quality_review.py` before official-channel preflight.
   - Package validation may advance only to `package_valid_official_preflight_pending`; it must not mark submitted, receipted, accepted, paid, or application-number received.

3. Legal gate
   - Read `references/legal-gates.md`.
   - Verify the selected legal gate mode: counsel/agent review, or AI self-filing with no external lawyer and no mandatory-agent condition.
   - Verify authorization, inventor, ownership, secrecy review, agency or self-filing eligibility, signature, and fee authority.
   - Stop if any hard gate fails.

4. Agent team review when requested or high-risk
   - Read `references/advisory-board-agent-team.md`.
   - Use person skills as advisory lenses only.
   - Record seat-by-seat findings, disagreements, legal gates, and stop/proceed decision.

5. Strategic classification
   - Classify the case as core asset, peripheral asset, defensive publication, continuation/divisional candidate, PCT candidate, SEP candidate, licensing asset, or low-value filing.
   - Produce capital rationale: moat, transaction value, financing relevance, competitive coverage, and maintenance burden.

6. Prior-art diligence
   - Build closest-prior-art table from patents, literature, products, standards, and user-provided references.
   - When a concrete cited-patent set is provided, run `scripts/prepare_reference_patent_delta.py` and `scripts/validate_reference_patent_delta.py` before claim drafting; cited patents may define boundaries, risks, and fallback positions, but must not supply applicant claim support or novelty/patentability guarantees.
   - Separate fact, inference, and recommendation.
   - Do not claim novelty or patentability as a guarantee.

7. Inventive concept distillation
   - Extract technical problem, technical means, technical effect, necessary features, optional features, alternatives, and implementation evidence.
   - Mark unsupported or AI legal/compliance-confirmation-required statements.

8. Claim architecture
   - Draft or review independent claims, dependent fallback ladder, apparatus/system/method/medium variants, parameter ranges, and embodiment support.
   - Map each claim element to specification support.
   - Run `scripts/validate_claim_support_map.py` before treating a populated support map as filing-readiness evidence.

9. Specification and drawing check
   - Ensure claim support, antecedent basis, drawings references, embodiments, alternatives, technical effects, and industrial applicability.
   - Flag unsupported performance claims and vague AI/algorithm terms.

10. Red-team review
   - Simulate examiner, invalidity petitioner, competitor design-around, and litigation proof issues.
   - Produce severity, evidence, mitigation, and owner.

11. Filing operations
   - Read `references/cnipa-filing-readiness.md` for CNIPA matters.
   - Read `references/official-channel-facts.md` for current source baseline.
   - Read `references/filing-execution-boundary.md` before planning official interaction.
   - Use `assets/templates/official-channel-preflight.yaml`, `assets/templates/receipt-capture.yaml`, `assets/templates/audit-log-entry.yaml`, and `assets/templates/docket-entry.yaml`.
   - Use `assets/templates/filing-package-manifest.yaml` and run `scripts/validate_filing_package_manifest.py` before official-channel preflight.
   - Run `scripts/validate_official_channel_preflight.py` when a structured official-channel preflight is available.
   - Run `scripts/validate_filing_status_transition.py` when status advances between filing states; it must reject missing pre-submission `official_system_touched=false`, submitted-or-later statuses without official-action evidence, ready-or-later statuses without exact `final_package_hash` and `reviewed_package_hash`, AI self-filing states with `external_lawyer_involved` not false, and any generator-side official action flag.
   - When validated package and official preflight evidence are available, read `references/ready-for-authorized-filing.md` and run `scripts/prepare_ready_for_authorized_filing.py`.
   - Advancing to `ready_for_authorized_filing` is a handoff or approved-adapter-preflight state only; it must not mark uploaded, signed, paid, submitted, receipted, accepted, or application-number received.
   - Validate XML/schema/tool version, forms, attachments, signatures, fees, deadlines, priority claims, and exact package hashes.
   - Do not confuse preview with filing.
   - Before relying on post-adapter artifacts as real official evidence, read `references/production-official-evidence-gate.md` and run `scripts/validate_production_official_evidence_gate.py` on `production-official-evidence-packet.json`. Benchmark, mock, placeholder, or production-shape-test evidence must fail the strict production gate; when reference-delta metadata is present, adapter execution, receipt capture, application-number evidence, and the packet must preserve the same application-materials hash, reference-patent delta hash, positive counts, and `reference_delta_boundary_preserved=true`.
   - Before any approved adapter may use an official account/session boundary, read `references/official-session-authorization.md` and run `scripts/validate_official_session_authorization.py` on `official-session-authorization-packet.json`. Benchmark, placeholder, unsafe, credential-bearing, or production-shape-test session evidence must fail strict authorization.

12. Submission or handoff
   - If legal gate and official-channel requirements pass, prepare authorized submission steps and receipt capture.
   - If submission cannot be lawfully automated, produce a ready-to-submit handoff for the authorized person.
   - Before treating any adapter as production-ready, read `references/production-adapter-readiness.md` and run `scripts/validate_production_adapter_readiness.py` on `production-adapter-readiness-packet.json`. Benchmark, mock, placeholder, unsafe, or production-shape-test adapter evidence must not authorize real execution.
   - Before any `approved_adapter` execution attempt, read `references/official-session-authorization.md` and `references/approved-adapter-preflight.md`, bind a strict production adapter readiness packet and a strict official session authorization packet, create `assets/templates/approved-adapter-preflight.json`, and run `scripts/validate_approved_adapter_preflight.py`.
   - When ready-for-authorized-filing evidence and adapter approval evidence are available, run `scripts/prepare_approved_adapter_preflight.py` to create `approved-adapter-preflight.json`, `filing-adapter-request.json`, `adapter-boundary-report.md`, audit plan, docket plan, and hash manifest.
   - Approved-adapter preflight, audit/docket plan internals, and filing-adapter request/response hashes must use exact lowercase `sha256:<64 hex>` values; validators must recompute local referenced files and compare request/response hashes back to the referenced preflight or execution-result artifact. Use a plain `pending` marker, not a fake `sha256:*`, for downstream hashes that cannot exist before materialization.
   - Passing approved-adapter preflight allows only an adapter execution attempt; it is not evidence of submission, receipt, acceptance, or application number.
   - After an approved adapter returns a result, read `references/adapter-execution-result.md`, validate `assets/templates/adapter-execution-result.json` with `scripts/validate_adapter_execution_result.py`, or run `scripts/prepare_adapter_execution_result.py` against an independently supplied `adapter-execution-source.json`, and advance only to `submitted_pending_receipt`.
   - Adapter execution evidence must use exact lowercase `sha256:<64 hex>` values and bind submitted-pending status snapshot plus submitted file-list evidence to local file hashes before any `submitted_pending_receipt` status is accepted.
   - Do not advance from `submitted_pending_receipt` to `official_receipt_received` until `scripts/validate_receipt_capture.py` passes with receipt evidence; status may record `official_system_touched=true` only as independently supplied official evidence, while `generator_official_system_touched` remains false.

13. Docketing and portfolio update
   - Record application number or receipt status, deadlines, fee events, office-action windows, family links, portfolio tags, and next actions.
   - Run `scripts/validate_receipt_capture.py` before marking any receipt-driven status.
   - Receipt capture evidence must use exact lowercase `sha256:<64 hex>` values; when a receipt or payment receipt file path is present, the validator or generator must recompute the file hash and reject mismatches.
   - When a `submitted_pending_receipt` case has independently supplied official receipt evidence, run `scripts/prepare_receipt_capture.py` against `receipt-capture-source.json` and advance only to `official_receipt_received`.
   - Run `scripts/validate_application_number_evidence.py` before marking `accepted_or_application_number_received`.
   - Application-number evidence must use exact lowercase `sha256:<64 hex>` values and bind the receipt file, official status snapshot file, official file-list file, and paid payment receipt file when applicable.
   - When official receipt evidence and independently supplied application-number evidence are available, run `scripts/prepare_application_number_acceptance.py` against `application-number-source.json`.
   - Keep mock receipt or mock application-number evidence separate from production evidence and mark it explicitly.
   - Build `assets/templates/case-lifecycle-trace.json` or run `scripts/prepare_case_lifecycle_trace.py`, then run `scripts/validate_case_lifecycle_trace.py` when a case completes a major filing lifecycle or enters portfolio operations. For the AI self-filing cited-patent chain, run `scripts/prepare_case_lifecycle_trace.py --route ai_self_filing_no_external_lawyer --reference-delta`.

14. Case processor / adapter boundary
   - Read `references/case-processor-state-machine.md`, `references/filing-adapter-interface.md`, and `references/approved-adapter-preflight.md` when adapter mode is requested.
   - Use `assets/templates/case-record.json`, `assets/templates/filing-adapter-request.json`, and `assets/templates/filing-adapter-response.json`.
   - Run `scripts/validate_case_record.py`, `scripts/validate_filing_adapter_contract.py`, and `scripts/validate_approved_adapter_preflight.py` when `execution_mode=approved_adapter`.
   - In `dry_run` or `handoff`, keep the case at `ready_for_authorized_filing` unless a lawful official action actually occurs.
   - In `approved_adapter`, keep the case at `approved_for_adapter_execution` until an adapter response proves official submission action.
   - In offline queues, `approved_adapter` is evidence-only and requires `approved_adapter_evidence_mode=true`; the runner validates supplied adapter execution evidence but does not execute an adapter or touch official systems.
   - For any `submitted_pending_receipt` claim, run `scripts/validate_adapter_execution_result.py`, `scripts/validate_filing_adapter_contract.py response`, and `scripts/validate_filing_status_transition.py`.

15. Case queue batch processor
   - Read `references/case-queue-batch-processor.md` before accepting multiple cases, folders, or filing tasks in one batch.
   - Use `assets/templates/case-queue.json` and `assets/templates/batch-processor-result.json`.
   - Use `scripts/build_case_queue.py` to create a structured dry-run, handoff, or approved-adapter evidence queue from received case folders.
   - Use `scripts/run_case_queue.py` for local dry-run, handoff, or approved-adapter evidence queue execution when a structured queue is available.
   - Use `scripts/orchestrate_case_workflow.py` when the user wants build-queue, run-queue, report, and hash manifest in one offline command.
   - Run `scripts/validate_case_queue.py`, `scripts/validate_batch_processor_result.py`, and the relevant per-case validators.
   - In `dry_run` or `handoff`, set `official_system_touched=false` and `official_submission_performed=false` for the batch and for every case.
   - Report every case independently with decision, status, validators, errors, warnings, owner, and next action.

## Output Contract

Every substantial output must include:

- Karpathy preflight result.
- Route and case status.
- Inputs received and missing items.
- Legal gate result.
- Business/IP capital rationale.
- Technical and patent-drafting analysis.
- Filing readiness or deficiency report.
- Risks with severity and owner.
- Source material manifest and artifact hashes when files are involved.
- Audit log entries to create.
- Next action and stop/proceed decision.

For direct filing workflows, include:

- "Not filed yet", "ready for authorized filing", "submitted pending official receipt", or "official receipt received" status.
- Official-channel preflight status.
- Version hashes used for filing.
- Official receipt and application number fields, even if pending.

## Stop Conditions

Stop and do not file when:

- Karpathy preflight was skipped or cannot identify assumptions, evidence, success criteria, and stop rule.
- Neither counsel/patent-agent review nor validated AI self-filing authorization is tied to the final version.
- AI self-filing is requested but a mandatory-agent condition, foreign/HMT applicant condition for this route, or agency-bypass request exists.
- Applicant authorization is absent, ambiguous, expired, or outside scope.
- Inventor or ownership confirmation is missing.
- Secrecy/foreign-filing status is unresolved for relevant invention or utility model matters.
- XML/schema/package validation fails.
- Official-channel preflight, receipt-capture plan, audit-log plan, or docket plan is missing.
- Official system demands human-only confirmation and no lawful authorized automation path exists.
- The request asks to bypass official access controls, signatures, captchas, authorization, or legal review.
- The filing package hash differs from the reviewed or AI-reviewed package hash.
- The user asks to fabricate, hide, or misrepresent any legal or technical fact.

## Benchmark Mode

When testing this skill with sample patents:

1. Create an IP investment memo.
2. Build a prior-art matrix.
3. Distill the inventive concept.
4. Draft a claim architecture.
5. Build a claim support map with `assets/templates/claim-support-map.md`.
6. Validate the claim support map with `scripts/validate_claim_support_map.py` when populated.
7. Run red-team review.
8. Produce legal gate and filing readiness checklist.
9. Score the output using `references/quality-rubric.md`.
10. Run `scripts/validate_benchmark_gate.py` before treating the benchmark as complete.
11. Record Darwin evidence in `results.tsv`, prompt runs, source captures, and artifact hashes when available.
12. Run `scripts/validate_artifact_hash_manifest.py` when `artifact-hashes.json` is present; it must reject unsafe or duplicate artifact paths, non-exact lowercase `sha256:<64 hex>` values, invalid byte counts, missing artifacts, and hash mismatches.
13. After skill, script, template, or benchmark changes, read `references/regression-gate.md` and run `scripts/run_regression_gate.py --json`; it must include JSON/YAML parse checks and positive structured benchmark scans for `sha256:*` placeholders and dangerous `true` booleans. When verification must be handed off or archived, also run it with `--output-dir` and validate the generated `artifact-hashes.json`.

For positive authorized-filing readiness benchmarks:

1. Use `benchmarks/authorized-cn-ready-for-filing/` as the pattern.
2. Run `scripts/validate_submission_packet.py`.
3. Run `scripts/validate_official_channel_preflight.py`.
4. Run `scripts/validate_authorized_ready_benchmark.py`.
5. Keep status at `ready_for_authorized_filing` until a lawful official-channel action creates receipt evidence.

For incoming-disclosure-to-application benchmarks:

1. Use `benchmarks/incoming-disclosure-to-application/` as the pattern.
2. Run `scripts/validate_source_material_manifest.py`.
3. Run `scripts/validate_invention_disclosure.py`.
4. Run `scripts/validate_patent_application_draft.py`.
5. Run `scripts/validate_claim_support_map.py`.
6. Run `scripts/validate_incoming_application_benchmark.py`.
7. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
8. Keep status at `draft_only` and decision `do_not_file` until AI self-filing legal/compliance authorization and applicant authorization are added for the no-external-lawyer route.
9. Confirm the incoming-disclosure draft, claim support map, source manifest, and disclosure do not default to attorney, lawyer, counsel, patent-agent, or patent agent review wording.

For source-material-file-binding-rejection benchmarks:

1. Use `benchmarks/source-material-file-binding-rejection/` as the pattern.
2. Run `scripts/validate_source_material_file_binding_rejection_benchmark.py`.
3. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
4. Confirm missing material files, material hash mismatches, source-package hash mismatches, malformed SHA-256 fields, unknown claim-support material IDs, prior-art marked usable for claim support, and claim-support links to prior art all fail before drafting or filing.

For case-package-intake-dry-run benchmarks:

1. Use `benchmarks/case-package-intake-dry-run/` as the pattern.
2. Run `scripts/prepare_case_package.py` from `raw-input/` to produce `case-package/`.
3. Run `scripts/validate_case_package_manifest.py`.
4. Run `scripts/validate_source_material_manifest.py`.
5. Run `scripts/validate_case_package_benchmark.py`.
6. Confirm filing is not allowed, no official action fields are true, the default legal gate mode is `ai_self_filing_no_external_lawyer`, and no intake report or source manifest defaults to attorney, lawyer, counsel, patent-agent, or patent agent review.

For case-package-orchestration-dry-run benchmarks:

1. Use `benchmarks/case-package-orchestration-dry-run/` as the pattern.
2. Run `scripts/orchestrate_case_intake.py` from a raw input folder to produce case package, disclosure scaffold, queue, batch result, report, and hash manifest.
3. Run `scripts/validate_case_intake_orchestration_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm status remains `intake_received` and disclosure remains `scaffold_pending_confirmation`.
6. Confirm filing and draft generation remain disallowed, AI legal/compliance confirmation remains pending, and no report/source manifest/scaffold defaults to attorney, lawyer, counsel, patent-agent, or patent agent review.
7. Confirm the case package, disclosure scaffold, queue item, and batch result row preserve `legal_gate_mode=ai_self_filing_no_external_lawyer` and `external_lawyer_involved=false`.

For disclosure-normalization-scaffold benchmarks:

1. Use `benchmarks/disclosure-normalization-scaffold/` as the pattern.
2. Run `scripts/normalize_invention_disclosure.py` from a validated case package.
3. Run `scripts/validate_invention_disclosure_scaffold.py`.
4. Run `scripts/validate_disclosure_normalization_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
6. Confirm inventor confirmation, AI legal/compliance gate, and no-copying confirmation remain pending.
7. Confirm filing and draft generation remain disallowed and no scaffold or normalization report defaults to attorney, lawyer, counsel, patent-agent, or patent agent review.
8. Confirm the scaffold top level and `scaffold_controls` preserve `legal_gate_mode=ai_self_filing_no_external_lawyer` and `external_lawyer_involved=false`.

For scaffold-confirmation-to-disclosure benchmarks:

1. Use `benchmarks/scaffold-confirmation-to-disclosure/` as the pattern.
2. Run `scripts/validate_disclosure_confirmation_packet.py`.
3. Run `scripts/confirm_invention_disclosure.py` to produce `invention-disclosure.json`, `filing-status.json`, `confirmation-report.md`, and `artifact-hashes.json`.
4. Run `scripts/validate_invention_disclosure.py`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_scaffold_confirmation_benchmark.py`.
7. Confirm draft generation is allowed but filing remains disallowed.
8. Confirm the confirmation packet uses AI legal/compliance draft review only, `external_lawyer_involved=false`, exact source/evidence hashes, and separated prohibited reference hashes.
9. Confirm final filing legal gate remains failed until final AI self-filing legal/compliance authorization, applicant filing authorization, official-channel preflight, agency/signature authority, and fee authority pass.

For disclosure-confirmation-rejection benchmarks:

1. Use `benchmarks/disclosure-confirmation-rejection/` as the pattern.
2. Run `scripts/validate_disclosure_confirmation_rejection_benchmark.py`.
3. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
4. Confirm patent-agent, attorney, in-house counsel, external-lawyer flags, malformed hash fields, unknown technical-effect hashes, and prohibited reference hashes are rejected before draft generation or filing.

For draft-package-generation benchmarks:

1. Use `benchmarks/draft-package-generation/` as the pattern.
2. Run `scripts/generate_draft_package.py` from a confirmed `invention-disclosure.json`.
3. Run `scripts/validate_patent_application_draft.py`.
4. Run `scripts/validate_claim_support_map.py --allow-draft`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_draft_package_generation_benchmark.py`.
7. Confirm draft generation is allowed but filing remains disallowed.
8. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, and the generated draft, claim support map, and report do not default to attorney, lawyer, counsel, patent-agent, or patent agent review.
9. Confirm no official receipt, application number, signature, fee payment, or official-channel action is claimed.

For draft-package-reference-delta benchmarks:

1. Use `benchmarks/draft-package-reference-delta/` as the pattern.
2. Run `scripts/prepare_reference_patent_delta.py` to create `reference-patent-delta.json`.
3. Run `scripts/generate_draft_package.py` with `--reference-delta reference-patent-delta.json`.
4. Run `scripts/validate_draft_package_generation_benchmark.py`.
5. Confirm the reference delta validates, its case ID matches the disclosure, the draft contains a `Reference Patent Delta Strategy`, the claim support map uses the delta rows instead of generic prior-art comparison placeholders, reference patents remain boundary evidence only, and no official action or external lawyer involvement occurs.

For draft-package-to-filing-validation benchmarks:

1. Use `benchmarks/draft-package-to-filing-validation/` as the pattern.
2. Supply a real `submission-authorization-packet.json`; do not generate attorney approval or applicant authorization from draft contents.
3. Ensure source draft, authorization packet, claims, specification, abstract, drawings, and request metadata files exist and match exact `sha256:<64 hex>` values.
4. Run `scripts/prepare_validated_filing_package.py`.
5. Run `scripts/validate_submission_packet.py`.
6. Run `scripts/validate_filing_package_manifest.py`.
7. Run `scripts/validate_filing_status_transition.py`.
8. Run `scripts/validate_validated_filing_package_benchmark.py`.
9. Confirm status is `package_valid_official_preflight_pending` and no official submission, receipt, fee payment, signature, or application number is claimed.

For ai-self-filing-package-validation benchmarks:

1. Use `benchmarks/ai-self-filing-package-validation/` as the pattern.
2. Supply a real or benchmark `ai-self-filing-source.json`; do not generate applicant authority, inventor facts, ownership, or legal/compliance evidence from draft contents.
3. Bind `ai_compliance_review.abnormal_filing_risk_assessment` to a same-case `abnormal-filing-risk-assessment.json` artifact path and exact lowercase `sha256:<64 hex>` artifact hash with `risk_level=low`.
4. Run `scripts/prepare_ai_self_filing_package.py`; the generator must write source draft and final material files into the package and bind the filing-package manifest document hashes to those files.
5. Run `scripts/validate_ai_self_filing_authorization.py`.
6. Run `scripts/validate_filing_package_manifest.py`.
7. Run `scripts/validate_filing_status_transition.py`.
8. Run `scripts/validate_ai_self_filing_package_benchmark.py`.
9. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, all AI legal gate review checks pass, abnormal-filing risk evidence path/hash is file-bound, no legal advice/lawyer/patent-agent review is claimed, no mandatory-agent condition exists, and no official submission, receipt, fee payment, signature, or application number is claimed.

For ai-self-filing-package-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-package-reference-delta/` as the pattern.
2. Use `benchmarks/draft-package-reference-delta/` as the draft input and bind `ai_compliance_review.abnormal_filing_risk_assessment.artifact_path` to `benchmarks/abnormal-filing-risk-reference-delta/abnormal-filing-risk-assessment.json`.
3. Run `scripts/prepare_ai_self_filing_package.py`.
4. Run `scripts/validate_ai_self_filing_authorization.py`.
5. Run `scripts/validate_ai_self_filing_package_benchmark.py`.
6. Confirm the generated authorization packet preserves `reference_patent_delta_hash`, `reference_delta_rows_count`, `reference_delta_claim_elements_count`, and `reference_delta_boundary_preserved=true` from the abnormal-filing risk assessment while still treating reference patents as boundary evidence only.
7. Confirm no legal advice/lawyer/patent-agent review, official upload, signature, payment, submission, receipt, or application number is claimed.

For ai-self-filing-application-materials benchmarks:

1. Use `benchmarks/ai-self-filing-application-materials/` as the pattern.
2. Use `benchmarks/ai-self-filing-package-validation/` as the validated package input, `benchmarks/draft-package-generation/` as the draft input, and `benchmarks/ai-self-filing-draft-evidence-provenance/` as the claim-support provenance input.
3. Run `scripts/prepare_patent_application_materials.py`.
4. Run `scripts/validate_patent_application_materials.py`.
5. Run `scripts/validate_patent_application_materials_benchmark.py`.
6. Run `scripts/validate_artifact_hash_manifest.py`.
7. Confirm generated claims, specification, abstract, drawings plan, request-form metadata, document generation plan, XML readiness checklist, source filing-package manifest hash, official material inventory source-manifest match, draft evidence provenance hash, same-case abnormal-risk assessment hash, and filing status all validate.
8. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, no legal advice/lawyer/patent-agent review is claimed, status remains `package_valid_official_preflight_pending`, and no official system is touched, uploaded to, signed, paid, submitted, receipted, or assigned an application number.

For ai-self-filing-application-materials-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-application-materials-reference-delta/` as the pattern.
2. Use `benchmarks/ai-self-filing-package-reference-delta/` as the validated package input, `benchmarks/draft-package-reference-delta/` as the draft input, and `benchmarks/draft-reference-delta-evidence-provenance/` as the claim-support provenance input.
3. Run `scripts/prepare_patent_application_materials.py`.
4. Run `scripts/validate_patent_application_materials.py`.
5. Run `scripts/validate_patent_application_materials_benchmark.py`.
6. Confirm `application-materials.json` preserves the same `reference_patent_delta_hash`, row count, and claim-element count across both `evidence_provenance` and `abnormal_filing_risk_assessment`, with `reference_delta_boundary_preserved=true`.
7. Confirm reference patents remain boundary and claim-strategy evidence only, not applicant claim support, and no official action or external lawyer involvement occurs.

For application-materials-quality-gate benchmarks:

1. Use `benchmarks/application-materials-quality-gate/` as the pattern.
2. Run `scripts/prepare_application_materials_quality_review.py` against `benchmarks/ai-self-filing-application-materials/`.
3. Run `scripts/validate_application_materials_quality_review.py`.
4. Run `scripts/validate_application_materials_quality_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
6. Confirm the quality review recomputes the application-materials hash, validates the underlying materials, requires exact dimension check IDs, rejects forged or non-recomputed dimension scores, scores at least 85 overall, keeps every dimension at least 7, reaches enterprise-ready score when benchmark material satisfies all checks, and keeps official-system/submission/external-lawyer flags false.

For reference-patent-delta benchmarks:

1. Use `benchmarks/reference-patent-delta/` as the pattern.
2. Run `scripts/prepare_reference_patent_delta.py` from `reference-delta-source.json`.
3. Run `scripts/validate_reference_patent_delta.py` on `reference-patent-delta.json`.
4. Run `scripts/validate_reference_patent_delta_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py` on `artifact-hashes.json`.
6. Confirm all cited CN reference patents are boundary evidence only, every claim element has applicant-owned file-bound support, every claim element has a delta row, no reference/prior-art material is used as applicant support, no novelty or patentability guarantee is claimed, and no official action or external lawyer involvement occurs.

For application-materials-pipeline benchmarks:

1. Use `benchmarks/application-materials-pipeline/` as the pattern.
2. Run `scripts/orchestrate_application_materials_pipeline.py` from a validated AI self-filing package, draft package, and draft-evidence provenance folder.
3. Run `scripts/validate_application_materials_pipeline_benchmark.py`.
4. Run `scripts/validate_patent_application_materials_benchmark.py` on the nested `application-materials/` folder.
5. Run `scripts/validate_application_materials_quality_benchmark.py` on the nested `application-materials-quality-gate/` folder.
6. Run `scripts/validate_artifact_hash_manifest.py` on the top-level `artifact-hashes.json`.
7. Confirm the pipeline result keeps `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, `official_system_touched=false`, `official_submission_performed=false`, and stops at `package_valid_official_preflight_pending` with official-channel preflight required.

For application-materials-pipeline-reference-delta benchmarks:

1. Use `benchmarks/application-materials-pipeline-reference-delta/` as the pattern.
2. Run `scripts/orchestrate_application_materials_pipeline.py` from `benchmarks/ai-self-filing-package-reference-delta/`, `benchmarks/draft-package-reference-delta/`, and `benchmarks/draft-reference-delta-evidence-provenance/`.
3. Run `scripts/validate_application_materials_pipeline_benchmark.py`.
4. Run `scripts/validate_patent_application_materials_benchmark.py` on the nested `application-materials/` folder.
5. Run `scripts/validate_application_materials_quality_benchmark.py` on the nested `application-materials-quality-gate/` folder.
6. Confirm the nested application materials preserve the reference-delta hash/count/boundary fields and the pipeline still performs no official upload, signature, payment, submission, receipt, application-number capture, or external-lawyer route.

For ai-self-filing-official-ready-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-official-ready-reference-delta/` as the pattern.
2. Run `scripts/prepare_ready_for_authorized_filing.py` from `benchmarks/ai-self-filing-package-reference-delta/` plus an official preflight source that points at `benchmarks/ai-self-filing-application-materials-reference-delta/application-materials.json`.
3. Run `scripts/validate_ready_for_authorized_filing_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` on `artifact-hashes.json`.
5. Confirm the official preflight, filing status, and readiness report preserve the same `application_materials.hash`, `reference_patent_delta_hash`, positive delta row/claim-element counts, and `reference_delta_boundary_preserved=true`.
6. Confirm reference patents remain boundary evidence only and the benchmark performs no official upload, signature, payment, submission, receipt, application-number capture, or external-lawyer route.

For ai-self-filing-approved-adapter-preflight-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-approved-adapter-preflight-reference-delta/` as the pattern.
2. Run `scripts/prepare_approved_adapter_preflight.py` from `benchmarks/ai-self-filing-official-ready-reference-delta/`, `benchmarks/ai-self-filing-package-reference-delta/`, and an independently supplied approved-adapter source.
3. Run `scripts/validate_generated_approved_adapter_preflight_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` on `artifact-hashes.json`.
5. Confirm the approved-adapter preflight, adapter request, filing status, audit input hashes, and adapter boundary report preserve the same `application_materials.hash`, `reference_patent_delta_hash`, positive delta row/claim-element counts, and `reference_delta_boundary_preserved=true`.
6. Confirm reference patents remain boundary evidence only and the benchmark performs no official upload, adapter execution, signature, payment, submission, receipt, application-number capture, or external-lawyer route.

For pre-submission-pipeline benchmarks:

1. Use `benchmarks/pre-submission-pipeline/` as the pattern.
2. Run `scripts/orchestrate_pre_submission_pipeline.py` from raw input files plus AI-only confirmation and self-filing source templates.
3. Run `scripts/validate_pre_submission_pipeline_benchmark.py`.
4. Confirm the nested case package, disclosure confirmation, draft package, draft-evidence provenance, abnormal-filing risk, AI self-filing package validation, application-materials pipeline, AI self-filing official-ready stage, AI self-filing approved-adapter preflight stage, and `case-lifecycle-trace/` all pass their own validators.
5. Run `scripts/validate_artifact_hash_manifest.py` on the top-level `artifact-hashes.json`.
6. Confirm `pre_submission_lifecycle_gate=passed`, `lifecycle_trace_hash` matches `case-lifecycle-trace/case-lifecycle-trace.json`, `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, `official_system_touched=false`, `official_submission_performed=false`, `adapter_execution_performed=false`, `automatic_submission_performed=false`, and final status is `approved_for_adapter_execution`.

For pre-submission-pipeline-reference-delta benchmarks:

1. Use `benchmarks/pre-submission-pipeline-reference-delta/` as the pattern.
2. Run `scripts/orchestrate_pre_submission_pipeline.py` with `--reference-delta-source benchmarks/reference-patent-delta/reference-delta-source.json`.
3. Run `scripts/validate_pre_submission_pipeline_benchmark.py`.
4. Confirm the optional `reference-patent-delta/` stage passes and the generated draft, provenance, abnormal-risk gate, AI self-filing package, application-materials pipeline, official-ready stage, approved-adapter preflight, and lifecycle trace all remain green.
5. Confirm `pre-submission-pipeline-result.json`, the generated AI self-filing source, nested application materials, and `case-lifecycle-trace/case-lifecycle-trace.json` preserve the same `reference_patent_delta_hash` with `reference_delta_boundary_preserved=true`.
6. Confirm reference patents remain boundary and claim-strategy evidence only, not applicant claim support, legal advice, filing authorization, official submission, receipt, or application-number evidence.

For pre-submission-handoff-package benchmarks:

1. Use `benchmarks/pre-submission-handoff-package/` and `benchmarks/pre-submission-handoff-package-reference-delta/` as the patterns.
2. Run `scripts/prepare_pre_submission_handoff_package.py` from the corresponding pre-submission pipeline benchmark.
3. Run `scripts/validate_pre_submission_handoff_package.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` on the handoff package `artifact-hashes.json`.
5. Build a queue from both handoff package folders and run `scripts/run_case_queue.py`.
6. Confirm the package is read-only, revalidates the source pre-submission pipeline, preserves AI-only legal mode and `external_lawyer_involved=false`, copies final package/application-material/official-ready/approved-adapter/lifecycle/receipt-plan/audit/docket evidence, and does not touch an official system, execute an adapter, submit, pay, sign, capture a receipt, or claim an application number.

For pre-submission-to-handoff benchmarks:

1. Use `benchmarks/pre-submission-to-handoff/` and `benchmarks/pre-submission-to-handoff-reference-delta/` as the patterns.
2. Run `scripts/orchestrate_pre_submission_to_handoff.py` from raw input files plus AI-only confirmation and self-filing source templates; include `--reference-delta-source` for the reference-delta variant.
3. Run `scripts/validate_pre_submission_to_handoff_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` on the top-level `artifact-hashes.json`.
5. Build a queue from both folders and run `scripts/run_case_queue.py`.
6. Confirm the nested pre-submission pipeline, nested handoff package, wrapper result, source pre-submission hash, handoff package hash, lifecycle trace hash, optional reference-delta hash/count/boundary fields, AI-only legal mode, and no-official-action flags all remain green.

For inbox-to-handoff benchmarks:

1. Use `benchmarks/inbox-to-handoff/` as the pattern.
2. Put received cases under `inbox/`, one child folder per case; each may include `case-config.json` and `raw-input/`, and at least one benchmark case must use `reference_delta_source`.
3. Run `scripts/orchestrate_inbox_to_handoff.py`.
4. Run `scripts/validate_inbox_to_handoff_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py` on the inbox-level `artifact-hashes.json`.
6. Build a queue from the inbox benchmark and run `scripts/run_case_queue.py`.
7. Confirm every processed case passes `validate_pre_submission_to_handoff_benchmark`, the inbox-level queue/result passes, reference-delta boundary evidence is preserved for the configured case, `external_lawyer_involved=false`, and no official system, adapter execution, submission, fee payment, receipt, or application-number action is claimed.

For inbox-to-handoff-rejection benchmarks:

1. Use `benchmarks/inbox-to-handoff-rejection/` as the pattern.
2. Run `scripts/validate_inbox_to_handoff_rejection_benchmark.py`.
3. Run `scripts/validate_artifact_hash_manifest.py` on the rejection benchmark `artifact-hashes.json`.
4. Build a queue from the rejection benchmark and run `scripts/run_case_queue.py`.
5. Confirm raw-input path traversal, reference-delta path traversal, missing raw input, empty inbox, and stale output reuse all fail before pre-submission generation.

For pre-submission-handoff-rejection benchmarks:

1. Use `benchmarks/pre-submission-handoff-rejection/` as the pattern.
2. Run `scripts/validate_pre_submission_handoff_rejection_benchmark.py`.
3. Run `scripts/validate_artifact_hash_manifest.py` on the rejection benchmark `artifact-hashes.json`.
4. Build a queue from the rejection benchmark and run `scripts/run_case_queue.py`.
5. Confirm lifecycle hash mismatch, official-action flag mutation, missing evidence role, copied evidence tamper, and reference-delta boundary mutation all fail before adapter execution.

For ai-self-filing-application-materials-binding-rejection benchmarks:

1. Use `benchmarks/ai-self-filing-application-materials-binding-rejection/` as the pattern.
2. Run `scripts/validate_ai_self_filing_application_materials_binding_rejection_benchmark.py`.
3. Confirm AI self-filing official-ready generation rejects missing application-materials paths, missing application-materials hashes, materials hash mismatches, missing materials files, and wrong artifact types.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm no official system is touched, no submission is performed, and no external lawyer is involved.

For patent-application-materials-rejection benchmarks:

1. Use `benchmarks/patent-application-materials-rejection/` as the pattern.
2. Run `scripts/validate_patent_application_materials_rejection_benchmark.py`.
3. Confirm malformed application materials reject missing applicant metadata, missing inventor metadata, missing generated claims materials, hash-correct missing-section placeholder materials, malformed hash fields, missing or hash-mismatched document generation plans, official material inventory source-manifest mismatch, source manifest hash mismatch, failed XML readiness, prior-art/reference claim support, final source-package hash mismatch, and missing safeguards.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm no official system is touched, no submission is performed, and no external lawyer is involved.

For ai-self-filing-legal-gate-rejection benchmarks:

1. Use `benchmarks/ai-self-filing-legal-gate-rejection/` as the pattern.
2. Run `scripts/validate_ai_self_filing_legal_gate_rejection_benchmark.py`.
3. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
4. Confirm legal-advice claims, lawyer/patent-agent review claims, missing stop-condition checks, failed legal gate checks, invalid hash shape, abnormal-risk artifact hash mismatch, missing abnormal-risk artifact file, missing AI legal gate review evidence, and missing/high-risk abnormal filing assessment evidence all fail for the expected reason.

For ai-self-filing-abnormal-risk-binding-rejection benchmarks:

1. Use `benchmarks/ai-self-filing-abnormal-risk-binding-rejection/` as the pattern.
2. Run `scripts/validate_ai_self_filing_abnormal_risk_binding_rejection_benchmark.py`.
3. Confirm package generation rejects missing abnormal-risk assessment paths, missing assessment artifacts, and artifact hash mismatches.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm no official system is touched, no submission is performed, and no external lawyer is involved.

For ai-self-filing-deficiency-report benchmarks:

1. Use `benchmarks/ai-self-filing-deficiency-report/` as the pattern.
2. Run `scripts/prepare_ai_self_filing_deficiency_report.py` from a failed AI self-filing authorization packet or rejection case.
3. Run `scripts/validate_ai_self_filing_deficiency_report_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm status is `legal_gate_failed`, decision is `do_not_file`, draft-only work remains allowed, deficiency rows include failed gate, missing/contradictory evidence, risk, required cure, and owner, and no official system is touched.

For ai-self-filing-cure-revalidation benchmarks:

1. Use `benchmarks/ai-self-filing-cure-revalidation/` as the pattern.
2. Run `scripts/prepare_ai_self_filing_cure_revalidation.py` from a valid deficiency folder and cured packet source.
3. Run `scripts/validate_ai_self_filing_cure_revalidation_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm the failed source packet still reproduces prior validator errors, the cured packet passes the AI self-filing authorization gate, status advances only to `ready_for_package_validation`, package validation remains required, and no official system is touched.

For draft-evidence-provenance-gate benchmarks:

1. Use `benchmarks/draft-evidence-provenance-gate/` as the pattern.
2. Run `scripts/prepare_draft_evidence_provenance.py` from a draft package plus source material manifest.
3. Run `scripts/validate_draft_evidence_provenance_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm every claim support row uses exact file-bound applicant/inventor/R&D source evidence, copied source material files match their hashes, prior-art or reference-patent material is not used as claim support, status remains draft-only, and no official action or external lawyer involvement occurs.

For draft-reference-delta-evidence-provenance benchmarks:

1. Use `benchmarks/draft-reference-delta-evidence-provenance/` as the pattern.
2. Run `scripts/prepare_draft_evidence_provenance.py` from `benchmarks/draft-package-reference-delta/` plus a source material manifest.
3. Run `scripts/validate_draft_evidence_provenance_benchmark.py`.
4. Confirm `reference-patent-delta.json` is copied, validated, and hash-bound in `draft-evidence-provenance.json`; it must remain boundary evidence only, while claim support rows continue to use applicant-owned evidence hashes.

For abnormal-filing-risk-gate benchmarks:

1. Use `benchmarks/abnormal-filing-risk-gate/` as the pattern.
2. Run `scripts/prepare_abnormal_filing_risk_assessment.py` from a source-backed draft package after draft evidence provenance.
3. Run `scripts/validate_abnormal_filing_risk_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm the G8 assessment is backed by exact applicant-source hashes, covers random computer generation, copied or simply replaced prior art, fabricated effects, obvious patchwork, unreasonable degradation, non-necessary narrowing, maliciously distributed batch filings, and false inventor/applicant risk; status remains draft-only, and no official action or external lawyer involvement occurs.

For abnormal-filing-risk-reference-delta benchmarks:

1. Use `benchmarks/abnormal-filing-risk-reference-delta/` as the pattern.
2. Run `scripts/prepare_abnormal_filing_risk_assessment.py` from `benchmarks/draft-reference-delta-evidence-provenance/`.
3. Run `scripts/validate_abnormal_filing_risk_benchmark.py`.
4. Confirm `reference_patent_delta_hash`, `reference_delta_rows_count`, and `reference_delta_claim_elements_count` are preserved in `abnormal-filing-risk-assessment.json`; `reference_delta_boundary_preserved` must pass, while reference patents remain boundary evidence only and no official action or external lawyer involvement occurs.

For abnormal-filing-risk-rejection benchmarks:

1. Use `benchmarks/abnormal-filing-risk-rejection/` as the pattern.
2. Run `scripts/validate_abnormal_filing_risk_rejection_benchmark.py`.
3. Confirm unsafe mutations for random generation, simple replacement, unsupported technical effects, missing prior-art delta, malicious batch filing language, and unconfirmed inventor contribution are rejected.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm rejection tests do not touch an official system, submit, or involve an external lawyer.

For draft-to-filing-package-validation benchmarks:

1. Use `benchmarks/draft-to-filing-package-validation/` as the pattern.
2. Confirm source draft, authorization packet, claims, specification, abstract, drawings, and request metadata files exist and their manifest/packet hashes are exact lowercase `sha256:<64 hex>` values.
3. Run `scripts/validate_submission_packet.py`.
4. Run `scripts/validate_filing_package_manifest.py`.
5. Run `scripts/validate_draft_to_package_benchmark.py`.
6. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
7. Keep status at `package_valid_official_preflight_pending` until official-channel preflight, receipt capture, and human-only step checks pass.

For official-channel-preflight-to-ready benchmarks:

1. Use `benchmarks/official-channel-preflight-to-ready/` as the pattern.
2. Run `scripts/validate_official_channel_preflight.py`.
3. Run `scripts/validate_receipt_capture.py --allow-plan-only` for the receipt plan.
4. Run `scripts/validate_filing_status_transition.py`.
5. Run `scripts/validate_official_ready_benchmark.py`.
6. Keep status at `ready_for_authorized_filing`; do not mark submitted or receipted.

For validated-package-to-official-ready benchmarks:

1. Use `benchmarks/validated-package-to-official-ready/` as the pattern.
2. Supply `official-preflight-source.json`; do not infer account, signature, automation, fee, or receipt-capture authority from the package alone.
3. Run `scripts/prepare_ready_for_authorized_filing.py`.
4. Run `scripts/validate_official_channel_preflight.py`.
5. Run `scripts/validate_receipt_capture.py --allow-plan-only`.
6. Run `scripts/validate_filing_status_transition.py`.
7. Run `scripts/validate_ready_for_authorized_filing_benchmark.py`.
8. Confirm no upload, signature, fee payment, official submission, receipt, acceptance, or application number is claimed.

For ai-self-filing-official-ready benchmarks:

1. Use `benchmarks/ai-self-filing-official-ready/` as the pattern.
2. Use `benchmarks/ai-self-filing-package-validation/` as the validated package input and `benchmarks/ai-self-filing-application-materials/` as the source-bound materials input.
3. Supply `official-preflight-source.json` with `application_materials.path` and `application_materials.hash`; do not infer account, signature, automation, fee, receipt-capture authority, or materials generation from the AI self-filing package alone.
4. Run `scripts/prepare_ready_for_authorized_filing.py`.
5. Run `scripts/validate_official_channel_preflight.py`.
6. Run `scripts/validate_receipt_capture.py --allow-plan-only`.
7. Run `scripts/validate_ready_for_authorized_filing_benchmark.py`.
8. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, `application_materials_generation=passed`, `application_materials_hash` is bound through official preflight and status, and no upload, signature, payment, official submission, receipt, or application number is claimed.

For receipt-capture benchmarks:

1. Use `benchmarks/receipt-capture-mock/` as the pattern.
2. Run `scripts/validate_receipt_capture.py`.
3. Run `scripts/validate_filing_status_transition.py`.
4. Run `scripts/validate_receipt_capture_benchmark.py`.
5. Mark benchmark data clearly as mock unless real official evidence exists.

For submitted-pending-receipt-to-official-receipt benchmarks:

1. Use `benchmarks/submitted-pending-receipt-to-official-receipt/` as the pattern.
2. Supply `receipt-capture-source.json`; do not infer receipt from submitted-pending status alone.
3. Run `scripts/prepare_receipt_capture.py`.
4. Run `scripts/validate_receipt_capture.py`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_generated_receipt_capture_benchmark.py`.
7. Confirm benchmark receipt data is marked `benchmark_mock=true`, the official session authorization hash and session-reference hash are preserved from adapter execution through receipt/status, the generator did not touch an official system, and accepted/application-number status is not marked until application-number evidence validates separately.

For ai-self-filing-submitted-pending-receipt-to-official-receipt benchmarks:

1. Use `benchmarks/ai-self-filing-submitted-pending-receipt-to-official-receipt/` as the pattern.
2. Supply `receipt-capture-source.json`; do not infer receipt from submitted-pending status alone.
3. Run `scripts/prepare_receipt_capture.py` with `benchmarks/ai-self-filing-adapter-to-submitted-pending-receipt/` as input.
4. Run `scripts/validate_receipt_capture.py`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_generated_receipt_capture_benchmark.py`.
7. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, benchmark receipt data is marked `benchmark_mock=true`, the official session authorization hash and session-reference hash are preserved from adapter execution through receipt/status, the generator did not touch an official system, and accepted/application-number status is not marked until application-number evidence validates separately.

For ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta/` as the pattern.
2. Supply `receipt-capture-source.json`; do not infer receipt from submitted-pending status alone.
3. Run `scripts/prepare_receipt_capture.py` with `benchmarks/ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta/` as input.
4. Run `scripts/validate_receipt_capture.py`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_generated_receipt_capture_benchmark.py`.
7. Confirm receipt source, receipt YAML, filing status, and report preserve the same `application_materials_hash`, `reference_patent_delta_hash`, positive delta row/claim-element counts, and `reference_delta_boundary_preserved=true`.
8. Confirm reference patents remain boundary evidence only, `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, benchmark receipt data is marked `benchmark_mock=true`, the generator did not touch an official system, and accepted/application-number status is not marked until application-number evidence validates separately.

For application-number-acceptance-mock benchmarks:

1. Use `benchmarks/application-number-acceptance-mock/` as the pattern.
2. Run `scripts/validate_application_number_evidence.py`.
3. Run `scripts/validate_filing_status_transition.py`.
4. Run `scripts/validate_application_number_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
6. Confirm benchmark data is marked mock, preserves official session authorization and session-reference hashes, and does not claim a real official application number.

For official-receipt-to-application-number benchmarks:

1. Use `benchmarks/official-receipt-to-application-number/` as the pattern.
2. Supply `application-number-source.json`; do not infer an application number from receipt status alone.
3. Run `scripts/prepare_application_number_acceptance.py`.
4. Run `scripts/validate_application_number_evidence.py`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_generated_application_number_benchmark.py`.
7. Confirm benchmark data is marked `benchmark_mock=true`, the official session authorization hash and session-reference hash are preserved from receipt evidence through application-number evidence/status, the generator did not touch an official system, and the portfolio/docket update is present.

For ai-self-filing-official-receipt-to-application-number benchmarks:

1. Use `benchmarks/ai-self-filing-official-receipt-to-application-number/` as the pattern.
2. Supply `application-number-source.json`; do not infer an application number from receipt status alone.
3. Run `scripts/prepare_application_number_acceptance.py` with `benchmarks/ai-self-filing-submitted-pending-receipt-to-official-receipt/` as input.
4. Run `scripts/validate_application_number_evidence.py`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_generated_application_number_benchmark.py`.
7. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, benchmark data is marked `benchmark_mock=true`, the official session authorization hash and session-reference hash are preserved from receipt evidence through application-number evidence/status, the generator did not touch an official system, and portfolio/docket update is present.

For ai-self-filing-official-receipt-to-application-number-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-official-receipt-to-application-number-reference-delta/` as the pattern.
2. Supply `application-number-source.json`; do not infer an application number from receipt status alone.
3. Run `scripts/prepare_application_number_acceptance.py` with `benchmarks/ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta/` as input.
4. Run `scripts/validate_application_number_evidence.py`.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_generated_application_number_benchmark.py`.
7. Confirm application-number source, evidence, filing status, and report preserve the same `application_materials_hash`, `reference_patent_delta_hash`, positive delta row/claim-element counts, and `reference_delta_boundary_preserved=true`.
8. Confirm reference patents remain boundary evidence only, `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, benchmark data is marked `benchmark_mock=true`, the generator did not touch an official system, and portfolio/docket update is present.

For case-lifecycle-trace-mock benchmarks:

1. Use `benchmarks/case-lifecycle-trace-mock/` as the pattern.
2. Run `scripts/validate_case_lifecycle_trace.py`.
3. Run `scripts/validate_case_lifecycle_benchmark.py`.
4. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
5. Confirm legal, package, stage artifact hash, official-session hash, submission, receipt, and application-number ordering invariants are true.

For case-lifecycle-rejection-gate benchmarks:

1. Use `benchmarks/case-lifecycle-rejection-gate/` as the pattern.
2. Run `scripts/validate_case_lifecycle_rejection_benchmark.py`.
3. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
4. Confirm session-reference mismatch, stage artifact hash mismatch, receipt-before-submission, and submitted-package-hash mismatch all fail for the expected reason.

For generated-case-lifecycle-trace benchmarks:

1. Use `benchmarks/generated-case-lifecycle-trace/` as the pattern.
2. Run `scripts/prepare_case_lifecycle_trace.py`.
3. Run `scripts/validate_case_lifecycle_trace.py`.
4. Run `scripts/validate_case_lifecycle_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py`.
6. Confirm the trace is `benchmark_mock`, every stage is marked mock, every stage `artifact_hash` matches the referenced artifact file, legal gate is not skipped, official session authorization/reference hashes stay consistent across approved-adapter through application-number stages, receipt appears only after submission, and application number appears only after receipt.

For ai-self-filing-lifecycle-trace benchmarks:

1. Use `benchmarks/ai-self-filing-lifecycle-trace/` as the pattern.
2. Run `scripts/prepare_case_lifecycle_trace.py --route ai_self_filing_no_external_lawyer`.
3. Run `scripts/validate_case_lifecycle_trace.py`.
4. Run `scripts/validate_case_lifecycle_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py`.
6. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, package hash consistency, stage artifact hash accuracy, official session authorization/reference hash consistency, no receipt before submission, no application number before receipt, and explicit mock labeling when the trace includes mock adapter execution, mock receipt, or mock application-number evidence.
7. Confirm post-adapter mock evidence separates evidence claims from generator actions: `generator_official_system_touched=false`, `generator_official_submission_performed=false`, and `benchmark_mock=true` wherever simulated official evidence is used.

For ai-self-filing-lifecycle-trace-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-lifecycle-trace-reference-delta/` as the pattern.
2. Run `scripts/prepare_case_lifecycle_trace.py --route ai_self_filing_no_external_lawyer --reference-delta`.
3. Run `scripts/validate_case_lifecycle_trace.py`.
4. Run `scripts/validate_case_lifecycle_benchmark.py`.
5. Run `scripts/validate_artifact_hash_manifest.py`.
6. Confirm `reference_patent_delta_hash`, positive reference-delta row and claim-element counts, and `reference_delta_boundary_preserved=true` survive from AI self-filing legal authorization through official-ready, approved-adapter, adapter execution, receipt capture, and application-number evidence.
7. Confirm official-preflight and later stages preserve the same `application_materials_hash`, while reference patents remain boundary evidence only and all simulated post-adapter evidence remains mock-labeled.

For production-official-evidence-gate benchmarks:

1. Use `benchmarks/production-official-evidence-gate/` as the pattern.
2. Run `scripts/validate_production_official_evidence_gate.py` on `production-shape/production-official-evidence-packet.json` with `--allow-production-shape-test` and confirm it passes only as a shape test.
3. Run the same packet without `--allow-production-shape-test` and confirm the strict production gate rejects it.
4. Run the strict gate on `mock-rejection/production-official-evidence-packet.json` and confirm mock evidence is rejected.
5. Run `scripts/validate_production_official_evidence_gate_benchmark.py`.
6. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, adapter execution, receipt capture, and application-number evidence are all bound to the same official session authorization/session-reference hashes, reference-delta metadata stays consistent when present, no credentials or bypass fields are present, and no benchmark/mock/shape-test evidence can be treated as real official evidence.

For production-adapter-readiness-gate benchmarks:

1. Use `benchmarks/production-adapter-readiness-gate/` as the pattern.
2. Run `scripts/validate_production_adapter_readiness.py` on `production-shape/production-adapter-readiness-packet.json` with `--allow-production-shape-test` and confirm it passes only as a shape test.
3. Run the same packet without `--allow-production-shape-test` and confirm strict adapter readiness rejects it.
4. Run the strict gate on every `production-ready/*.json` packet and confirm only `evidence_mode=production_adapter_readiness` can pass.
5. Run the strict gate on `unsafe-rejection/production-adapter-readiness-packet.json` and confirm credential or official-control bypass evidence is rejected.
6. Run `scripts/validate_production_adapter_readiness_benchmark.py`.
7. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, no credential material or bypass field can pass, and no benchmark/mock/shape-test adapter evidence can authorize real execution.

For official-session-authorization-gate benchmarks:

1. Use `benchmarks/official-session-authorization-gate/` as the pattern.
2. Run `scripts/validate_official_session_authorization.py` on `production-shape/official-session-authorization-packet.json` with `--allow-production-shape-test` and confirm it passes only as a shape test.
3. Run the same packet without `--allow-production-shape-test` and confirm strict session authorization rejects it.
4. Run the strict gate on every `production-ready/*.json` packet and confirm only `evidence_mode=official_session_authorization` can pass.
5. Run the strict gate on `unsafe-rejection/official-session-authorization-packet.json` and confirm credential material or official-control bypass evidence is rejected.
6. Run `scripts/validate_official_session_authorization_benchmark.py`.
7. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, no credential material or bypass field can pass, and no benchmark/mock/shape-test session evidence can authorize official-session use.

For case-processor-dry-run benchmarks:

1. Use `benchmarks/case-processor-dry-run/` as the pattern.
2. Run `scripts/validate_case_record.py`.
3. Run `scripts/validate_filing_adapter_contract.py request`.
4. Run `scripts/validate_filing_adapter_contract.py response`.
5. Run `scripts/validate_case_processor_benchmark.py`.
6. Confirm dry-run or handoff does not advance to `submitted_pending_receipt`.

For approved-adapter-preflight-ready benchmarks:

1. Use `benchmarks/approved-adapter-preflight-ready/` as the pattern.
2. Run `scripts/validate_approved_adapter_preflight.py`.
3. Run `scripts/validate_filing_adapter_contract.py request`.
4. Run `scripts/validate_filing_status_transition.py`.
5. Run `scripts/validate_approved_adapter_benchmark.py`.
6. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
7. Confirm the adapter request recomputes and binds the approved-adapter preflight hash, production adapter readiness packet hash, strict official session authorization hash, and session-reference hash through approved preflight, adapter request, and filing status.
8. Confirm all approved-adapter preflight and filing-adapter request hashes use exact lowercase `sha256:<64 hex>` values and local referenced files match their hashes.
9. Confirm the benchmark does not touch an official system, submit, sign, pay, capture a receipt, or create an application number.

For official-ready-to-approved-adapter-preflight benchmarks:

1. Use `benchmarks/official-ready-to-approved-adapter-preflight/` as the pattern.
2. Supply `approved-adapter-source.json`; do not infer adapter registry approval, production adapter readiness, security review, dry-run result, two-person approval, or credential handling from ready status alone.
3. Run `scripts/prepare_approved_adapter_preflight.py`.
4. Run `scripts/validate_approved_adapter_preflight.py`.
5. Run `scripts/validate_filing_adapter_contract.py request`.
6. Run `scripts/validate_filing_status_transition.py`.
7. Run `scripts/validate_generated_approved_adapter_preflight_benchmark.py`.
8. Confirm the adapter request recomputes and binds the approved-adapter preflight hash, production adapter readiness packet hash, strict official session authorization hash, and session-reference hash through approved preflight, adapter request, and filing status.
9. Confirm all source, preflight, and adapter request hashes use exact lowercase `sha256:<64 hex>` values.
10. Confirm the benchmark does not touch an official system, execute the adapter, submit, sign, pay, capture a receipt, or create an application number.

For ai-self-filing-approved-adapter-preflight benchmarks:

1. Use `benchmarks/ai-self-filing-approved-adapter-preflight/` as the pattern.
2. Use `benchmarks/ai-self-filing-official-ready/` as the ready case input and `benchmarks/ai-self-filing-package-validation/` as the validated package input.
3. Supply `approved-adapter-source.json`; do not infer adapter registry approval, production adapter readiness, dry-run result, security review, two-person approval, or credential handling from ready status alone.
4. Run `scripts/prepare_approved_adapter_preflight.py`.
5. Run `scripts/validate_approved_adapter_preflight.py`.
6. Run `scripts/validate_filing_adapter_contract.py request`.
7. Run `scripts/validate_generated_approved_adapter_preflight_benchmark.py`.
8. Confirm the adapter request recomputes and binds the approved-adapter preflight hash, production adapter readiness packet hash, strict official session authorization hash, and session-reference hash through approved preflight, adapter request, and filing status.
9. Confirm all source, preflight, and adapter request hashes use exact lowercase `sha256:<64 hex>` values.
10. Confirm the benchmark does not involve an external lawyer, touch an official system, execute the adapter, submit, sign, pay, capture a receipt, or create an application number.

For adapter-execution-mock-submitted benchmarks:

1. Use `benchmarks/adapter-execution-mock-submitted/` as the pattern.
2. Run `scripts/validate_adapter_execution_result.py`.
3. Run `scripts/validate_filing_adapter_contract.py response`.
4. Run `scripts/validate_receipt_capture.py` on the pending receipt artifact.
5. Run `scripts/validate_filing_status_transition.py`.
6. Run `scripts/validate_adapter_execution_benchmark.py`.
7. Confirm mock data is marked `benchmark_mock=true` and no receipt hash or application number is present.

For approved-adapter-to-submitted-pending-receipt benchmarks:

1. Use `benchmarks/approved-adapter-to-submitted-pending-receipt/` as the pattern.
2. Supply `adapter-execution-source.json`; do not infer an official submission from approved-adapter preflight alone.
3. Run `scripts/prepare_adapter_execution_result.py`.
4. Run `scripts/validate_adapter_execution_result.py`.
5. Run `scripts/validate_filing_adapter_contract.py response`.
6. Run `scripts/validate_receipt_capture.py` on `receipt-capture-pending.yaml`.
7. Run `scripts/validate_filing_status_transition.py`.
8. Run `scripts/validate_generated_adapter_execution_result_benchmark.py`.
9. Confirm benchmark data is marked `benchmark_mock=true`; adapter execution result recomputes adapter-request, approved-preflight, receipt-plan, audit, and docket hashes; adapter response recomputes adapter-execution-result hash; the production adapter readiness hash, official session authorization hash, and official session-reference hash are preserved from approved-adapter preflight through response/status; the generator did not touch the official system; and no receipt hash or application number is present.

For ai-self-filing-adapter-to-submitted-pending-receipt benchmarks:

1. Use `benchmarks/ai-self-filing-adapter-to-submitted-pending-receipt/` as the pattern.
2. Supply `adapter-execution-source.json`; do not infer an official submission from AI self-filing approved-adapter preflight alone.
3. Run `scripts/prepare_adapter_execution_result.py` with `benchmarks/ai-self-filing-approved-adapter-preflight/` as input.
4. Run `scripts/validate_adapter_execution_result.py`.
5. Run `scripts/validate_filing_adapter_contract.py response`.
6. Run `scripts/validate_receipt_capture.py` on `receipt-capture-pending.yaml`.
7. Run `scripts/validate_filing_status_transition.py`.
8. Run `scripts/validate_generated_adapter_execution_result_benchmark.py`.
9. Confirm `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, benchmark data is marked `benchmark_mock=true`; adapter execution result recomputes adapter-request, approved-preflight, receipt-plan, audit, and docket hashes; adapter response recomputes adapter-execution-result hash; the production adapter readiness hash, official session authorization hash, and official session-reference hash are preserved from approved-adapter preflight through response/status; the generator did not touch the official system; and no receipt hash or application number is present.

For ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta benchmarks:

1. Use `benchmarks/ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta/` as the pattern.
2. Supply `adapter-execution-source.json`; do not infer an official submission from AI self-filing approved-adapter preflight alone.
3. Run `scripts/prepare_adapter_execution_result.py` with `benchmarks/ai-self-filing-approved-adapter-preflight-reference-delta/` as input.
4. Run `scripts/validate_adapter_execution_result.py`.
5. Run `scripts/validate_filing_adapter_contract.py response`.
6. Run `scripts/validate_receipt_capture.py` on `receipt-capture-pending.yaml`.
7. Run `scripts/validate_filing_status_transition.py`.
8. Run `scripts/validate_generated_adapter_execution_result_benchmark.py`.
9. Confirm the adapter execution result, filing-adapter response, filing status, audit input hashes, and report preserve the same `application_materials_hash`, `reference_patent_delta_hash`, positive delta row/claim-element counts, and `reference_delta_boundary_preserved=true`.
10. Confirm reference patents remain boundary evidence only, `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, benchmark data is marked `benchmark_mock=true`, the generator did not touch the official system or execute the adapter, and no receipt hash or application number is present.

For case-queue-batch-processor benchmarks:

1. Use `benchmarks/case-queue-batch-processor/` as the pattern.
2. Run `scripts/run_case_queue.py` to produce or compare a local runner output when the benchmark includes `runner-result.json`.
3. Run `scripts/validate_case_queue.py`.
4. Run `scripts/validate_batch_processor_result.py`.
5. Run `scripts/validate_case_queue_benchmark.py`.
6. Run `scripts/validate_artifact_hash_manifest.py` if `artifact-hashes.json` is present.
7. Confirm dry-run or handoff does not touch official systems, submit, sign, pay, or advance any case to a receipt-driven status.
8. Confirm draft-only queue next actions default to AI self-filing legal/compliance authorization, not attorney, lawyer, counsel, patent-agent, or patent agent review.
9. Confirm queue and result rows preserve `legal_gate_mode` and keep `external_lawyer_involved=false` on the AI self-filing path.

For approved-adapter-evidence-queue benchmarks:

1. Use `benchmarks/approved-adapter-evidence-queue/` as the pattern.
2. Set `execution_mode=approved_adapter` and `approved_adapter_evidence_mode=true`.
3. Point the queue item at an independently supplied adapter execution evidence folder, such as `benchmarks/approved-adapter-to-submitted-pending-receipt/`.
4. Run `scripts/run_case_queue.py`, `scripts/validate_case_queue.py`, `scripts/validate_batch_processor_result.py`, and `scripts/validate_approved_adapter_evidence_queue_benchmark.py`.
5. Confirm the queue item and result stay at `submitted_pending_receipt`, run `validate_generated_adapter_execution_result_benchmark`, preserve `legal_gate_mode=ai_self_filing_no_external_lawyer`, keep `external_lawyer_involved=false`, keep runner and generator official-action flags false, and do not claim receipt, acceptance, or application number.

For case-queue-builder-dry-run benchmarks:

1. Use `benchmarks/case-queue-builder-dry-run/` as the pattern.
2. Run `scripts/build_case_queue.py` from case folders to produce `generated-case-queue.json`.
3. Run `scripts/validate_case_queue.py`.
4. Run `scripts/validate_case_queue_builder_benchmark.py`.
5. Run `scripts/run_case_queue.py` on the generated queue to prove the queue can enter the local runner.
6. Confirm the builder sets `official_submission_allowed=false` and `official_system_touch_allowed=false`.
7. Confirm every generated queue item carries `legal_gate_mode` and `external_lawyer_involved=false` for the AI self-filing no-external-lawyer default path.

For workflow-orchestration-dry-run benchmarks:

1. Use `benchmarks/workflow-orchestration-dry-run/` as the pattern.
2. Run `scripts/orchestrate_case_workflow.py` to generate queue, batch result, report, and hash manifest.
3. Run `scripts/validate_case_queue.py`.
4. Run `scripts/validate_batch_processor_result.py`.
5. Run `scripts/validate_workflow_orchestration_benchmark.py`.
6. Confirm the orchestrator does not touch an official system, submit, sign, pay, capture a real receipt, or create an application number.
7. Confirm the queue, batch result, and report preserve legal-gate metadata and keep `external_lawyer_involved=false` on the AI self-filing dry-run path.

For regression-gate verification:

1. Read `references/regression-gate.md`.
2. Run `scripts/run_regression_gate.py --json`; confirm `json_parse.ok=true`, `yaml_parse.ok=true`, `structured_sha256_placeholders.ok=true`, and `structured_dangerous_true_fields.ok=true`.
3. For auditable handoff, run `scripts/run_regression_gate.py --output-dir out/regression-gate --json` and validate `out/regression-gate/artifact-hashes.json`.
4. Confirm every benchmark folder validator, artifact manifest, source compile, JSON parse, forbidden scan, and evidence-bundle manifest check passes.
5. Confirm `official_system_touched=false`, `official_submission_performed=false`, and `external_lawyer_involved=false`.

## Agent Team Mode

When the user asks to use all person skills or an agent team:

1. Read `references/advisory-board-agent-team.md`.
2. Select only seats relevant to the case.
3. Keep each seat's authority bounded.
4. Produce a team decision with legal gate result.
5. Never let advisory personas override attorney/patent-agent review, AI self-filing legal/compliance evidence, mandatory-agent checks, or applicant authorization.

## Darwin Review Mode

When using Darwin-style optimization:

- First run assessment only; do not auto-edit unless the user explicitly asks.
- Run `scripts/run_regression_gate.py --json` before treating local changes as verified, and require JSON/YAML parsing plus the positive structured benchmark `sha256:*` placeholder and dangerous `true` boolean scans to pass.
- Evaluate frontmatter, workflow clarity, failure branches, checkpoints, specificity, resource integration, end-to-end structure, test-prompt performance, and anti-pattern blacklist.
- Keep improvements only when they make the patent workflow safer, more executable, and more enterprise-grade.
