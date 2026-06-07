# Patent Generation Engine

Use this reference when converting incoming materials or reference patents into a new patent draft.

## Mission

Generate patent application artifacts from real invention evidence. Do not generate patent filings from similarity alone.

## Required Inputs

- Invention disclosure form.
- Applicant and inventor context.
- Technical problem.
- Technical solution.
- Technical effects supported by evidence.
- At least one enabled embodiment.
- Drawings or block diagrams when applicable.
- Known prior art and closest references.
- Commercial/product context.
- Constraints: jurisdictions, deadlines, secrecy, publication risk, and budget.

## Generation Pipeline

1. Intake normalization
   - Convert messy materials into `assets/templates/invention-disclosure-form.yaml`.
   - Mark missing facts as missing, not assumed.

2. Anti-abnormal screen
   - Confirm the invention is based on real technical activity.
   - Reject copied, randomly generated, simple replacement, patchwork, or fabricated-effect cases.
   - After source-backed draft provenance is available, run `scripts/prepare_abnormal_filing_risk_assessment.py` and require `risk_level=low` before any AI self-filing authorization path can continue.

3. Prior-art delta
   - Build an element-level map against closest references.
   - Identify what is new, what is old, and what is unsupported.
   - For a concrete cited-patent set, run `scripts/prepare_reference_patent_delta.py` and validate `reference-patent-delta.json` before treating reference analysis as claim-strategy input.
   - Every proposed claim element must have applicant-owned file-bound support and a delta row; cited patents are boundary evidence only.

4. Inventive concept
   - Extract problem, means, effect, necessary features, optional features, alternatives, and implementation evidence.

5. Claim skeleton
   - Draft independent claim candidates only from supported features.
   - Add dependent fallback ladder tied to prior-art deltas.
   - When `reference-patent-delta.json` is available, pass it to `scripts/generate_draft_package.py --reference-delta` so the draft and claim support map consume the validated delta rows instead of generic prior-art placeholders.
   - Generate parallel method, apparatus, system, and medium categories only when supported.

6. Specification scaffold
   - Draft title, field, background, summary, drawing description, embodiments, alternatives, and effects.
   - Preserve unsupported areas as AI legal/compliance questions for draft-only review.
   - Do not promote missing source-draft sections into filing materials as placeholder text.

7. Claim support map
   - Use `assets/templates/claim-support-map.md`.
   - Every limitation needs disclosure support and evidence hash.
   - Run `scripts/prepare_draft_evidence_provenance.py` when source materials are available.
   - Run `scripts/prepare_abnormal_filing_risk_assessment.py` after provenance to document the G8 non-abnormal filing screen.
   - Treat applicant, inventor, R&D, prototype, experiment, and drawing evidence as possible claim support.
   - Treat reference patents and prior-art captures as boundary evidence only; they must not be used as the applicant's own claim support.

8. Red team
   - Attack novelty, inventive step, enablement, clarity, unity, ownership, non-abnormal filing risk, and design-around.

9. AI self-filing authorization-ready package
   - Package draft artifacts for AI legal/compliance authorization on the no-external-lawyer route.
   - Do not default to attorney, lawyer, counsel, patent-agent, or patent agent review wording.
   - No filing status may advance until AI self-filing legal/compliance authorization, applicant authorization, and official-channel gates pass.

## Similar Patent Use

Reference patents may be used to learn:

- Field vocabulary.
- Problem framing.
- Claim category patterns.
- Prior-art boundaries.
- Examiner risk themes.
- Technical feature taxonomy.
- Negative space: what the applicant must distinguish from.

Reference patents must not be used to:

- Copy claims.
- Substitute synonyms.
- Generate randomized variants.
- Hide the true prior-art source.
- Create filings without a real technical contribution.
- Supply evidence hashes for the applicant's claim limitations.
- Claim novelty, inventive step, patentability, allowance, lawyer review, patent-agent review, or filing authorization.

## Output Set

Minimum draft package:

- IP investment memo.
- Invention disclosure normalization.
- Prior-art matrix.
- Inventive concept memo.
- Claim architecture.
- Claim support map.
- Specification scaffold.
- Drawing request list.
- Red-team report.
- Legal gate status.
- Filing readiness status.

## Stop Conditions

Stop in draft-only mode when:

- Invention disclosure is incomplete.
- Technical effect is unsupported.
- The only difference from prior art is a wording change.
- AI generated the invention without real human technical contribution.
- Inventor, applicant, ownership, secrecy, AI self-filing legal/compliance authorization, or applicant authorization is missing.
