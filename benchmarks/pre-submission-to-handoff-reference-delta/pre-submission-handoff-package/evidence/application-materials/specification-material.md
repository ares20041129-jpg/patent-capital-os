# Specification Material

Case ID: CASE-PRE-SUB-HANDOFF-REF-001
Source draft hash: sha256:80f2539c69aa427fdc0a2c504c8488807f30fe63cd562964a966ee9cc2213877
Final package hash: sha256:119c2b0199b06a7c66a0bb5ca18303c482ca1465a8552057d959e1000d59af6f
Route: AI self-filing, no external lawyer or patent agent in default path
Boundary: generated material only; not legal advice, not official submission, not receipt evidence.

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
