# Patent Application Draft

Case ID: CASE-INBOX-HANDOFF-REF-001  
Draft version: draft-package-2026-06-03T070314plus0800  
Source material manifest: invention-disclosure.json  
Disclosure hash: sha256:759186471def5502ff8b24f3def5d1b76f3d2fda7f5aea0ba2cd3bc936eb96f3  
Draft status: ai_self_filing_authorization_needed

## Title

Adaptive motor control for dough-state estimation.

## Technical Field

The draft relates to the technical field reflected in the confirmed invention disclosure, including the disclosed apparatus, method, control logic, data processing, and implementation embodiments.

## Background

Known references and products may disclose parts of the field. This draft uses them only as prior-art context and does not copy claims, wording, or effects not backed by evidence.

Closest known references:

| Reference | Relevance | Claim risk |
| --- | --- | --- |
| prior-art-notes.txt | Prior-art material received; publication identifier pending extraction. | Requires element-level review |

## Technical Problem

Existing appliances use fixed mixing schedules and do not adapt to dough state.

## Technical Solution

Required features:

1. compare motor-current ripple, bowl temperature, and timed rest intervals
2. classify dough hydration and elasticity state from the comparison
3. adjust kneading torque and rest timing when the classified state crosses a threshold

Optional features:

1. Optional fallback features require AI legal/compliance selection.

## Reference Patent Delta Strategy

Reference delta status: reference_delta_ready_for_draft_strategy
Reference patents are boundary evidence only and do not supply applicant claim support.

| Element | Known In Prior Art | Distinguishing Feature | Claim Strategy | Fallback |
| --- | --- | --- | --- | --- |
| E1 | partial | uses the three-signal comparison as a state-classification input rather than a single fixed schedule parameter | place the three-signal comparison in the independent claim as the sensing and classification basis | narrow to motor-current ripple plus bowl temperature if rest-interval evidence needs more support |
| E2 | partial | classifies hydration and elasticity state rather than only monitoring temperature, time, or appliance mode | tie the state classifier to a concrete dough-state output and avoid result-only optimization wording | dependent claim for threshold ranges or state labels supported by experiment data |
| E3 | no | changes kneading torque and rest timing in response to the classified dough state crossing a threshold | make the control action depend on threshold crossing to distinguish from generic bread-maker control | dependent claims for torque, rest timing, and exception-handling variants |

## Beneficial Technical Effects

| Effect | Evidence | Source material ID | Confidence |
| --- | --- | --- | --- |
| Improves dough-state transition judgment compared with a fixed mixing schedule. | Prototype log indicates motor-current variance changes after water absorption; source hash sha256:6baab568f9192b044032b1eb3cad2fd81e547dd6abcfd039dfd1de975921959c. | E-001 | draft |
| Provides a controller input for adjusting rest intervals based on dough hydration and elasticity state. | Drawing notes and technical idea material in source hash sha256:36938c5922b3d40d2d16a0e50d7edacb676dd227621189f3a8d261ef7c235771. | E-002 | draft |

## Brief Description Of Drawings

| Figure | Description | Required for claim support? |
| --- | --- | --- |
| Fig. 1 | drawing-notes.txt | yes |

## Detailed Embodiments

### Embodiment 1

Components:

- Components pending final drawing confirmation.

Steps:

1. Compare motor current ripple, bowl temperature, and timed rest intervals to classify dough hydration and elasticity state.

Parameters:

- Parameter ranges require inventor and AI legal/compliance confirmation before filing readiness.

Alternatives:

- Equivalent components or control sequences may be used only if supported by the confirmed disclosure.

Failure handling:

- Features lacking evidence must be removed, narrowed, or escalated to the AI legal/compliance gate before filing readiness.

## Claims Draft

### Independent Claim Candidates

1. A technical method for Adaptive motor control for dough-state estimation, comprising: compare motor-current ripple, bowl temperature, and timed rest intervals; classify dough hydration and elasticity state from the comparison; adjust kneading torque and rest timing when the classified state crosses a threshold.

### Dependent Claim Ladder

2. The method of claim 1, wherein narrow to motor-current ripple plus bowl temperature if rest-interval evidence needs more support.
3. The method of claim 1, wherein dependent claim for threshold ranges or state labels supported by experiment data.
4. The method of claim 1, wherein dependent claims for torque, rest timing, and exception-handling variants.

## Abstract

A technical solution is disclosed for Adaptive motor control for dough-state estimation. The solution includes compare motor-current ripple, bowl temperature, and timed rest intervals; classify dough hydration and elasticity state from the comparison; adjust kneading torque and rest timing when the classified state crosses a threshold. The draft is generated only from confirmed disclosure facts and remains subject to AI self-filing legal/compliance authorization.

## Claim Support Map Link

See claim-support-map.md for limitation-level support and evidence hashes.

## AI Legal/Compliance Questions

- Confirm inventor names and contributions.
- Confirm applicant and ownership basis.
- Confirm no copying or synonym substitution from reference patents.
- Confirm technical effects and supporting evidence.
- Confirm secrecy review and filing jurisdiction plan.
- Confirm whether motor-current ripple and bowl temperature should be claimed as required features or fallback dependent features.
- Confirm closest prior art before broad independent claim drafting.

## Filing Gate

Do not file this draft. The legal gate for filing has not passed because final AI self-filing legal/compliance authorization, applicant filing authorization, final package hash, fee authority, and official-channel preflight are not validated.
