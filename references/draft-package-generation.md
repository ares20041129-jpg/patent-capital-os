# Draft Package Generation

Use this reference when a confirmed invention disclosure should become draft-only AI self-filing legal/compliance authorization artifacts.

## Purpose

Draft package generation creates a patent application draft and claim support map from `invention-disclosure.json`. It does not create a filing package and does not authorize official submission.

## Command

```bash
python -X utf8 scripts/generate_draft_package.py invention-disclosure.json --output-dir draft-package-generation --json
```

When a validated cited-patent delta is available:

```bash
python -X utf8 scripts/generate_draft_package.py invention-disclosure.json --reference-delta reference-patent-delta.json --output-dir draft-package-reference-delta --json
```

## Outputs

- `patent-application-draft.md`
- `claim-support-map.md`
- optional `reference-patent-delta.json` when a validated cited-patent delta is supplied
- optional `draft-evidence-provenance.json` and `draft-evidence-provenance-report.md` when a source material manifest is available
- optional `abnormal-filing-risk-assessment.json` and `abnormal-filing-risk-report.md` after draft evidence provenance
- `filing-status.json`
- `draft-package-report.md`
- `artifact-hashes.json`

## Required Invariants

- `invention-disclosure.json` passes `scripts/validate_invention_disclosure.py`.
- `patent-application-draft.md` passes `scripts/validate_patent_application_draft.py`.
- `claim-support-map.md` passes `scripts/validate_claim_support_map.py --allow-draft`; claim evidence hashes must be exact lowercase `sha256:<64 hex>` values.
- If `--reference-delta` is supplied, `reference-patent-delta.json` must validate, its `case_id` must match the disclosure, and the draft plus claim support map must use its claim elements, distinguishing features, technical-effect evidence, claim strategy, and fallback positions.
- When source materials are available, `draft-evidence-provenance.json` passes `scripts/validate_draft_evidence_provenance.py`, copies file-bound source materials into the provenance output, and proves every claim support row uses applicant/inventor/R&D source evidence rather than reference-patent or prior-art material.
- If a draft package includes `reference-patent-delta.json`, draft evidence provenance must copy, validate, and hash-bind it as boundary evidence while still prohibiting it as applicant claim support.
- A supplied reference-patent delta may guide prior-art boundaries and fallback positions, but it must not supply applicant claim support or a novelty/patentability guarantee.
- Draft provenance `source_package_hash`, `draft_hash`, `claim_support_map_hash`, own-support hashes, prohibited-reference hashes, and row evidence hashes must be exact lowercase `sha256:<64 hex>` values.
- When source-backed provenance is available, `abnormal-filing-risk-assessment.json` passes `scripts/validate_abnormal_filing_risk_assessment.py`, preserves copied source files for audit, and keeps `risk_level=low`, `filing_allowed=false`, and `external_lawyer_involved=false`.
- When provenance includes a reference-patent delta hash, abnormal-filing risk assessment must preserve that hash and pass `reference_delta_boundary_preserved` to prove the case is not a copied, synonym-substituted, or patchwork filing from cited patents.
- `filing-status.json` remains `status=draft_only`.
- `legal_gate=failed`.
- `legal_gate_mode=ai_self_filing_no_external_lawyer`.
- `decision=do_not_file`.
- `draft_generation_allowed=true`.
- `filing_allowed=false`.
- `external_lawyer_involved=false`.
- `official_system_touched=false`.
- `official_submission_performed=false`.
- Generated patent draft, claim support map, and draft package report must not default to attorney, lawyer, counsel, patent-agent, or patent agent review.
- No receipt hash or application number may appear.

## Validator

Run:

```bash
python -X utf8 scripts/validate_draft_package_generation_benchmark.py benchmarks/draft-package-generation --json
```

For source-backed draft provenance:

```bash
python -X utf8 scripts/prepare_draft_evidence_provenance.py draft-package-dir source-material-manifest.yaml --output-dir draft-evidence-provenance-gate --json
python -X utf8 scripts/validate_draft_evidence_provenance_benchmark.py draft-evidence-provenance-gate --json
python -X utf8 scripts/prepare_abnormal_filing_risk_assessment.py draft-evidence-provenance-gate --output-dir abnormal-filing-risk-gate --json
python -X utf8 scripts/validate_abnormal_filing_risk_benchmark.py abnormal-filing-risk-gate --json
python -X utf8 scripts/validate_abnormal_filing_risk_rejection_benchmark.py abnormal-filing-risk-rejection --json
```

Passing this validator means the draft package is ready for AI self-filing legal/compliance authorization. It does not mean the draft is filing-ready, submitted, receipted, or accepted.
