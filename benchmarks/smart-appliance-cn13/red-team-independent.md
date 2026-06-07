# Independent Red-Team Review

Case ID: BENCHMARK-SMART-APPLIANCE-CN13  
Date: 2026-06-01  
Reviewer mode: independent adversarial review  
Decision: revise / do_not_file

## Karpathy Preflight

- Assumption: this is a benchmark invention synthesized from abstract-level references, not a real invention disclosure.
- Smallest step: attack the draft claims and filing readiness without changing the report.
- Evidence: benchmark report, source captures, claim-support map, and legal-gate status.
- Brittle points: novelty, inventive step, enablement, inventorship, and official filing readiness cannot be concluded from abstracts.
- Stop rule: no filing, no fee payment, no official status claim.

## Attacks

| Issue | Severity | Attack | Evidence | Required mitigation |
| --- | --- | --- | --- | --- |
| Obvious sensor aggregation | Critical | A skilled person could combine known VOC, torque, image, height, and environment controls. | CN120827118A, CN121092920A, CN120186196A, CN118859738A | Define a non-generic confidence-consistency rule and prove improvement over single-sensor control. |
| Self-optimization anticipated | High | Recipe-specific threshold updates may be covered by household bread maker self-optimization. | CN121195989A | Tie updates to cross-modal failure labels and a specific state-transition threshold. |
| Generic AI/multi-model weakness | High | Model fusion for food quality control is already disclosed. | CN120765118B | Avoid claiming model names; claim controller constraints and sensor-disagreement handling. |
| Enablement gap | High | No real drawings, experiments, sensor timing, calibration examples, or appliance architecture. | Benchmark-only materials | Add inventor disclosure, diagrams, prototype logs, and comparative data. |
| Claim support gap | High | Claim map is benchmark-level support only. | `claim-support-map.md` | Replace benchmark support with real source material IDs and hashes. |
| Non-abnormal filing risk | Critical | User wants "similar patents"; system must reject copy/synonym/batch generation. | User objective and source set | Require invention disclosure validation and anti-abnormal screen before drafting. |
| Legal gate failure | Critical | No counsel review, applicant authorization, inventor confirmation, ownership, secrecy, XML, fee authority, or official channel. | `submission-packet-status.json` | Maintain `do_not_file`. |
| Design-around | Medium | Competitor can remove one modality or change confidence rule. | Claim architecture | Add fallback claims for modality subsets and controller variants only if supported. |

## Verdict

The benchmark is useful for skill evaluation and claim strategy. It is not a filing-ready patent application.

The next defensible move is to create a real source material manifest and invention disclosure for an actual product, then rerun the support map, prior-art matrix, and counsel review gates.
