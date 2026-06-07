# Patent Application Materials Generation

Use this reference after a filing package has passed validation and before any official-channel preflight, upload, signature, payment, or submission.

## Purpose

The application materials stage converts a validated package into a source-bound, machine-auditable materials bundle. It generates the materials needed for a filing operator or lawful adapter to inspect the case without pretending that any official action has occurred.

This stage is especially important in AI self-filing mode because the system must prove that generated claims, specification, abstract, drawings plan, request-form metadata, and XML readiness are tied to applicant evidence, not copied from reference patents or prior art.

## Required Inputs

- A validated filing package folder with `filing-package-manifest.yaml`, `filing-status.json`, and either an AI self-filing authorization packet or a counsel-reviewed submission packet.
- For AI self-filing: `ai-self-filing-authorization-packet.json` with `legal_gate_mode=ai_self_filing_no_external_lawyer`.
- For AI self-filing: same-case `draft-evidence-provenance.json` proving claim-support rows, own support hashes, and no reference/prior-art support.
- For AI self-filing: same-case `abnormal-filing-risk-assessment.json` with `risk_level=low`.
- If provenance or abnormal-filing assessment contains `reference_patent_delta_hash`, both local copied summaries in `application-materials.json` must preserve the same reference-delta hash, row count, claim-element count, and the abnormal-risk summary must keep `reference_delta_boundary_preserved=true`.
- The source patent draft whose hash matches the validated package and provenance artifact.
- No official-session credentials, cookies, payment secrets, captchas, MFA secrets, or official-system control bypass material.

## Generated Outputs

`scripts/prepare_patent_application_materials.py` creates:

- `application-materials.json`
- `request-form-metadata.json`
- `document-generation-plan.json`
- `claims-material.md`
- `specification-material.md`
- `abstract-material.md`
- `drawings-materials-plan.md`
- `xml-readiness-checklist.json`
- `draft-evidence-provenance.json`
- `abnormal-filing-risk-assessment.json`
- `filing-status.json`
- `application-materials-report.md`
- `artifact-hashes.json`

After materials generation, `scripts/prepare_application_materials_quality_review.py` creates:

- `application-materials-quality-review.json`
- `application-materials-quality-report.md`
- `artifact-hashes.json`

For one-command local execution, `scripts/orchestrate_application_materials_pipeline.py` creates:

- `application-materials/`
- `application-materials-quality-gate/`
- `application-materials-pipeline-result.json`
- `application-materials-pipeline-report.md`
- `artifact-hashes.json`

This pipeline only joins materials generation and independent quality review. It does not perform official-channel preflight, upload, signature, payment, submission, receipt capture, or application-number capture.

The generated bundle must validate with:

```bash
python -X utf8 scripts/validate_patent_application_materials.py application-materials.json --json
```

Benchmark folders validate with:

```bash
python -X utf8 scripts/validate_patent_application_materials_benchmark.py benchmarks/ai-self-filing-application-materials --json
python -X utf8 scripts/validate_patent_application_materials_benchmark.py benchmarks/ai-self-filing-application-materials-reference-delta --json
python -X utf8 scripts/validate_application_materials_quality_benchmark.py benchmarks/application-materials-quality-gate --json
python -X utf8 scripts/validate_application_materials_pipeline_benchmark.py benchmarks/application-materials-pipeline --json
python -X utf8 scripts/validate_application_materials_pipeline_benchmark.py benchmarks/application-materials-pipeline-reference-delta --json
```

## Material Inventory

The bundle must include both generated material files and official material inventory references:

- Claims material
- Specification material
- Abstract material
- Drawings material plan
- Request-form metadata
- XML readiness checklist

For a CN invention filing path, the request metadata, claims, specification, abstract, and drawings/package readiness must be present before official preflight. Exact official forms, XML schema behavior, and filing-channel constraints must still be checked against the current official channel before any upload or submission.

## Legal And Safety Gates

The materials stage preserves the legal step but does not create lawyer review. In AI self-filing mode:

- `external_lawyer_involved=false`
- `legal_gate_mode=ai_self_filing_no_external_lawyer`
- `no_legal_advice_claimed=true`
- `no_lawyer_or_agent_review_claimed=true`
- `official_system_touched=false`
- `official_submission_performed=false`
- `filing_allowed=false` until official-channel preflight passes

The bundle must bind:

- AI self-filing authorization packet hash
- Filing package manifest hash
- Filing status hash
- Source draft hash
- Final package hash
- Draft evidence provenance artifact hash
- Abnormal filing risk assessment artifact hash
- Optional reference-patent delta hash and counts across both evidence provenance and abnormal filing risk summaries when the draft used reference patents

All application-materials hash fields must use exact lowercase `sha256:<64 hex>` values. Generated material file hashes, request metadata hash, document generation plan hash, XML readiness hash, filing-status hash, draft evidence provenance hash, abnormal-risk artifact hash, own-support hashes, prohibited-reference hashes, official inventory hashes, and XML validation/report hashes must reject descriptive placeholders such as `sha256:source-draft`.

Generated material paths inside `application-materials.json` must be relative paths that resolve inside the materials output directory. Do not allow absolute paths, `..` traversal, or generated-material references outside the materials bundle. The source package directory may point to the upstream validated package, but copied provenance, copied abnormal-risk evidence, request metadata, generated documents, XML readiness, and filing status must remain hash-bound local files inside the materials bundle.

Generated claims, specification, abstract, and drawing-plan files must contain the expected source-draft section markers. Do not pass materials that contain "section not found in source draft" placeholders even when the file path and hash are otherwise valid.

Quality review must be separate from generation. Before official-channel preflight, run `scripts/prepare_application_materials_quality_review.py` or the combined local `scripts/orchestrate_application_materials_pipeline.py` and validate `application-materials-quality-review.json` with `scripts/validate_application_materials_quality_review.py`. The quality gate must score at least 85 overall, every dimension must score at least 7, every dimension must contain the exact expected check IDs, each dimension score must recompute from those checks, the application-materials hash must recompute, and official-system/submission/external-lawyer flags must remain false.

## Stop Conditions

Stop and generate a deficiency instead of materials when:

- The validated package benchmark fails.
- The source draft hash does not match the package or provenance artifact.
- The provenance artifact has unsupported claim rows or uses reference/prior-art material as claim support.
- The abnormal filing risk assessment is missing, mismatched, not same-case, or not low risk.
- Reference-patent delta metadata is present in provenance or abnormal-filing risk evidence but the materials summary drops it, mismatches the hash or counts, or loses `reference_delta_boundary_preserved=true`.
- Any application-materials hash field is missing, malformed, not exact lowercase `sha256:<64 hex>`, or mismatched against a referenced local generated file.
- Any generated material path is absolute, contains `..`, resolves outside the materials output directory, or points to a missing/non-matching local artifact.
- Any generated claims, specification, abstract, or drawing-plan file is a missing-section placeholder or lacks its required source-draft section marker.
- The independent application-materials quality review is missing, hash-mismatched, below threshold, has a failed dimension, omits or changes expected dimension check IDs, contains forged dimension scores, or claims any official action.
- Applicant, inventor, ownership, secrecy, fee, or request-form metadata is missing from the authorization packet.
- The requested output would claim official submission, receipt, fee payment, signature, or application number without independent official evidence.

## Next Gate

Successful materials generation keeps status at `package_valid_official_preflight_pending` and sets `decision=materials_generated_official_preflight_required`.

The next gate is official-channel preflight. Do not upload, sign, pay, submit, claim receipt, or claim an application number from the materials bundle alone.
