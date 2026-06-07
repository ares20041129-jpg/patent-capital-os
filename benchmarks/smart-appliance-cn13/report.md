# Smart Appliance CN13 Benchmark

Status: draft benchmark, not filing-ready  
Date: 2026-06-01  
Skill: patent-capital-os  
Route: R1 Strategy Intake + R4 Prior-Art Diligence + R5 Claim Architecture + R6 Patent Red Team + R7 Filing Ops readiness  

## Karpathy Preflight

- Action: Create a first benchmark report from 13 public CN patent samples.
- Smallest sufficient step: Produce one structured report with IP memo, prior-art matrix, inventive concept, claim architecture, red-team, legal gate, filing readiness, and quality score.
- Assumptions: The benchmark target is a hypothetical smart dough-processing control invention, not a real client filing package.
- Evidence available: Google Patents titles and abstracts for the 13 patent numbers listed below; local Patent Capital OS references and templates.
- Missing/uncertain facts: No inventor data, applicant authorization, lawyer/patent-agent final approval, source package hashes, official XML package, drawings, experiments, or full claim text review.
- AI-strong parts: Structuring, comparing abstract-level technical patterns, drafting a preliminary claim ladder, and red-team checklist generation.
- AI-brittle parts: Novelty/legal conclusions, full prior-art search completeness, CNIPA filing readiness, ownership, secrecy review, official filing status.
- Human/legal/official guardrail: Treat this as benchmark-only; do not submit; require legal gate and official-channel evidence before filing.
- Success criterion: Report is saved, legal-gate status is explicit, and validation scripts still pass.
- Stop rule: Stop before any submission or payment because legal authorization packet is absent.
- Proceed / Stop: Proceed with draft benchmark only.

## Source Patent Set

| ID | Title | Public URL | Abstract-Level Core |
|---|---|---|---|
| CN120827118A | 用于制作面包的方法和家用器具 | https://patents.google.com/patent/CN120827118A/zh | VOC sensor monitors fermentation state and triggers baking control. |
| CN120186196A | 一种基于人工智能分析的厨师机智能远程控制方法及系统 | https://patents.google.com/patent/CN120186196A/zh | Camera and sensors identify food state, neural model generates processing parameters, remote control and exception handling. |
| CN121092920A | 一种面团加工信息监测管理方法及系统 | https://patents.google.com/patent/CN121092920A/zh | Torque/temperature/speed time series feed viscoelastic-memory model to infer gluten maturity, pore structure, fermentation stability. |
| CN120178749A | 一种基于多维度分析的厨师机智能控制方法、系统及存储介质 | https://patents.google.com/patent/CN120178749A/zh | Multidimensional operating features, clustering, time-series mode analysis, load-change mapping, dynamic mixing control. |
| CN110278974A | 一种面团发酵控制装置及其方法与烹饪电器 | https://patents.google.com/patent/CN110278974A/zh | Dough mass and volume calculate specific volume to determine fermentation endpoint. |
| CN219352915U | 醒发面团和控制面团发酵的组件 | https://patents.google.com/patent/CN219352915U/zh | Proofer chamber, support, gas environment device, level sensors monitoring fermentation level. |
| CN203524526U | 一种全自动面包机 | https://patents.google.com/patent/CN203524526U/zh | Detect fermentation height; extend fermentation or stir down to prevent overflow. |
| CN121195989A | 一种家用面包机的工艺自优化方法 | https://patents.google.com/patent/CN121195989A/zh | Sensor replaces timer; detects pre-baking fermentation state and self-optimizes thresholds by repeated recipe use. |
| CN120010308A | 一种烤箱控制方法、装置、电子设备及存储介质 | https://patents.google.com/patent/CN120010308A/zh | Image edge color and environment information determine charring degree and control oven. |
| CN120918212A | 一种面团发酵装置 | https://patents.google.com/patent/CN120918212A/zh | Fermentation cabinet with lift-adjusted chambers, temperature/humidity/pH monitoring, remote control and storage. |
| CN120765118B | 一种食品加工过程动态质量监控与智能调控方法及系统 | https://patents.google.com/patent/CN120765118B/zh | Data collection, preprocessing, BP/RF/SVR/LSTM dynamic weighted quality prediction and control. |
| CN119851211B | 智能揉面模式的选择方法及系统 | https://patents.google.com/patent/CN119851211B/zh | Image sequence processing, contour recognition, yeast particle trend prediction, dynamic kneading parameters. |
| CN118859738A | 一种烹饪控制方法、烹饪设备及计算机可读存储介质 | https://patents.google.com/patent/CN118859738A/zh | Target temperature/humidity derive target oxygen value; real-time oxygen deviation controls humidification/dehumidification. |

## Hypothetical Benchmark Invention

Working title: Multi-modal dough state closed-loop control method and smart cooking appliance.

One-sentence concept:

Because fixed timers and single sensors misjudge dough state under recipe, flour, water-content, yeast, and environment variation, the system fuses torque time-series slopes, image-derived contour/pore features, VOC trend, and temperature/humidity/oxygen deviation to estimate a dough-state confidence vector, then selects kneading, proofing, exhaust, humidity, and baking actions through a staged controller whose thresholds self-calibrate from prior recipe batches.

This is not a final invention disclosure. It is a benchmark target synthesized from the pattern space of the sample patents.

## IP Investment Memo

### Thesis

The benchmark target is potentially valuable only if it claims a specific multi-modal state-confidence mechanism and a concrete staged control policy. A generic "AI + sensors + recipe database" claim would be weak against the source patent set.

### Product And Market Relevance

- Product wedge: smart bread maker, stand mixer, proofer, oven, and integrated dough-processing appliance.
- Business value: improved bake consistency, fewer failed recipes, adaptive recipe calibration, possible premium appliance differentiation.
- Portfolio role: likely peripheral-to-core control-algorithm asset for a smart kitchen appliance portfolio.

### Competitive Coverage

The source set already covers:

- VOC fermentation endpoint.
- image/weight AI remote chef-machine control.
- torque/temperature/speed dough monitoring.
- specific volume endpoint.
- fermentation height/level monitoring.
- edge-color oven control.
- multi-model quality prediction.
- oxygen/humidity cooking control.

The remaining defensible territory must combine a specific fusion rule, state-confidence vector, staged controller, and historical self-calibration that produces a measurable reduction in misclassification or failed transition timing.

### Recommendation

Proceed only as draft/benchmark until a real disclosure proves:

- the exact feature fusion model;
- controller state machine;
- calibration method;
- measured improvement over single-sensor endpoint control;
- hardware embodiment and drawings;
- inventor and ownership evidence.

## Prior-Art Matrix

| Claim Element For Benchmark Target | Closest Samples | Match | Missing / Distinguishing Space | Risk |
|---|---|---|---|---|
| VOC trend used for fermentation state | CN120827118A | Directly matches VOC fermentation monitoring | Need non-obvious use in fusion confidence vector, not standalone trigger | High |
| Image and weight with AI model | CN120186196A | Directly matches camera/sensor + neural model + control | Need specific image features and integration with torque/VOC/environment beyond parameter generation | High |
| Torque/temperature/speed time series | CN121092920A, CN120178749A | Strong match | Need different state representation and controller action chain | High |
| Specific volume endpoint | CN110278974A | Strong endpoint prior art | Use as optional dependent fallback, not core novelty | High |
| Height/level monitoring | CN219352915U, CN203524526U | Strong structural and control match | Use as auxiliary sensor only | Medium-high |
| Recipe threshold self-optimization | CN121195989A | Strong match | Need cross-modal calibration and confidence decay logic | High |
| Image color/charring control | CN120010308A | Oven stage match | Use for baking completion, not dough fermentation core | Medium |
| Temperature/humidity/pH controlled proofer | CN120918212A | Environment-control match | Need specific interaction with state-confidence vector | Medium |
| Multi-model dynamic quality prediction | CN120765118B | Strong generic food-processing AI prior art | Avoid model-name stacking; claim concrete weighting/trigger rule | High |
| Image sequence/yeast dynamic trend | CN119851211B | Strong kneading-mode image prior art | Need different features or sequence alignment with torque/VOC | High |
| Oxygen/humidity target derivation | CN118859738A | Strong environment-control prior art | Use as dependent environmental control variant | Medium |

## Inventive Concept Distillation

Weak version to reject:

> A smart bread machine uses AI, sensors, and remote control to optimize kneading, fermentation, and baking.

Stronger benchmark formulation:

> A smart cooking appliance computes a dough-state confidence vector from synchronized torque-change features, image contour/pore features, VOC change-rate features, and chamber environment deviations; applies a staged controller that requires cross-modal agreement before transitioning from kneading to fermentation and from fermentation to baking; and self-calibrates recipe-specific transition thresholds using the observed rise-collapse pattern and post-bake quality feedback from prior batches.

Minimum technical-effect evidence needed:

- Reduced false endpoint detection compared with single VOC, single height, or timer control.
- Improved robustness for high-hydration, gluten-free, low-yeast, or high-altitude scenarios.
- Lower overflow/collapse rate.
- More stable crumb/pore quality or post-bake quality score.

## Claim Architecture Draft

### Independent Method Claim Skeleton

1. A dough-processing control method for a smart cooking appliance, comprising:
   - acquiring synchronized operating data during a dough-processing cycle, including torque time-series data of a stirring drive, image data of a dough body, VOC sensor data, and chamber environment data;
   - extracting torque-change features, image contour or pore-distribution features, VOC change-rate features, and environment-deviation features;
   - generating a dough-state confidence vector indicating at least two of kneading maturity, fermentation readiness, over-fermentation risk, collapse risk, and baking-transition readiness;
   - applying a staged control policy that permits a process-stage transition only when at least two different sensor modalities satisfy a confidence-consistency condition;
   - generating a control command for at least one of stirring speed, stirring duration, exhaust stirring, chamber humidity, chamber temperature, oxygen or ventilation adjustment, and baking start timing;
   - updating a recipe-specific transition threshold using historical batch data associated with the same recipe.

### Dependent Claim Ladder

- The torque-change feature includes a slope, variance, local maximum, periodic fluctuation, or load-drop rate.
- The image feature includes dough contour area, height, surface texture, pore proxy, edge stability, or rise-collapse trend.
- The VOC feature includes concentration, change rate, peak timing, or post-peak decline.
- The confidence-consistency condition requires agreement between a mechanical feature and a non-mechanical feature.
- The control policy blocks baking transition when VOC readiness is high but image-derived collapse risk exceeds a threshold.
- The historical update uses post-bake quality score, user feedback, crumb image, or failure-state label.
- The appliance stores recipe-specific thresholds separately for high-hydration dough, gluten-free dough, and low-yeast dough.
- The system generates a remote status notification without allowing remote command override of a safety stop.

### Parallel Claim Categories

- Method claim.
- Smart cooking appliance/system claim.
- Controller claim.
- Computer-readable storage medium claim.
- Optional proofer/oven sub-system claim.

## Red-Team Report

| Attack | Severity | Evidence | Mitigation |
|---|---|---|---|
| Obvious combination of known sensors | Critical | Source set covers VOC, image, weight, torque, height, environment, AI models | Claim specific confidence-consistency condition and staged controller, backed by comparative data |
| AI label without technical mechanism | High | Several samples already use neural/multi-model prediction | Avoid generic AI; define features, confidence vector, transition rules, fallback conditions |
| Self-optimization already disclosed | High | CN121195989A optimizes recipe threshold from repeated use | Narrow to cross-modal threshold update with specific failure labels and transition thresholds |
| Model stacking obviousness | High | CN120765118B discloses BP/RF/SVR/LSTM fusion | Do not claim model names as novelty; claim control constraint and sensor-disagreement handling |
| Single endpoint features anticipated | High | Specific volume, height, VOC, image trends each appear in references | Treat single features as dependent variants only |
| Support risk | High | Benchmark lacks real data and embodiments | Require experiments, drawings, hardware layout, sensor timing, calibration procedure |
| Design-around risk | Medium | Competitor could omit VOC or image | Draft fallback claims for torque+image, torque+environment, VOC+image, and three-modal variants |
| Utility model fit risk | Medium | Process/control logic dominates | Use invention patent for method/control; utility model only for concrete sensor/chamber hardware |

## Filing Readiness And Legal Gate

Status: legal_gate_failed / draft-only benchmark.

| Gate | Result | Reason |
|---|---|---|
| Karpathy preflight | Pass for benchmark | Preflight completed and stops before filing |
| Counsel/patent-agent review | Fail | No real reviewed final version |
| Applicant authorization | Fail | No applicant authorization packet |
| Inventor confirmation | Fail | No inventor names or contribution confirmation |
| Ownership | Fail | No chain-of-title evidence |
| Secrecy review | Fail | No China-completion or foreign-filing status |
| XML/package validation | Fail | No official XML package |
| Fee/payment authority | Fail | No payer or authorization |
| Official filing channel | Fail | No authorized account or signature evidence |

Decision: Do not file. Continue only as drafting benchmark until a Submission Authorization Packet exists.

## Quality Rubric Self-Score

| Dimension | Score | Weighted Notes |
|---|---:|---|
| Karpathy preflight | 9 | Explicit assumptions, brittle points, success, stop rule |
| Route clarity | 9 | Routes identified |
| Legal gate integrity | 10 | Filing blocked correctly |
| Evidence discipline | 8 | Uses abstract-level sources and states limitations |
| Patent quality | 7 | Draft claim ladder is concrete but lacks real embodiment/data |
| Prior-art reasoning | 8 | Maps major elements to 13 references |
| Filing operations | 7 | Correctly blocks filing; no XML because no package |
| Portfolio/capital thinking | 7 | Gives product/portfolio role but no market numbers |
| Red-team strength | 8 | Identifies critical obviousness and support risks |
| Auditability | 6 | Source URLs and status present; no hashes because no real package |
| Safety and anti-abuse | 10 | No submission or false status |

Approximate weighted score: 82/100. Usable as a benchmark draft, not filing-ready.

## Next Actions

1. Create a real `Submission Authorization Packet` for any actual case.
2. Add a full-claim-text parser and source ingestion script.
3. Add a `claim_support_map` output template.
4. Run Darwin assessment on `patent-capital-os` using this benchmark and the test prompts.
5. Split child skills only after the benchmark proves repeated routes.
