# Claim Support Map

Case ID: CASE-INTAKE-ORCH-001  
Version: draft-package-2026-06-03T042033plus0800  
Source package hash: sha256:50b929eeee1b5ce160d5a580414580c78966e35ce1540db6f4309e2e8df23005  
Reviewer: Patent Capital OS draft generator  
Review timestamp: 2026-06-03T04:20:33+08:00  
Gate status: draft

## Claim Map

| Claim | Limitation | Required? | Disclosure support | Figure / embodiment | Prior-art delta | Technical effect | Fallback position | Evidence hash | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | compare motor-current ripple, bowl temperature, and timed rest intervals | yes | Confirmed invention disclosure required feature 1. | Fig. 1 / Embodiment 1 | uses the three-signal comparison as a state-classification input rather than a single fixed schedule parameter | prototype evidence links the comparison to hydration and elasticity classification | narrow to motor-current ripple plus bowl temperature if rest-interval evidence needs more support | sha256:6baab568f9192b044032b1eb3cad2fd81e547dd6abcfd039dfd1de975921959c | draft_supported |
| 1 | classify dough hydration and elasticity state from the comparison | yes | Confirmed invention disclosure required feature 2. | Fig. 2 / Embodiment 1 | classifies hydration and elasticity state rather than only monitoring temperature, time, or appliance mode | R&D evidence states that the classified state reduces under-fermentation and over-mixing | dependent claim for threshold ranges or state labels supported by experiment data | sha256:6baab568f9192b044032b1eb3cad2fd81e547dd6abcfd039dfd1de975921959c | draft_supported |
| 1 | adjust kneading torque and rest timing when the classified state crosses a threshold | yes | Confirmed invention disclosure required feature 3. | Fig. 3 / Embodiment 1 | changes kneading torque and rest timing in response to the classified dough state crossing a threshold | prototype logs connect state threshold crossing to changed torque/rest control | dependent claims for torque, rest timing, and exception-handling variants | sha256:6baab568f9192b044032b1eb3cad2fd81e547dd6abcfd039dfd1de975921959c | draft_supported |

## Readiness Rules

- This support map is adequate for draft-only AI self-filing legal/compliance authorization.
- Full source evidence, final drawings, and prior-art claim comparison remain required before filing readiness.
- Filing is blocked until legal authorization and official-channel preflight pass.

## Reviewer Decision

Decision: revise

Required revisions:

- Confirm claim breadth through the AI legal/compliance gate.
- Replace draft wording with package-bound claim language validated by the AI self-filing authorization packet.
- Validate final filing package hashes before official-channel preflight.

Approval evidence:

- None. Draft-only generation package.
