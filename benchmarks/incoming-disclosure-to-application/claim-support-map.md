# Claim Support Map

Case ID: INCOMING-DISCLOSURE-APP-001  
Version: benchmark-draft-2026-06-01  
Source package hash: sha256:573cc3efea6c9ef9ef569f67315abb3aa3fc90c69f25969526708600d8b17778  
Reviewer: Patent Capital OS draft generator  
Review timestamp: 2026-06-01T19:20:00+08:00  
Gate status: draft

## Claim Map

| Claim | Limitation | Required? | Disclosure support | Figure / embodiment | Prior-art delta | Technical effect | Fallback position | Evidence hash | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Acquire synchronized torque time-series, image, VOC, and chamber environment signals. | yes | M-001 disclosure required features; M-003 controller diagram. | Fig. 1 and Fig. 2 | Prior art shows individual modalities; synchronized multi-modal window must be supported. | Enables cross-modal dough-state estimation. | Three-modal subset if one sensor unavailable. | sha256:6cf74b95c4758ab461a38fddc1e53aa54d2b070431fb26f6f9c37d362484faa8 | draft_supported |
| 1 | Extract torque-change, image contour or pore proxy, VOC change-rate, and environment-deviation features. | yes | M-001 feature list; M-002 prototype log summary. | Fig. 2 | Delta is feature extraction aligned to one state window, not isolated sensing. | Reduces single-sensor endpoint error. | Limit to torque slope, contour stability, VOC rate, humidity deviation. | sha256:ace5a3fd82f7b5fb63688094fd0106f745e5b1ee69a5f6c19f9c0715c30998cc | draft_supported |
| 1 | Generate a dough-state confidence vector for maturity/readiness/risk states. | yes | M-001 technical solution and embodiment. | Fig. 3 | Delta over generic model prediction is explicit state vector used for transition control. | Produces machine-actionable stage state. | Narrow to fermentation readiness and collapse risk. | sha256:6cf74b95c4758ab461a38fddc1e53aa54d2b070431fb26f6f9c37d362484faa8 | draft_supported |
| 1 | Permit transition only when at least two modalities satisfy confidence-consistency. | yes | M-001 technical contribution; M-003 controller flow. | Fig. 4 | Main delta over known single-trigger endpoints. | Blocks premature stage transition. | Mechanical plus non-mechanical agreement. | sha256:49771d6235b5197776378a1fb940467ded64873dbf5ea0b507ed469875203cb0 | draft_supported |
| 1 | Generate stirring, exhaust, humidity, temperature, ventilation, oxygen, or baking timing command. | yes | M-001 embodiment steps. | Fig. 4 | Tie environment controls to confidence-consistency result. | Converts detection into closed-loop control. | Limit command list to stirring/exhaust/baking timing if needed. | sha256:6cf74b95c4758ab461a38fddc1e53aa54d2b070431fb26f6f9c37d362484faa8 | draft_supported |
| 1 | Update recipe-specific transition threshold using historical batch data. | yes | M-001 threshold update feature; M-002 batch feedback summary. | Fig. 5 | Must distinguish from generic self-optimization by using confidence-consistency failure labels. | Improves recipe adaptation over repeated batches. | Use post-bake quality score or failure-state label only. | sha256:ace5a3fd82f7b5fb63688094fd0106f745e5b1ee69a5f6c19f9c0715c30998cc | draft_supported |

## Readiness Rules

- This support map is adequate for a benchmark draft only.
- Full raw logs, drawings, prior-art full claims, and AI legal/compliance authorization are still required before filing readiness.
- Filing is blocked until legal authorization and official-channel preflight pass.

## Reviewer Decision

Decision: revise

Required revisions:

- Replace benchmark hashes with actual file hashes.
- Add raw experiment data and final drawings.
- Add full prior-art claims and description analysis.
- Obtain AI self-filing legal/compliance authorization tied to the final package hash.

Approval evidence:

- None. Draft-only benchmark.
