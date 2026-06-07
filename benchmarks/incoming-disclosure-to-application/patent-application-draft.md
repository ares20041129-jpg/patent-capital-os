# Patent Application Draft

Case ID: INCOMING-DISCLOSURE-APP-001  
Draft version: benchmark-draft-2026-06-01  
Source material manifest: source-material-manifest.yaml  
Disclosure hash: sha256:6cf74b95c4758ab461a38fddc1e53aa54d2b070431fb26f6f9c37d362484faa8  
Draft status: ai_self_filing_authorization_needed

## Title

Multi-modal dough state transition control method and smart cooking appliance.

## Technical Field

The draft relates to smart cooking appliances, bread makers, dough processing controllers, and closed-loop control of kneading, fermentation, exhaust, environment adjustment, and baking transition timing.

## Background

Timer-only dough processing and single-sensor fermentation endpoints can misjudge dough state when flour protein, hydration, yeast activity, recipe type, and chamber environment vary. Known references disclose individual monitoring paths such as VOC fermentation sensing, torque or speed time-series analysis, image-based food state recognition, fermentation height monitoring, and recipe self-optimization.

Closest known references:

| Reference | Relevance | Claim risk |
| --- | --- | --- |
| CN120827118A | VOC fermentation state and baking trigger | High risk for standalone VOC readiness |
| CN121092920A | Torque/temperature/speed dough processing model | High risk for mechanical time-series features |
| CN121195989A | Bread maker process self-optimization | High risk for generic recipe threshold update |
| CN120765118B | Multi-model food process quality monitoring and control | High risk for generic AI/model fusion |

## Technical Problem

The technical problem is to reduce false stage transitions in dough processing when one signal indicates readiness while other modalities still indicate insufficient kneading, under-fermentation, over-fermentation, collapse risk, or environmental deviation.

## Technical Solution

Required features:

1. Acquire synchronized torque time-series, dough image, VOC, and chamber environment signals.
2. Extract torque-change, image contour or pore proxy, VOC change-rate, and environment-deviation features.
3. Generate a dough-state confidence vector for kneading maturity, fermentation readiness, over-fermentation risk, collapse risk, and baking-transition readiness.
4. Permit a stage transition only when at least two different sensor modalities satisfy a confidence-consistency condition.
5. Generate a control command for stirring, exhaust stirring, humidity, temperature, ventilation, oxygen adjustment, or baking start timing.
6. Update recipe-specific transition thresholds using historical batch feedback associated with the same recipe.

Optional features:

1. Block baking transition when VOC readiness is high but image-derived collapse risk exceeds a threshold.
2. Use a torque plus image fallback when VOC data is unavailable.
3. Store threshold sets separately for high-hydration, low-yeast, or gluten-free dough.

## Beneficial Technical Effects

| Effect | Evidence | Source material ID | Confidence |
| --- | --- | --- | --- |
| Reduces false fermentation-to-baking transition compared with timer-only control | Prototype log summary | M-002 | benchmark |
| Detects sensor disagreement before stage transition | Controller block diagram and disclosure | M-001, M-003 | benchmark |
| Improves recipe adaptation across batch history | Invention disclosure threshold-update section | M-001 | benchmark |

## Brief Description Of Drawings

| Figure | Description | Required for claim support? |
| --- | --- | --- |
| Fig. 1 | Smart cooking appliance with torque sensor, camera, VOC sensor, environment sensor, controller, and recipe memory | yes |
| Fig. 2 | Sensor synchronization and feature extraction flow | yes |
| Fig. 3 | Dough-state confidence vector generation | yes |
| Fig. 4 | Confidence-consistency stage transition controller | yes |
| Fig. 5 | Recipe-specific threshold update using historical batch feedback | yes |

## Detailed Embodiments

### Embodiment 1

Components:

A smart bread maker includes a stirring motor with torque sensing, a chamber camera, a VOC sensor, temperature and humidity sensors, a controller, and recipe threshold memory.

Steps:

1. During a dough-processing cycle, the controller collects a synchronized sensor window.
2. The controller computes torque slope or load-drop features, image contour stability or pore proxy features, VOC concentration change-rate features, and chamber environment-deviation features.
3. The controller generates a confidence vector representing kneading maturity, fermentation readiness, over-fermentation risk, collapse risk, and baking-transition readiness.
4. The controller permits a process-stage transition only when a mechanical modality and at least one non-mechanical modality satisfy a confidence-consistency condition.
5. If modalities disagree, the controller extends the current stage, performs exhaust stirring, adjusts humidity or temperature, or delays baking.
6. After batch completion, the controller updates recipe-specific transition thresholds using batch feedback.

Parameters:

- Sensor window length may be 30-180 seconds.
- Stage transition may require at least two modalities to satisfy confidence thresholds.
- Thresholds may be stored per recipe class.

Alternatives:

The appliance may use torque plus image when VOC data is unavailable, or VOC plus image when torque data is unavailable, if the fallback is supported by calibration data.

Failure handling:

When sensor disagreement exceeds a threshold or a sensor is unavailable, the controller blocks automatic baking transition and records a failure label for later calibration.

## Claims Draft

### Independent Claim Candidates

1. A dough-processing control method for a smart cooking appliance, comprising: acquiring synchronized operating data during a dough-processing cycle, the operating data including torque time-series data of a stirring drive, image data of a dough body, VOC sensor data, and chamber environment data; extracting torque-change features, image contour or pore-distribution features, VOC change-rate features, and environment-deviation features; generating a dough-state confidence vector indicating at least kneading maturity, fermentation readiness, over-fermentation risk, collapse risk, or baking-transition readiness; applying a staged control policy that permits a process-stage transition only when at least two different sensor modalities satisfy a confidence-consistency condition; generating a control command for at least one of stirring speed, stirring duration, exhaust stirring, chamber humidity, chamber temperature, oxygen or ventilation adjustment, and baking start timing; and updating a recipe-specific transition threshold using historical batch data associated with the same recipe.

### Dependent Claim Ladder

2. The method of claim 1, wherein the torque-change feature includes at least one of slope, variance, local maximum, periodic fluctuation, or load-drop rate.
3. The method of claim 1, wherein the image feature includes at least one of dough contour area, height, surface texture, pore proxy, edge stability, or rise-collapse trend.
4. The method of claim 1, wherein the confidence-consistency condition requires agreement between a mechanical feature and a non-mechanical feature.
5. The method of claim 1, wherein a baking transition is blocked when VOC readiness is high and image-derived collapse risk exceeds a threshold.
6. The method of claim 1, wherein the historical batch data includes post-bake quality score, user feedback, crumb image, or failure-state label.
7. A smart cooking appliance comprising sensors, a controller, and memory configured to perform the method of claim 1.

## Abstract

A smart cooking appliance acquires synchronized torque, image, VOC, and chamber environment data during dough processing, extracts modality-specific features, generates a dough-state confidence vector, and permits stage transitions only when at least two modalities satisfy a confidence-consistency condition. The appliance generates stirring, exhaust, environment, ventilation, or baking timing commands and updates recipe-specific transition thresholds using historical batch feedback.

## Claim Support Map Link

See claim-support-map.md for limitation-level support and benchmark evidence hashes.

## AI Legal/Compliance Questions

- Confirm technical distinction over full claims and descriptions of CN120765118B, CN121195989A, CN121092920A, and CN120827118A before AI self-filing authorization.
- Confirm whether fallback modality subsets have enough source support for dependent claims.
- Confirm whether a utility model should be limited to sensor/chamber hardware while the method remains an invention filing.

## Filing Gate

Do not file this draft. The legal gate has not passed because final AI self-filing legal/compliance authorization, applicant filing authorization, final XML package, fee authorization, and official-channel preflight are not validated for this case.
