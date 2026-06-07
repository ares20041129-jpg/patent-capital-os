# Quality Rubric

Use this rubric to score Patent Capital OS outputs and to run Darwin-style review.

Score each dimension 1-10 and calculate weighted total.

| Dimension | Weight | What Good Looks Like |
|---|---:|---|
| Karpathy preflight | 8 | Assumptions, smallest action, evidence, brittle AI points, success criteria, and stop rule are explicit |
| Route clarity | 7 | Request is correctly routed and status is explicit |
| Legal gate integrity | 15 | Mandatory gates are checked, stop conditions are enforced |
| Evidence discipline | 11 | Facts, assumptions, inferences, and missing evidence are separated |
| Patent quality | 12 | Technical problem/means/effect, claims, support, and fallback ladder are concrete |
| Prior-art reasoning | 10 | Closest references are mapped to claim elements with risk levels |
| Filing operations | 11 | XML/package/fee/receipt/deadline handling is precise |
| Portfolio/capital thinking | 8 | Business value, moat, transaction readiness, and maintenance burden are addressed |
| Red-team strength | 9 | Examiner, invalidity, design-around, and proof risks are attacked |
| Auditability | 6 | Hashes, approvals, owners, timestamps, and next actions are captured |
| Safety and anti-abuse | 3 | No bypass, fabrication, or false filing-status claims |

## Pass Levels

- 90-100: enterprise-ready.
- 80-89: usable with minor review.
- 70-79: draft quality; do not file without cleanup.
- Below 70: not ready.

## Application Materials Quality Gate

Before official-channel preflight, generated application materials must pass a separate quality review:

- `scripts/prepare_application_materials_quality_review.py` writes `application-materials-quality-review.json`.
- `scripts/validate_application_materials_quality_review.py` recomputes the referenced `application-materials.json` hash and validates the underlying materials.
- Overall weighted score must be at least 85.
- Every dimension must score at least 7.
- Enterprise-ready materials score at least 90.
- Quality review does not provide legal advice, does not claim lawyer or patent-agent review, and does not perform official upload, signature, payment, submission, receipt capture, or application-number creation.

## Required Red Flags

Any one of these makes filing readiness fail regardless of score:

- Missing Karpathy preflight before material action.
- Missing legal review tied to final version.
- Missing applicant authorization.
- Unresolved inventor or ownership issue.
- Unresolved secrecy review where relevant.
- XML/package validation failure.
- Official channel cannot be used lawfully.
- Filing package hash mismatch.
- Fabricated or unsupported legal/technical fact.
