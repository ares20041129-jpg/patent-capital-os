# Patent Workflows

Use this reference for drafting, diligence, red-team, and portfolio workflows.

## Prior-Art Diligence

Inputs:

- Invention disclosure.
- Reference patents and publication numbers.
- Product manuals, standards, papers, code or experiment summaries.
- Jurisdictions and filing type.

Process:

1. Extract proposed claim elements.
2. Identify closest prior art.
3. Map each claim element against each reference.
4. Distinguish facts, inferences, and recommendations.
5. Rate novelty risk and inventive-step risk.
6. Identify technical-effect evidence needed to support differences.
7. When the reference set is concrete, materialize `reference-patent-delta.json` with `scripts/prepare_reference_patent_delta.py` and validate it before claim drafting.

Output columns:

- Reference.
- Title/source.
- Relevant disclosure.
- Matching claim element.
- Missing claim element.
- Distinguishing technical feature.
- Technical effect evidence.
- Combination risk.
- Recommended claim adjustment.

Hard gates:

- Every claim element must have applicant-owned file-bound support.
- Every claim element must have a delta row against the cited references.
- Reference patents are boundary evidence only and must not be used as applicant claim support.
- The output must not claim novelty, inventive step, patentability, allowance, lawyer review, patent-agent review, filing authorization, receipt, or application number.

## Inventive Concept Distillation

Use this test:

```text
Because [known system limitation],
the invention uses [specific technical means],
to change [measurable technical state/control/result],
thereby producing [technical effect].
```

Reject weak formulations:

- “Use AI to optimize”.
- “Use sensors to monitor”.
- “Remote control with an app”.
- “Improve accuracy” without a specific mechanism.
- “Dynamic adjustment” without input, rule/model, and output.

## Claim Architecture

Create:

- Broad independent claim around the core technical contribution.
- Dependent fallback ladder:
  - data source variants;
  - feature extraction variants;
  - state model variants;
  - control action variants;
  - exception and safety variants;
  - hardware arrangement variants;
  - training/calibration/history variants.
- Parallel claim categories:
  - method;
  - device/system;
  - controller;
  - storage medium;
  - appliance/product.

Check:

- Each element has support.
- Each dependent claim narrows meaningfully.
- No purely result-oriented independent claim.
- No unsupported performance promise.
- No unclear antecedent basis.

## Specification Review

For each claim element, confirm:

- Description support.
- Embodiment support.
- Alternative embodiment.
- Drawing reference if structural.
- Technical effect link.
- Failure or exception handling if operational.

## Red-Team Review

Attack from four roles:

- Examiner: obviousness, clarity, support, subject matter.
- Invalidity petitioner: prior-art combinations and lack of enablement.
- Competitor: design-around path.
- Litigation counsel: claim proof and infringement detectability.

For each attack, output:

- Attack theory.
- Evidence.
- Severity: critical, high, medium, low.
- Mitigation.
- Owner.

## Portfolio Strategy

Tag each case:

- Core product coverage.
- Peripheral product coverage.
- Process/manufacturing know-how.
- Data/model/control logic.
- Defensive publication candidate.
- Divisional/PCT candidate.
- SEP/licensing candidate.
- Low-value hold/abandon.

Portfolio decisions:

- File now.
- Hold for more evidence.
- Keep as trade secret.
- Defensive publish.
- Split into family.
- Prepare PCT.
- Abandon or do not maintain.
