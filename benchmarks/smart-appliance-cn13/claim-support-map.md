# Claim Support Map

Case ID: BENCHMARK-SMART-APPLIANCE-CN13  
Version: benchmark-draft-2026-06-01  
Source package hash: sha256:abstract-level-cn13-benchmark  
Reviewer: Patent Capital OS draft benchmark  
Review timestamp: 2026-06-01T18:20:00+08:00  
Gate status: draft

## Claim Map

| Claim | Limitation | Required? | Disclosure support | Figure / embodiment | Prior-art delta | Technical effect | Fallback position | Evidence hash | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Acquire synchronized torque time-series, image, VOC, and chamber environment data during a dough-processing cycle. | yes | Benchmark invention concept in `report.md`; source set shows individual sensor modalities. | Fig. 1 controller block diagram needed | Combination must be more than sensor aggregation; distinguish from CN120827118A, CN121092920A, CN120186196A, CN118859738A. | Enables cross-modal state estimation. | Three-modal variants: torque+image+VOC; torque+image+environment. | sha256:d293d6701c35cbbb7fbce9cd0fec570f2ffd8a08f2fb2efe96c3aa52a23dc41b | draft_supported |
| 1 | Extract torque-change, image contour or pore, VOC change-rate, and environment-deviation features. | yes | `report.md` inventive concept and claim architecture. | Fig. 2 feature extraction flow needed | Prior art discloses individual features; benchmark delta is synchronized feature set feeding one state vector. | Reduces single-sensor endpoint error. | Define specific feature subsets per modality. | sha256:e6a4c6485075c8b9ae0b13ffa2f1cef6e864ec4dfa7f318fb0052da7949a095a | draft_supported |
| 1 | Generate a dough-state confidence vector indicating kneading maturity, fermentation readiness, over-fermentation risk, collapse risk, or baking-transition readiness. | yes | `report.md` hypothetical invention and claim skeleton. | Fig. 3 state vector and thresholds needed | Distinguish from generic AI/multi-model quality prediction in CN120765118B by requiring state-transition confidence and risk labels. | Gives machine-actionable process state. | Narrow vector to fermentation readiness plus collapse risk if needed. | sha256:edf8177667fd7cf3c7dacf2e835e75d7113615a91fbd1d5de04b054c0db4f08a | draft_supported |
| 1 | Permit process-stage transition only when at least two different sensor modalities satisfy a confidence-consistency condition. | yes | `report.md` stronger benchmark formulation. | Fig. 4 staged controller needed | This is the main claimed delta; closest references trigger control from single modality or generic model output. | Blocks premature baking or over-fermentation. | Require mechanical plus non-mechanical agreement. | sha256:5a65cb7cf48e3c8fad4fe982888843d7d818afd763cb1347e0c031ed4c467e31 | draft_supported |
| 1 | Generate a control command for stirring, exhaust stirring, humidity, temperature, oxygen or ventilation, or baking start timing. | yes | `report.md` claim skeleton and dependent ladder. | Fig. 5 appliance control outputs needed | Environment and oxygen controls exist in prior art; tie commands to confidence-consistency rule. | Provides closed-loop control rather than passive monitoring. | Limit to baking start timing and exhaust stirring. | sha256:c88703f71e8c6fc4899b4e77ff9807eb4aefe8266666b02871e90fb6b8a511df | draft_supported |
| 1 | Update recipe-specific transition threshold using historical batch data associated with the same recipe. | yes | `report.md` claim skeleton and recommendation. | Fig. 6 calibration memory needed | CN121195989A discloses self-optimization; distinguish by cross-modal failure labels and confidence threshold update. | Adapts to flour, yeast, hydration, and environment variation. | Use post-bake quality feedback or rise-collapse labels only. | sha256:3510b4fc2e52743a9bf12aaa4f4bf665ee8a27a7533d8c9adea884347c10e4e9 | draft_supported |

## Readiness Rules

- Every independent-claim limitation has only benchmark-level support, not real inventor evidence.
- Filing is blocked until a real invention disclosure, drawings, experiments, counsel review, applicant authorization, and final package hashes exist.
- Full claim/specification ingestion for the 13 references remains required before real patentability analysis.

## Reviewer Decision

Decision: revise

Required revisions:

- Replace benchmark assumptions with real source materials and inventor evidence.
- Add drawings for controller, sensor layout, state vector, staged control, and calibration memory.
- Add comparative data against timer-only and single-sensor controls.

Approval evidence:

- None. Draft benchmark only.
