# Abnormal Filing Risk Assessment

Case ID: CASE-PRE-SUB-HANDOFF-REF-001
Gate: G8 Non-abnormal filing check
Status: abnormal_filing_risk_assessed
Decision: draft_only_do_not_file_until_ai_self_filing_gate
Risk level: low
Filing boundary: draft-only; do not file until the AI self-filing legal/compliance gate and official-channel gates pass.
Official system touched: no
Official submission performed: no

## CNIPA Order 77 Risk Baseline

This gate screens for random computer generation, fabricated technical effects, copied or simply replaced prior art, obvious patchwork, unreasonable degradation, non-necessary narrowing, maliciously distributed batch filings, false inventor/applicant changes, and other bad-faith indicators.

## Reference Delta Boundary

When reference-patent delta evidence is present, this gate treats it as a hash-bound boundary and claim-strategy artifact only. It must not become applicant claim support or a novelty/patentability guarantee.

## Checks

| Check | Result | Evidence | Required cure |
| --- | --- | --- | --- |
| real_inventive_activity | pass | Inventor contribution is confirmed and R&D evidence includes prototype, experiment, log, or source hashes. | Collect inventor contribution confirmation and real R&D evidence before draft generation or filing. |
| no_random_generation | pass | No random-generation, simple-replacement, or synonym-substitution marker was found in core disclosure fields. | Replace generated or wording-only material with real technical contribution evidence and inventor confirmation. |
| no_reference_copy_or_simple_replacement | pass | Similarity control is confirmed and provenance rows do not use prior-art/reference hashes as applicant claim support. | Remove copied material, rewrite claims from applicant evidence, and rerun provenance validation. |
| reference_delta_boundary_preserved | pass | Reference-patent delta is hash-bound as boundary evidence and claim support rows remain applicant-evidence based. | Keep reference patents as boundary evidence only and rerun provenance if any row uses reference material as support. |
| technical_effects_supported | pass | All technical effects cite evidence hashes traceable to applicant disclosure or R&D material. | Tie each technical effect to applicant evidence and remove unsupported performance claims. |
| not_obvious_patchwork | pass | The draft has multiple required features, known prior-art references, and element-level prior-art delta rows. | Build a feature-by-feature prior-art delta and remove unsupported combinations. |
| not_unreasonable_degradation_or_nonessential_narrowing | pass | No unreasonable-degradation or non-essential-narrowing marker was found. | Explain the technical purpose of narrowed features or remove artificial degradation language. |
| no_malicious_batch_or_duplicate_pattern | pass | No maliciously distributed batch filing or duplicate filing marker was found in the case text. | Provide legitimate portfolio purpose and distinct invention evidence for each case. |
| inventor_applicant_consistency | pass | Applicant, inventors, and contribution confirmation are present. | Confirm applicant identity, inventor list/order, and real contribution before any filing package. |

## Filing Boundary

This is a draft-only abnormal-filing risk gate. It is not legal advice, not lawyer review, not patent-agent review, not filing package validation, not official-channel preflight, not an official submission, not a receipt, and not an application number.
