# Patent Capital OS Worklog

## 2026-06-08 07:36 +08:00

Karpathy preflight:

- Assumptions: the active goal is to design a comprehensive, top-tier GitHub marketing strategy for the Patent Capital OS skill before expanding execution; existing `MARKETING.md` is an execution kit and needs a deeper strategy layer.
- Smallest sufficient action: add a strategy document that explains audience architecture, category design, trust model, narrative, GitHub surfaces, growth loops, metrics, risks, and claim guardrails; then link it from README, `MARKETING.md`, and `PUBLISHING.md`.
- Evidence check: current GitHub README, topics, issues, discussions, labels, and launch kit already exist; GitHub and OpenSSF sources were checked for README, topics, discussions, and open-source best-practice trust mechanics.
- Jagged-intelligence check: AI can write impressive marketing words that overclaim adoption or legal authority. The strategy must make trust, proof, and official-boundary discipline the differentiator instead of adding hype.
- Success criteria: repository contains a strategic GitHub marketing document that is materially more comprehensive than the execution kit, points back to authoritative GitHub/OpenSSF sources, and preserves all no-official-submission and no-fabricated-adoption constraints.
- Stop rule: do not alter patent workflow semantics, legal gates, official filing boundaries, or public adoption claims.

Backup:

- `<skill-root>\backups\20260608-top-tier-github-marketing-strategy`

Changes recorded:

- Added `docs\github-marketing-strategy.md` as the strategic thinking layer behind the GitHub launch kit.
- The strategy covers executive thesis, source base, constraints, audience tiers, category design, narrative architecture, GitHub surface strategy, trust flywheel, content system, 90-day plan, metrics, experiments, risk register, claim matrix, maintainer operating model, and strategic checklist.
- Updated `MARKETING.md` to point to `docs/github-marketing-strategy.md` for deeper strategy.
- Updated `README.md` and `PUBLISHING.md` so the strategic document is part of the GitHub publishing and maintainer evidence surface.

Source notes:

- GitHub README guidance: `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes`
- GitHub repository topics guidance: `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics`
- GitHub Discussions guidance: `https://docs.github.com/en/discussions`
- OpenSSF Best Practices Badge program: `https://openssf.org/projects/best-practices-badge/`

Verification:

- Markdown/link inspection with `rg`: confirmed `docs/github-marketing-strategy.md` is linked from `README.md`, `MARKETING.md`, `PUBLISHING.md`, and `WORKLOG.md`.
- `git diff --check`: passed, with the existing `WORKLOG.md` CRLF normalization warning only.
- `python -m json.tool test-prompts.json`: passed.
- `CITATION.cff` YAML parse: passed.
- `gh repo view ares20041129-jpg/patent-capital-os --json description,repositoryTopics,hasIssuesEnabled,hasDiscussionsEnabled,url`: confirmed description, topics, Issues, and Discussions remain aligned.

## 2026-06-08 04:50 +08:00

Karpathy preflight:

- Assumptions: the user clarified that the need is not a generic marketing plan, but a GitHub-specific marketing and positioning kit for the Patent Capital OS skill itself.
- Smallest sufficient action: rewrite `MARKETING.md` as a GitHub launch kit, sharpen the README first-screen positioning, update publishing checklist wording, and configure GitHub repository metadata plus starter contribution entrypoints.
- Evidence check: the repository is public at `https://github.com/ares20041129-jpg/patent-capital-os`; GitHub repo settings, topics, labels, and issues can be updated through `gh`; changes must not touch patent workflow code or official filing boundaries.
- Jagged-intelligence check: marketing copy can easily overclaim usage, legal authority, or official filing capability. Keep the plan tied to GitHub presentation, developer trust, validation evidence, and truthful public contribution paths.
- Success criteria: GitHub visitors can understand the patent skill in 30 seconds, see the no-official-submission boundary, find contribution entrypoints, and recognize Cyrus Sheng as the active maintainer without fabricated adoption claims.
- Stop rule: do not create fake adopters, fake testimonials, fake usage metrics, fake legal review, or any claim that the skill performs real official filing.

Backup:

- `<skill-root>\backups\20260608-github-skill-marketing-kit`

Changes recorded:

- Rewrote `MARKETING.md` from a broad channel/ad plan into `GitHub Launch Kit` for this patent skill, covering repository positioning, GitHub one-liner, topics, README first screen, developer value, differentiation, conversion path, release copy, issue strategy, discussion prompts, adopter evidence, profile copy, star pitch, contributor pitch, GitHub SEO, forbidden claims, and maintainer rhythm.
- Updated `README.md` first-screen copy so the repository presents Patent Capital OS as an open-source Codex skill for evidence-bound patent workflow automation aimed at developers and GPT builders.
- Added a concise `Why Developers Should Care` section to the README.
- Updated `PUBLISHING.md` so `MARKETING.md` is described as the GitHub launch kit for this patent skill.
- Updated GitHub repository description to: `Evidence-bound Codex skill for patent intake, AI legal/compliance gates, application-material generation, quality review, and read-only pre-submission handoff.`
- Updated GitHub topics to include `ai-agents`, `gpt-skills`, `legal-compliance`, `patent-automation`, and `patent-workflow` alongside the existing project topics.
- Enabled GitHub Issues and Discussions.
- Added GitHub labels: `benchmark`, `validator`, `workflow`, `legal-boundary`, and `patent-domain`.
- Created starter issues:
  - `#1` Add a compact architecture diagram to the README.
  - `#2` Add a minimal sample inbox fixture for first-time users.
  - `#3` Document which validators protect each workflow boundary.
  - `#4` Clarify draft generation vs handoff readiness vs official submission.
  - `#5` Add contributor guidance for rejection benchmarks.

Verification:

- `gh repo view ares20041129-jpg/patent-capital-os --json description,repositoryTopics,hasIssuesEnabled,hasDiscussionsEnabled,url`: confirmed description, topics, Issues, and Discussions.
- Starter issues `#1` through `#5` were created under the public repository.

## 2026-06-08 04:21 +08:00

Karpathy preflight:

- Assumptions: the user wants the public project and author/maintainer identity to present as Cyrus Sheng while keeping the existing GitHub login and repository URLs stable; the marketing plan should target developers, GPT builders, agent engineers, and adjacent legaltech/IP operators without fabricating adoption.
- Smallest sufficient action: update repository-facing maintainer/author metadata, update the public profile README, add a focused `MARKETING.md`, and preserve the existing patent workflow, legal/compliance gates, official-boundary flags, scripts, benchmarks, and release semantics.
- Evidence check: current GitHub repository and profile repository exist under `ares20041129-jpg`; GitHub profile README can be updated through the repository contents API; changing the GitHub account display-name field requires an additional `user` OAuth scope that the current CLI token does not have.
- Jagged-intelligence check: AI is useful for positioning, launch sequencing, and documentation consistency, but brittle at claiming market traction or changing external account settings without authenticated scope. Marketing copy must stay evidence-based and must not claim legal advice, official filing, broad usage, or ecosystem dependence before public proof exists.
- Success criteria: local docs identify Cyrus Sheng as author/primary maintainer, public profile README starts with `# Cyrus Sheng`, marketing plan exists, validation checks pass, and GitHub display-name scope limitation is recorded honestly.
- Stop rule: do not fabricate adoption, testimonials, attorney/legal review, official filing status, GitHub profile fields, or external advertising performance.

Backup:

- `<skill-root>\backups\20260608-cyrus-sheng-brand-marketing`

Changes recorded:

- Updated `README.md`, `MAINTAINERS.md`, `GOVERNANCE.md`, `CITATION.cff`, `NOTICE`, `docs\maintainer-application-evidence.md`, and `docs\github-profile-readme.md` so the public author/maintainer identity is Cyrus Sheng with GitHub handle `@ares20041129-jpg`.
- Updated local git author name to `Cyrus Sheng` while keeping the GitHub noreply email.
- Updated the public GitHub profile README through the profile repository API so it now opens with `# Cyrus Sheng` and links to Patent Capital OS, governance, maintainer role, roadmap, adoption tracking, and marketing/community plan.
- Added `MARKETING.md` with positioning, audience, launch hooks, channel strategy, content assets, launch copy, KPIs, guardrails, and a weekly maintainer rhythm for developers, GPT builders, agent engineers, and legaltech/IP operators.
- Updated `PUBLISHING.md` so the GitHub release checklist includes `MARKETING.md`.

Marketing source notes:

- Stack Overflow advertising, Reddit community targeting, LinkedIn Ads, OpenAI Developers, and OpenAI Developer Community were checked as current channel references for developer/GPT-builder distribution planning.

Verification:

- `python -m json.tool test-prompts.json`: passed.
- `python -c "import yaml ..."` over `CITATION.cff`: passed.
- `gh api repos/ares20041129-jpg/ares20041129-jpg/contents/README.md`: confirmed the remote profile README begins with `# Cyrus Sheng`.
- `gh api user -X PATCH -f name='Cyrus Sheng' ...`: blocked by missing GitHub `user` scope; `gh auth refresh -h github.com -s user` timed out in the interactive authorization flow, so the GitHub display-name field remains pending external authorization.
- `gh api user --jq '{login:.login,name:.name,bio:.bio,html_url:.html_url}'`: returned `name=null`, confirming the display-name field has not yet been changed by API.
- Commit `e64165b` (`Align maintainer brand with Cyrus Sheng`) was pushed to `main`.
- GitHub Actions run `27103779711`: success for the default CI smoke gate; default push CI validated prompt JSON and Python compilation, while the manual full-regression steps remained skipped by workflow design.

## 2026-06-08 04:09 +08:00

Karpathy preflight:

- Assumptions: the public GitHub repository and public maintainer profile have been created under `ares20041129-jpg`; the goal is to record publication evidence without changing workflow semantics.
- Smallest sufficient action: record the public repo, profile repo, release, topics, and CI result.
- Evidence check: GitHub CLI confirmed the project repo and profile repo are public, `v0.1.0` is published, topics are set, and CI completed successfully.
- Jagged-intelligence check: public visibility and maintainer status are real, but ecosystem importance and broad usage must still be earned through public adoption evidence.
- Success criteria: worklog records public release evidence and no local uncommitted changes remain after push.
- Stop rule: do not claim many users, downstream dependencies, or ecosystem importance until `ADOPTERS.md`, issues, forks, stars, citations, or integrations provide evidence.

Publication evidence:

- Public project repo: `https://github.com/ares20041129-jpg/patent-capital-os`
- Public profile repo: `https://github.com/ares20041129-jpg/ares20041129-jpg`
- Release: `https://github.com/ares20041129-jpg/patent-capital-os/releases/tag/v0.1.0`
- Topics: `ai-workflows`, `codex-skill`, `ip`, `legaltech`, `open-source`, `patent`, `workflow-automation`
- CI run `27103403471`: success.

Verification:

- `gh repo view ares20041129-jpg/patent-capital-os`: `visibility=PUBLIC`, `isPrivate=false`.
- `gh repo view ares20041129-jpg/ares20041129-jpg`: `visibility=PUBLIC`, `isPrivate=false`.
- `gh release view v0.1.0`: published, not draft, not prerelease.
- `git status --short`: clean before this worklog entry.

## 2026-06-08 03:54 +08:00

Karpathy preflight:

- Assumptions: the local skill loop is already closed and regression-green; the current gap is GitHub repository presentation and publishing hygiene, not workflow semantics.
- Smallest sufficient action: add repository-facing documentation and ignore rules without changing the patent workflow, legal gate, queue logic, benchmark contracts, or official boundary.
- Evidence check: the repository currently lacks a GitHub-facing `README`, contribution/security guidance, dependency entrypoint, and ignore policy even though the skill itself is implemented.
- Jagged-intelligence check: AI can over-edit internal workflow files when asked to "optimize for GitHub"; keep the change set to repository metadata and publishability docs only.
- Success criteria: add clear repository docs, add `.gitignore`, add `requirements.txt`, preserve workflow code unchanged, and verify the repository still parses and compiles where touched.
- Stop rule: do not change filing logic, legal-gate semantics, benchmark expectations, or any official-action boundary.

Backup:

- `<skill-root>\backups\20260608-ship-github-optimization`

Changes recorded:

- Added `README.md` with repository overview, capabilities, boundaries, quick start, layout, and publishing notes.
- Added `.gitignore` to exclude local runtime outputs, backups, caches, and export archives from Git tracking.
- Added `requirements.txt` with the explicit external runtime dependency surface.
- Added `CONTRIBUTING.md` with invariants, validation expectations, and PR guidance.
- Added `SECURITY.md` with the repository security boundary and high-risk change areas.
- Added `PUBLISHING.md` as a release and GitHub setup checklist.

Verification:

- `python -m json.tool test-prompts.json`: passed.
- `python -m py_compile` over all `scripts/*.py`: passed.
- repository-facing changes preserved the existing skill, benchmark, and official boundary files unchanged.

## 2026-06-08 04:00 +08:00

Karpathy preflight:

- Assumptions: the user wants the project to qualify as a credible active open-source project with a public primary/core maintainer; the logged-in GitHub account is `ares20041129-jpg`; public adoption must be earned and tracked rather than fabricated.
- Smallest sufficient action: add maintainer, governance, adopter, roadmap, license, CI, and community files that make the repository public-maintainer-ready without changing workflow semantics.
- Evidence check: maintainer evidence should be visible in `MAINTAINERS.md`, `GOVERNANCE.md`, `CODEOWNERS`, GitHub templates, CI, and `docs/maintainer-application-evidence.md`.
- Jagged-intelligence check: AI can overstate ecosystem importance; the new docs explicitly avoid unsupported usage claims and route adoption proof through public evidence.
- Success criteria: repository includes primary maintainer evidence, open-source license, public governance, adoption tracking, CI, and issue/PR templates; validators and compile checks still pass.
- Stop rule: do not claim broad usage, ecosystem importance, or downstream dependency until public evidence exists.

Backup:

- `<skill-root>\backups\20260608-open-source-maintainer-readiness`

Changes recorded:

- Added Apache-2.0 `LICENSE` and `NOTICE`.
- Added `MAINTAINERS.md`, `GOVERNANCE.md`, `ROADMAP.md`, `ADOPTERS.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `CHANGELOG.md`, and `CITATION.cff`.
- Added `docs\maintainer-application-evidence.md` and `docs\github-profile-readme.md`.
- Added `.github\CODEOWNERS`, pull request template, issue templates, and CI workflow.
- Added `.gitattributes` to keep public text files normalized to LF and binary fixtures treated as binary.
- Updated `README.md` and `PUBLISHING.md` with maintainer, adoption, governance, license, and GitHub visibility guidance.
- Sanitized publishable docs by replacing local machine paths with `<skill-root>` and `<codex-skill-root>` placeholders outside benchmark fixtures.
- Adjusted GitHub CI to run smoke checks on push/PR and keep full regression as a manual workflow dispatch option.

Verification:

- `python -m json.tool test-prompts.json`: passed.
- GitHub workflow and issue-template YAML parse: passed for 5 files after CI adjustment.
- `py_compile` over all `scripts/*.py`: passed for 115 scripts after clearing generated `scripts\__pycache__`.
- Secret-pattern scan over publishable files excluding `out/`, `backups/`, and `.git`: no matches.
- Publishable docs path scan excluding `benchmarks/`, `out/`, `backups/`, and `.git`: no local machine path matches.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=76 failed=0`, `artifact_manifests.total=174 failed=0`, `source_compile.total=115 failed=0`, `json_parse.total=745 failed=0`, `yaml_parse.total=133 failed=0`, `structured_sha256_placeholders.total=816 failed=0`, `structured_dangerous_true_fields.total=816 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 13:29 +08:00

Karpathy preflight:

- Assumptions: the inbox-to-handoff batch path is already green; the remaining skill-closure gap is a production-control handoff index plus a local completion audit, not API deployment or official submission.
- Smallest sufficient action: add thin read-only index and audit generators, validators, static benchmarks, queue registration, runbook, and skill documentation.
- Evidence check: the index must recompute per-case handoff hashes and preserve quality/reference-delta/no-official-action fields; the audit must validate local evidence for reference delta, materials, AI legal gate, inbox, rejection gates, handoff, index, runbook, regression contract, and official boundary.
- Jagged-intelligence check: AI can confuse readiness with filed status or over-trust a summary artifact; the new validators re-read source inbox evidence, re-run local validators, and keep adapter execution, receipt capture, and application-number evidence as later gates.
- Success criteria: new index and audit validators pass, generated queue/batch consumption passes, full regression passes, and all official action/external-lawyer flags remain false.
- Stop rule: do not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-131732-skill-closure-index-audit`
- `benchmarks\inbox-handoff-index\` and `benchmarks\skill-completion-audit\` did not exist before this stage and were generated as new benchmark evidence.

Changes recorded:

- Added `scripts\prepare_inbox_handoff_index.py` to summarize an inbox-to-handoff output into `inbox-handoff-index.json`, `inbox-handoff-index.md`, and `artifact-hashes.json`.
- Added `scripts\validate_inbox_handoff_index_benchmark.py` to validate source inbox evidence, per-case handoff hashes, quality gate fields, reference-delta preservation, next actions, and no-official-action flags.
- Added `scripts\prepare_skill_completion_audit.py` to generate a local no-auto-submit skill closure audit across reference delta, application materials, AI legal/compliance gate, inbox processing, unsafe input rejection, handoff, index, runbook, regression contract, and official boundary.
- Added `scripts\validate_skill_completion_audit_benchmark.py` to revalidate each completion-audit evidence item against local files and validators.
- Added `references\production-intake-runbook.md` for received material layout, commands, outputs, failure handling, archive rule, and the `approved_for_adapter_execution` / `handoff_ready_no_auto_submit` boundary.
- Updated `scripts\build_case_queue.py` and `scripts\run_case_queue.py` so `inbox-handoff-index` and `skill-completion-audit` are discovered, queued, validated, and reported.
- Updated `references\workflow-orchestration.md`, `references\case-queue-batch-processor.md`, `references\production-architecture.md`, `SKILL.md`, and `test-prompts.json` to document the handoff index and completion audit closure steps.
- Generated `benchmarks\inbox-handoff-index\`, `benchmarks\skill-completion-audit\`, `out\skill-closure-queue.json`, and `out\skill-closure-runner-result.json`.

Verification:

- `py_compile` on the four new scripts: passed.
- `prepare_inbox_handoff_index.py benchmarks\inbox-to-handoff --output-dir benchmarks\inbox-handoff-index --json`: passed with `summary.total=2`, `passed=2`, `reference_delta_cases=1`, no manifest errors, and no official action/external-lawyer flags.
- `validate_inbox_handoff_index_benchmark.py benchmarks\inbox-handoff-index --json`: passed with expected source support warnings only.
- `prepare_skill_completion_audit.py --skill-root . --output-dir benchmarks\skill-completion-audit --json`: passed with `summary.total=10`, `passed=10`, no manifest errors, and no official action/external-lawyer flags.
- `validate_skill_completion_audit_benchmark.py benchmarks\skill-completion-audit --json`: passed with expected source support warnings only.
- `build_case_queue.py` for the index and audit benchmarks: passed with `expected_outcome=inbox_handoff_index` and `expected_outcome=skill_completion_audit`, AI-only legal mode, and `external_lawyer_involved=false`.
- `run_case_queue.py out\skill-closure-queue.json --output out\skill-closure-runner-result.json --json`: passed with `summary.total=2`, `passed=2`, no official action flags, and next actions limited to read-only index/audit closure.
- `validate_case_queue.py out\skill-closure-queue.json --json`: passed.
- `validate_batch_processor_result.py out\skill-closure-runner-result.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\inbox-handoff-index\artifact-hashes.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\skill-completion-audit\artifact-hashes.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=76 failed=0`, `artifact_manifests.total=174 failed=0`, `source_compile.total=115 failed=0`, `json_parse.total=745 failed=0`, `yaml_parse.total=133 failed=0`, `structured_sha256_placeholders.total=816 failed=0`, `structured_dangerous_true_fields.total=816 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 07:07 +08:00

Karpathy preflight:

- Assumptions: the single-case pre-submission-to-handoff path is green; the remaining production intake gap is batching received raw-material folders into the same verified handoff state without real official execution.
- Smallest sufficient action: add a thin inbox batch orchestrator and validator that reuse existing single-case gates, register the folder with queue/build/regression, and create one benchmark with a normal case plus a reference-delta configured case.
- Evidence check: every processed case must pass `validate_pre_submission_to_handoff_benchmark`, the inbox-level queue and batch result must validate, the inbox manifest must validate, and the reference-delta case must be present.
- Jagged-intelligence check: AI can mis-handle inbox paths, confuse aggregate readiness with official submission, or skip reference-delta preservation; the new entrypoint restricts per-case config paths to the case folder, keeps a dry-run queue, and preserves all no-official-action flags.
- Success criteria: inbox benchmark passes, generated audit queue passes, full regression passes, and all official action/external-lawyer flags remain false.
- Stop rule: do not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-065751-inbox-to-handoff-batch`
- `benchmarks\inbox-to-handoff\` did not exist before this stage and was generated as new benchmark evidence.

Changes recorded:

- Added `scripts\orchestrate_inbox_to_handoff.py` to process an inbox of received raw-material case folders into per-case pre-submission-to-handoff outputs plus an inbox-level queue/result/report/manifest.
- Added `scripts\validate_inbox_to_handoff_benchmark.py` to revalidate every processed case, the inbox queue, batch result, report boundary text, reference-delta case presence, and top-level artifact manifest.
- Added `scripts\validate_inbox_to_handoff_rejection_benchmark.py` to prove unsafe inbox config paths, missing raw input, empty inbox, and stale output reuse are rejected before pre-submission generation.
- Updated `scripts\build_case_queue.py` and `scripts\run_case_queue.py` so `inbox-to-handoff` and `inbox-to-handoff-rejection` are discovered, queued, validated, and reported with `expected_outcome=inbox_to_handoff` or `inbox_to_handoff_rejection`.
- Added `benchmarks\inbox-to-handoff\` with two received cases: one ordinary case and one `reference_delta_source` configured case.
- Added `benchmarks\inbox-to-handoff-rejection\` with mutation cases for raw-input path traversal, reference-delta path traversal, missing raw input, empty inbox, and stale output reuse.
- Generated audit queue evidence in `out\inbox-to-handoff-queue.json`, `out\inbox-to-handoff-runner-result.json`, `out\inbox-to-handoff-rejection-queue.json`, and `out\inbox-to-handoff-rejection-runner-result.json`.
- Updated `references\workflow-orchestration.md`, `references\case-queue-batch-processor.md`, `references\production-architecture.md`, `SKILL.md`, and `test-prompts.json` to document the inbox-to-handoff production intake layer.

Verification:

- `py_compile` on the new inbox orchestrator, new validator, queue builder, and queue runner: passed.
- `python -m json.tool test-prompts.json`: passed.
- `orchestrate_inbox_to_handoff.py benchmarks\inbox-to-handoff\inbox --output-dir benchmarks\inbox-to-handoff ... --json`: passed with `summary.passed=2`, no manifest errors, and no official action/external-lawyer flags.
- `validate_inbox_to_handoff_benchmark.py benchmarks\inbox-to-handoff --json`: passed with expected source/draft support warnings only.
- `validate_artifact_hash_manifest.py benchmarks\inbox-to-handoff\artifact-hashes.json --json`: passed.
- `validate_case_queue.py benchmarks\inbox-to-handoff\case-queue.json --json`: passed.
- `validate_batch_processor_result.py benchmarks\inbox-to-handoff\batch-processor-result.json --json`: passed.
- `build_case_queue.py` for the inbox benchmark: passed with `expected_outcome=inbox_to_handoff`, `required_validators=["validate_inbox_to_handoff_benchmark"]`, AI-only legal mode, and `external_lawyer_involved=false`.
- `run_case_queue.py out\inbox-to-handoff-queue.json --output out\inbox-to-handoff-runner-result.json --json`: passed with `summary.passed=1`, no official action flags, and next action limited to read-only handoff evidence.
- `validate_case_queue.py out\inbox-to-handoff-queue.json --json`: passed.
- `validate_batch_processor_result.py out\inbox-to-handoff-runner-result.json --json`: passed.
- `validate_inbox_to_handoff_rejection_benchmark.py benchmarks\inbox-to-handoff-rejection --json`: passed with expected base inbox warnings only.
- `validate_artifact_hash_manifest.py benchmarks\inbox-to-handoff-rejection\artifact-hashes.json --json`: passed.
- `build_case_queue.py` for the inbox rejection benchmark: passed with `expected_outcome=inbox_to_handoff_rejection`, `required_validators=["validate_inbox_to_handoff_rejection_benchmark"]`, AI-only legal mode, and `external_lawyer_involved=false`.
- `run_case_queue.py out\inbox-to-handoff-rejection-queue.json --output out\inbox-to-handoff-rejection-runner-result.json --json`: passed with `summary.passed=1`, no official action flags, and next action limited to keeping unsafe inbox inputs blocked.
- `validate_case_queue.py out\inbox-to-handoff-rejection-queue.json --json`: passed.
- `validate_batch_processor_result.py out\inbox-to-handoff-rejection-runner-result.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=74 failed=0`, `artifact_manifests.total=172 failed=0`, `source_compile.total=111 failed=0`, `json_parse.total=741 failed=0`, `yaml_parse.total=133 failed=0`, `structured_sha256_placeholders.total=812 failed=0`, `structured_dangerous_true_fields.total=812 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 06:52 +08:00

Karpathy preflight:

- Assumptions: the full local pre-submission pipeline and read-only handoff package each validate independently; the remaining non-submission product gap is a one-command offline chain that produces both without creating hash self-reference or status escalation.
- Smallest sufficient action: add a thin `pre_submission_to_handoff` orchestrator and validator, register it with queue/build/regression gates, and generate only the normal plus reference-delta benchmark evidence.
- Evidence check: the wrapper validator must re-run the nested pre-submission validator and handoff validator, recompute source pre-submission, lifecycle trace, handoff package, and manifest hashes, preserve AI-only legal mode, and preserve reference-delta hash/count/boundary fields when present.
- Jagged-intelligence check: AI can confuse handoff readiness with adapter execution or official filing; the wrapper, queue decision, and next action keep status at `approved_for_adapter_execution` and state that adapter execution, receipt capture, and application-number evidence remain separate gates.
- Success criteria: both wrapper benchmarks pass, queue/batch consumption passes, full regression passes, and all official action/external-lawyer flags remain false.
- Stop rule: do not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-064454-pre-submission-to-handoff-orchestrator`
- The two `benchmarks\pre-submission-to-handoff*` folders did not exist before this stage and were generated as new benchmark evidence.

Changes recorded:

- Added `scripts\orchestrate_pre_submission_to_handoff.py` to run the full local pre-submission pipeline and then prepare a read-only handoff package in one offline command.
- Added `scripts\validate_pre_submission_to_handoff_benchmark.py` to validate nested pipeline, nested handoff package, wrapper result, source pre-submission hash, lifecycle trace hash, handoff package hash, optional reference-delta preservation, and top-level manifest.
- Updated `scripts\build_case_queue.py` and `scripts\run_case_queue.py` so `pre-submission-to-handoff` and `pre-submission-to-handoff-reference-delta` are discovered, queued, validated, and reported with `expected_outcome=pre_submission_to_handoff`.
- Generated `benchmarks\pre-submission-to-handoff\` and `benchmarks\pre-submission-to-handoff-reference-delta\`.
- Generated queue evidence in `out\pre-submission-to-handoff-queue.json` and `out\pre-submission-to-handoff-runner-result.json`.
- Updated `references\workflow-orchestration.md`, `references\case-queue-batch-processor.md`, `SKILL.md`, and `test-prompts.json` to document the one-command pre-submission-to-handoff path.

Verification:

- `py_compile` on the new wrapper, new validator, queue builder, and queue runner: passed.
- `python -m json.tool test-prompts.json`: passed.
- `orchestrate_pre_submission_to_handoff.py` normal benchmark generation: passed with `ok=true`, no manifest errors, and no official action/external-lawyer flags.
- `orchestrate_pre_submission_to_handoff.py --reference-delta-source ...` benchmark generation: passed with `ok=true`, no manifest errors, and no official action/external-lawyer flags.
- `validate_pre_submission_to_handoff_benchmark.py benchmarks\pre-submission-to-handoff --json`: passed with expected source/draft support warnings only.
- `validate_pre_submission_to_handoff_benchmark.py benchmarks\pre-submission-to-handoff-reference-delta --json`: passed with expected source/draft support warnings only.
- `validate_artifact_hash_manifest.py` on both new top-level manifests: passed.
- `build_case_queue.py` for both new wrapper benchmarks: passed with `required_validators=["validate_pre_submission_to_handoff_benchmark"]`, AI-only legal mode, and `external_lawyer_involved=false`.
- `run_case_queue.py out\pre-submission-to-handoff-queue.json --output out\pre-submission-to-handoff-runner-result.json --json`: passed with `summary.passed=2`, no official action flags, and next action limited to read-only handoff as adapter execution input evidence.
- `validate_case_queue.py out\pre-submission-to-handoff-queue.json --json`: passed.
- `validate_batch_processor_result.py out\pre-submission-to-handoff-runner-result.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=72 failed=0`, `artifact_manifests.total=137 failed=0`, `source_compile.total=108 failed=0`, `json_parse.total=595 failed=0`, `yaml_parse.total=109 failed=0`, `structured_sha256_placeholders.total=644 failed=0`, `structured_dangerous_true_fields.total=644 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 06:37 +08:00

Karpathy preflight:

- Assumptions: the read-only handoff package now passes positive validation, but production-grade workflow needs negative proof that forged or corrupted handoff packages are blocked before adapter execution.
- Smallest sufficient action: add a focused rejection benchmark for handoff package mutations, register it with queue/build/regression gates, and keep all mutation checks local.
- Evidence check: lifecycle hash mismatch, official-action flag mutation, missing filing-adapter request evidence role, copied lifecycle evidence tamper, and reference-delta boundary mutation must all fail with expected errors.
- Jagged-intelligence check: AI can over-trust a consolidated package or crash on malformed copied JSON; the handoff validator now reports corrupted lifecycle/application-material JSON as validation errors instead of throwing.
- Success criteria: rejection benchmark passes, queue/batch consumption passes, full regression passes, and all official action/external-lawyer flags remain false.
- Stop rule: do not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-063000-pre-submission-handoff-rejection-gate`

Changes recorded:

- Added `scripts\validate_pre_submission_handoff_rejection_benchmark.py`.
- Added `benchmarks\pre-submission-handoff-rejection\` with mutation cases for lifecycle hash mismatch, official submission flag mutation, missing filing-adapter request evidence role, copied lifecycle evidence tamper, and reference-delta boundary mutation.
- Hardened `scripts\validate_pre_submission_handoff_package.py` so corrupted copied lifecycle/application-materials JSON returns validation errors instead of crashing.
- Updated `scripts\build_case_queue.py` and `scripts\run_case_queue.py` so the handoff rejection benchmark is discovered, queued, and reported.
- Updated `references\workflow-orchestration.md`, `references\case-queue-batch-processor.md`, `SKILL.md`, and `test-prompts.json` to document the handoff rejection gate.
- Generated queue evidence in `out\pre-submission-handoff-rejection-queue.json` and `out\pre-submission-handoff-rejection-runner-result.json`.

Verification:

- `validate_pre_submission_handoff_rejection_benchmark.py benchmarks\pre-submission-handoff-rejection --json`: passed with expected source pre-submission warnings only.
- `validate_artifact_hash_manifest.py benchmarks\pre-submission-handoff-rejection\artifact-hashes.json --json`: passed.
- `py_compile` on handoff validator, handoff rejection validator, queue builder, and queue runner: passed.
- `build_case_queue.py` for the handoff rejection benchmark: passed with `expected_outcome=pre_submission_handoff_rejection`, `required_validators=["validate_pre_submission_handoff_rejection_benchmark"]`, AI-only legal mode, and `external_lawyer_involved=false`.
- `run_case_queue.py out\pre-submission-handoff-rejection-queue.json --output out\pre-submission-handoff-rejection-runner-result.json --json`: passed with `summary.passed=1` and no official action flags.
- `validate_case_queue.py out\pre-submission-handoff-rejection-queue.json --json`: passed.
- `validate_batch_processor_result.py out\pre-submission-handoff-rejection-runner-result.json --json`: passed.
- `python -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=70 failed=0`, `artifact_manifests.total=104 failed=0`, `source_compile.total=106 failed=0`, `json_parse.total=458 failed=0`, `yaml_parse.total=85 failed=0`, `structured_sha256_placeholders.total=483 failed=0`, `structured_dangerous_true_fields.total=483 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 06:29 +08:00

Karpathy preflight:

- Assumptions: a case that has passed the local pre-submission pipeline still needs a single read-only execution handoff package before any adapter execution; the handoff package must not itself execute, submit, pay, sign, capture a receipt, or create an application number.
- Smallest sufficient action: add a generator and validator for `pre-submission-handoff-package`, copy only the key final package/application-materials/official-ready/approved-adapter/lifecycle/receipt-plan/audit/docket evidence, and register the package with queue/build/regression gates.
- Evidence check: the handoff validator must re-run the source pre-submission validator, recompute copied evidence hashes, require the lifecycle gate/hash, preserve AI-only legal mode, and enforce reference-delta hash/count/boundary fields when present.
- Jagged-intelligence check: AI can confuse a consolidated handoff package with actual official submission; the package/report/runner next action explicitly say it is read-only and leaves adapter execution, receipt capture, and application-number evidence as separate gates.
- Success criteria: normal and reference-delta handoff packages generate and validate, queue/batch consumption passes, full regression passes, and all official action/external-lawyer flags remain false.
- Stop rule: do not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-062000-pre-submission-handoff-package`
- Key edited scripts/docs were backed up there; the two `benchmarks\pre-submission-handoff-package*` folders did not exist before this stage and were generated as new benchmark evidence.

Changes recorded:

- Added `scripts\prepare_pre_submission_handoff_package.py` to create a read-only handoff package from a passed pre-submission pipeline, copying final official documents, application materials, official preflight, receipt plan, approved-adapter preflight/request, lifecycle trace, audit plan, docket plan, and optional reference-delta evidence.
- Added `scripts\validate_pre_submission_handoff_package.py` to revalidate the source pre-submission pipeline, recompute copied evidence hashes, enforce lifecycle hash binding, AI-only legal mode, read-only controls, and reference-delta hash/count/boundary preservation.
- Updated `scripts\build_case_queue.py` and `scripts\run_case_queue.py` so handoff packages are discovered, queued, validated, and reported with a handoff-specific next action.
- Generated `benchmarks\pre-submission-handoff-package\` and `benchmarks\pre-submission-handoff-package-reference-delta\`.
- Generated queue evidence in `out\pre-submission-handoff-package-queue.json` and `out\pre-submission-handoff-package-runner-result.json`.
- Updated `references\workflow-orchestration.md`, `references\filing-execution-boundary.md`, `references\case-queue-batch-processor.md`, `SKILL.md`, and `test-prompts.json` to document the read-only pre-submission handoff package.

Verification:

- `py_compile` on handoff generator/validator, queue builder, and queue runner: passed.
- `prepare_pre_submission_handoff_package.py benchmarks\pre-submission-pipeline --output-dir benchmarks\pre-submission-handoff-package --json`: passed with expected source pre-submission warnings only.
- `prepare_pre_submission_handoff_package.py benchmarks\pre-submission-pipeline-reference-delta --output-dir benchmarks\pre-submission-handoff-package-reference-delta --json`: passed with expected source pre-submission warnings only.
- `validate_pre_submission_handoff_package.py` on both handoff benchmark folders: passed.
- `validate_artifact_hash_manifest.py` on both handoff package manifests: passed.
- `build_case_queue.py` for both handoff package folders: passed with `expected_outcome=pre_submission_handoff_package`, `required_validators=["validate_pre_submission_handoff_package"]`, AI-only legal mode, and `external_lawyer_involved=false`.
- `run_case_queue.py out\pre-submission-handoff-package-queue.json --output out\pre-submission-handoff-package-runner-result.json --json`: passed with `summary.passed=2`, read-only next actions, and no official action flags.
- `validate_case_queue.py out\pre-submission-handoff-package-queue.json --json`: passed.
- `validate_batch_processor_result.py out\pre-submission-handoff-package-runner-result.json --json`: passed.
- `python -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=69 failed=0`, `artifact_manifests.total=103 failed=0`, `source_compile.total=105 failed=0`, `json_parse.total=456 failed=0`, `yaml_parse.total=85 failed=0`, `structured_sha256_placeholders.total=483 failed=0`, `structured_dangerous_true_fields.total=483 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 06:17 +08:00

Karpathy preflight:

- Assumptions: pre-submission pipeline now reaches `approved_for_adapter_execution`, but that status should be gated by an explicit lifecycle audit trace rather than by nested stage success alone.
- Smallest sufficient action: generate a pre-submission `case-lifecycle-trace/`, validate it, bind `lifecycle_trace_hash`, make the top-level validator enforce `pre_submission_lifecycle_gate=passed`, and prove queue/batch runner consumption through `validate_pre_submission_pipeline_benchmark`.
- Evidence check: lifecycle trace hash must match the actual trace file, preserve AI-only legal metadata, preserve reference-delta metadata when present, and keep all official action flags false.
- Jagged-intelligence check: AI workflows can accidentally treat "approved for adapter execution" as a submission permission; the lifecycle gate and queue next-action wording keep adapter execution and automatic submission out of scope.
- Success criteria: both pre-submission benchmarks pass, nested lifecycle benchmarks pass, queue/batch result consumes the strengthened validator, full regression passes, and no official action or external-lawyer path appears.
- Stop rule: do not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-060601-pre-submission-lifecycle-hard-gate`

Changes recorded:

- Updated `scripts\orchestrate_pre_submission_pipeline.py` to generate `case-lifecycle-trace/`, validate it, bind `lifecycle_trace_hash`, emit `pre_submission_lifecycle_gate`, include lifecycle evidence in the report, and include the nested lifecycle manifest in the top-level artifact manifest.
- Updated `scripts\validate_pre_submission_pipeline_benchmark.py` to validate the nested lifecycle folder, recompute `lifecycle_trace_hash`, require `pre_submission_lifecycle_gate=passed`, and enforce reference-delta/application-material hash preservation in lifecycle metadata when present.
- Updated `scripts\run_case_queue.py` so pre-submission queue results keep next action gated on the lifecycle audit gate before any approved-adapter execution handoff.
- Regenerated `benchmarks\pre-submission-pipeline\` and `benchmarks\pre-submission-pipeline-reference-delta\` with lifecycle trace artifacts.
- Generated queue evidence in `out\pre-submission-lifecycle-hard-gate-queue.json` and `out\pre-submission-lifecycle-hard-gate-runner-result.json`.
- Updated `references\workflow-orchestration.md`, `references\case-lifecycle-trace.md`, `SKILL.md`, and `test-prompts.json` to document the pre-submission lifecycle hard gate and queue/batch consumption.
- Removed temporary staging output and generated `scripts\__pycache__`.

Verification:

- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline --json`: passed with expected source/draft support warnings only.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline-reference-delta --json`: passed with expected source/draft support warnings only.
- `validate_case_lifecycle_benchmark.py benchmarks\pre-submission-pipeline\case-lifecycle-trace --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\pre-submission-pipeline-reference-delta\case-lifecycle-trace --json`: passed.
- `validate_artifact_hash_manifest.py` on both regenerated pre-submission top-level manifests: passed.
- `build_case_queue.py` for both pre-submission benchmarks: passed with `required_validators=["validate_pre_submission_pipeline_benchmark"]`, AI-only legal mode, and `external_lawyer_involved=false`.
- `run_case_queue.py out\pre-submission-lifecycle-hard-gate-queue.json --output out\pre-submission-lifecycle-hard-gate-runner-result.json --json`: passed with `summary.passed=2`, lifecycle-gated next actions, and no official action flags.
- `validate_case_queue.py out\pre-submission-lifecycle-hard-gate-queue.json --json`: passed.
- `validate_batch_processor_result.py out\pre-submission-lifecycle-hard-gate-runner-result.json --json`: passed.
- `python -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=67 failed=0`, `artifact_manifests.total=101 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=433 failed=0`, `yaml_parse.total=75 failed=0`, `structured_sha256_placeholders.total=450 failed=0`, `structured_dangerous_true_fields.total=450 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 06:02 +08:00

Karpathy preflight:

- Assumptions: reference-delta metadata already flows through application-number mock evidence; lifecycle trace and production evidence gate are audit/validation layers only and must not perform official filing.
- Smallest sufficient action: add conditional reference-delta consistency checks to lifecycle and production-evidence validators, generate one lifecycle reference-delta benchmark, and update docs/prompts.
- Evidence check: reference-delta metadata must preserve `application_materials_hash`, `reference_patent_delta_hash`, positive row/claim-element counts, and `reference_delta_boundary_preserved=true` across legal authorization, official-ready, approved-adapter, adapter execution, receipt, and application-number evidence.
- Jagged-intelligence check: AI can drop provenance at audit boundaries or mistake reference patents for applicant support; validators now keep reference patents as boundary evidence only and reject mismatched downstream metadata.
- Success criteria: lifecycle reference-delta benchmark passes, production official evidence gate passes with shape-test warning only, full regression passes, official-system and submission flags remain false, and no external lawyer path appears.
- Stop rule: do not log in, upload, sign, pay, submit, capture a real receipt, claim a real application number, or treat benchmark/shape-test evidence as production official evidence.

Backup:

- `<skill-root>\backups\20260603-054231-lifecycle-production-reference-delta-gate`

Changes recorded:

- Updated `scripts\prepare_case_lifecycle_trace.py` with `--reference-delta` support for the AI self-filing lifecycle generator and trace/report metadata propagation.
- Updated `scripts\validate_case_lifecycle_trace.py` and `scripts\validate_case_lifecycle_benchmark.py` to enforce conditional reference-delta and application-materials hash preservation.
- Updated `scripts\validate_production_official_evidence_gate.py` and `scripts\validate_production_official_evidence_gate_benchmark.py` to enforce cross-artifact reference-delta consistency when present.
- Updated `scripts\validate_adapter_execution_result.py` so production-shape tests do not compare reference-delta fields against an unloaded approved-preflight file while production/file-backed validation remains strict.
- Registered `benchmarks\ai-self-filing-lifecycle-trace-reference-delta\` in `scripts\build_case_queue.py`.
- Generated `benchmarks\ai-self-filing-lifecycle-trace-reference-delta\`.
- Updated `benchmarks\production-official-evidence-gate\production-shape\` and its `artifact-hashes.json` to include reference-delta shape-test metadata.
- Updated `references\case-lifecycle-trace.md`, `references\production-official-evidence-gate.md`, `SKILL.md`, and `test-prompts.json`.
- Regenerated `out\regression-gate\` and removed generated `scripts\__pycache__`.

Verification:

- `prepare_case_lifecycle_trace.py --route ai_self_filing_no_external_lawyer --reference-delta --output-dir benchmarks\ai-self-filing-lifecycle-trace-reference-delta --json`: `ok=true`, `official_system_touched=false`, `official_submission_performed=false`.
- `validate_case_lifecycle_benchmark.py benchmarks\ai-self-filing-lifecycle-trace-reference-delta --json`: passed.
- `validate_production_official_evidence_gate_benchmark.py benchmarks\production-official-evidence-gate --json`: passed with expected `production_shape_test_not_real_official_evidence` warning.
- `validate_artifact_hash_manifest.py benchmarks\production-official-evidence-gate\artifact-hashes.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\ai-self-filing-lifecycle-trace-reference-delta\artifact-hashes.json --json`: passed.
- `python -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=67 failed=0`, `artifact_manifests.total=99 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=429 failed=0`, `yaml_parse.total=75 failed=0`, `structured_sha256_placeholders.total=446 failed=0`, `structured_dangerous_true_fields.total=446 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Confirmed no `scripts\__pycache__` remains.

## 2026-06-03 05:37 +08:00

Karpathy preflight:

- Assumptions: reference-delta submitted-pending and receipt/application-number mock evidence are local benchmark artifacts; they prove evidence-shape handling only and do not prove any real official filing event.
- Smallest sufficient action: propagate reference-delta metadata through receipt capture and application-number acceptance processors/validators, add two focused reference-delta benchmarks, and keep ordinary benchmarks compatible.
- Evidence check: receipt source/YAML/status/report and application-number source/evidence/status/report must preserve `application_materials_hash`, `reference_patent_delta_hash`, positive row/claim-element counts, and `reference_delta_boundary_preserved=true` when the upstream state carries them.
- Jagged-intelligence check: AI can accidentally treat reference patents as receipt or application-number evidence; reports now state the reference delta remains boundary and claim-strategy evidence only.
- Success criteria: new and old receipt/application-number benchmarks pass, full regression passes, generator official-action flags stay false, and no external-lawyer path appears.
- Stop rule: do not execute an adapter, log in, upload, sign, pay, submit, capture a real receipt, or claim a real application number.

Backup:

- `<skill-root>\backups\20260603-053500-reference-delta-receipt-application-number-binding`

Changes recorded:

- Updated `scripts\prepare_receipt_capture.py` to inherit reference-delta metadata from submitted-pending evidence and write it into receipt source, receipt YAML, filing status, and report.
- Updated `scripts\validate_receipt_capture_benchmark.py` and `scripts\validate_generated_receipt_capture_benchmark.py` to enforce conditional reference-delta preservation across receipt artifacts.
- Updated `scripts\prepare_application_number_acceptance.py` to inherit reference-delta metadata from receipt evidence/status and write it into application-number source, evidence, filing status, and report.
- Updated `scripts\validate_application_number_benchmark.py` and `scripts\validate_generated_application_number_benchmark.py` to enforce conditional reference-delta preservation across application-number artifacts.
- Registered `benchmarks\ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta\` and `benchmarks\ai-self-filing-official-receipt-to-application-number-reference-delta\` in `scripts\build_case_queue.py`.
- Added the two new reference-delta receipt/application-number benchmarks.
- Updated `references\application-number-evidence.md`, `SKILL.md`, and `test-prompts.json`.
- Regenerated `out\regression-gate\` and removed generated `scripts\__pycache__`.

Verification:

- `py_compile` on touched receipt/application-number scripts: passed.
- `json.tool test-prompts.json`: passed.
- `prepare_receipt_capture.py benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta ... --output-dir benchmarks\ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta --json`: passed with generator official-action flags false.
- `prepare_application_number_acceptance.py benchmarks\ai-self-filing-submitted-pending-receipt-to-official-receipt-reference-delta ... --output-dir benchmarks\ai-self-filing-official-receipt-to-application-number-reference-delta --json`: passed with generator official-action flags false.
- New and old `validate_generated_receipt_capture_benchmark.py` runs: passed.
- New and old `validate_generated_application_number_benchmark.py` runs: passed, with expected mock application-number warnings.
- New reference-delta receipt/application-number artifact manifests: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: passed with folder validators `66/66`, artifact manifests `98/98`, source compile `103/103`, JSON parse `427/427`, YAML parse `75/75`, structured sha256 placeholder scan `444/444`, structured dangerous-true scan `444/444`, forbidden scans `2/2`, `official_system_touched=false`, `official_submission_performed=false`, and `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 05:27 +08:00

Karpathy preflight:

- Assumptions: reference-delta approved-adapter preflight now validates; the next evidence-only downstream step should preserve the same delta metadata when independently supplied adapter execution evidence is converted to `submitted_pending_receipt`.
- Smallest sufficient action: update the adapter execution evidence processor and validators, add one reference-delta mock benchmark, and keep the ordinary adapter-execution benchmark compatible.
- Evidence check: result, response, status, audit input hashes, and report must preserve `application_materials_hash`, `reference_patent_delta_hash`, positive row/claim-element counts, and `reference_delta_boundary_preserved=true` when the approved preflight contains reference delta.
- Jagged-intelligence check: AI can confuse mock evidence that claims official submission with generator-side official action; the generated artifacts keep generator official-action flags false and continue to mark benchmark evidence as mock.
- Success criteria: new and old adapter-execution benchmarks pass, no receipt/application number appears, full regression passes, and external-lawyer/official-generator flags remain false.
- Stop rule: do not execute an adapter, log in, upload, sign, pay, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-052900-reference-delta-adapter-execution-binding`

Changes recorded:

- Updated `scripts\prepare_adapter_execution_result.py` to propagate reference-delta application-materials metadata into adapter execution result, filing-adapter response, filing status, audit input hashes, and report when present in the approved-adapter preflight.
- Updated `scripts\validate_adapter_execution_result.py`, `scripts\validate_adapter_execution_benchmark.py`, and `scripts\validate_filing_adapter_contract.py` to enforce reference-delta preservation only when a reference delta exists.
- Registered `benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta\` in `scripts\build_case_queue.py`.
- Added `benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta\` generated from the reference-delta approved-adapter preflight plus mock adapter execution evidence.
- Updated `references\adapter-execution-result.md`, `SKILL.md`, and `test-prompts.json`.
- Regenerated `out\regression-gate\` and removed generated `scripts\__pycache__`.

Verification:

- `py_compile` on touched adapter-execution scripts: passed.
- `json.tool test-prompts.json`: passed.
- `prepare_adapter_execution_result.py benchmarks\ai-self-filing-approved-adapter-preflight-reference-delta benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta\adapter-execution-source.json --output-dir benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta --json`: passed with generator official-action flags false.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt-reference-delta --json`: passed with expected mock/receipt-followup warnings.
- Old `benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt` validator: passed with expected mock/receipt-followup warnings.
- `run_regression_gate.py --output-dir out\regression-gate --json`: passed with folder validators `64/64`, artifact manifests `96/96`, source compile `103/103`, JSON parse `419/419`, YAML parse `73/73`, structured sha256 placeholder scan `434/434`, structured dangerous-true scan `434/434`, forbidden scans `2/2`, `official_system_touched=false`, `official_submission_performed=false`, and `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 05:19 +08:00

Karpathy preflight:

- Assumptions: the reference-delta application-materials chain already validates, but official-ready and approved-adapter stages needed explicit preservation of the same reference-patent delta evidence when present.
- Smallest sufficient action: bind reference-delta metadata through official-ready and approved-adapter outputs, add two focused benchmarks, keep ordinary no-reference-delta benchmarks compatible, and regenerate the end-to-end reference-delta pre-submission benchmark.
- Evidence check: validators must compare local file hashes, require exact lowercase `sha256:<64 hex>` fields, and prove `reference_delta_boundary_preserved=true` only when `reference_patent_delta_hash` exists.
- Jagged-intelligence check: AI is likely to over-propagate ordinary application-material hashes as if they were reference-delta evidence, so validators now make the reference-delta gate conditional on the actual delta hash.
- Success criteria: old and new official-ready/approved-adapter benchmarks pass; pre-submission reference-delta passes; full regression passes with official-action and external-lawyer flags false.
- Stop rule: do not execute an adapter, log in, upload, sign, pay, submit, capture a receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-050453-reference-delta-official-ready-adapter-binding`
- The backup includes touched scripts, docs, `WORKLOG.md`, the prior `benchmarks\pre-submission-pipeline-reference-delta\`, and the prior `out\regression-gate\` evidence bundle.

Changes recorded:

- Updated `scripts\prepare_ready_for_authorized_filing.py` to carry application-materials reference-delta hash/count/boundary metadata into official preflight, filing status, and readiness report when present.
- Updated `scripts\validate_ready_for_authorized_filing_benchmark.py` to require matching reference-delta metadata in official-ready artifacts.
- Updated `scripts\prepare_approved_adapter_preflight.py` to carry application-materials hash and reference-delta metadata into approved preflight, adapter request, filing status, audit inputs, and boundary report when present.
- Narrowed `scripts\validate_approved_adapter_preflight.py`, `scripts\validate_filing_adapter_contract.py`, and `scripts\validate_approved_adapter_benchmark.py` so ordinary application-material hashes stay compatible, while reference-delta hashes trigger strict preservation checks.
- Updated `scripts\validate_generated_approved_adapter_preflight_benchmark.py` and `scripts\build_case_queue.py` for the new reference-delta official-ready and approved-adapter benchmark coverage.
- Added `benchmarks\ai-self-filing-official-ready-reference-delta\` and `benchmarks\ai-self-filing-approved-adapter-preflight-reference-delta\`.
- Regenerated `benchmarks\pre-submission-pipeline-reference-delta\` so the full local pre-submission chain includes the stronger official-ready and approved-adapter reference-delta bindings.
- Updated `SKILL.md`, `references\ready-for-authorized-filing.md`, `references\approved-adapter-preflight.md`, and `test-prompts.json`.
- Regenerated `out\regression-gate\` and removed generated `scripts\__pycache__`.

Verification:

- `py_compile` on touched scripts: passed.
- `json.tool test-prompts.json`: passed.
- `prepare_ready_for_authorized_filing.py benchmarks\ai-self-filing-package-reference-delta ... --output-dir benchmarks\ai-self-filing-official-ready-reference-delta --json`: passed.
- `validate_ready_for_authorized_filing_benchmark.py benchmarks\ai-self-filing-official-ready-reference-delta --json`: passed.
- `prepare_approved_adapter_preflight.py benchmarks\ai-self-filing-official-ready-reference-delta benchmarks\ai-self-filing-package-reference-delta ... --output-dir benchmarks\ai-self-filing-approved-adapter-preflight-reference-delta --json`: passed.
- `validate_generated_approved_adapter_preflight_benchmark.py benchmarks\ai-self-filing-approved-adapter-preflight-reference-delta --json`: passed.
- Old `benchmarks\ai-self-filing-official-ready` and `benchmarks\ai-self-filing-approved-adapter-preflight` validators: passed.
- `orchestrate_pre_submission_pipeline.py ... --reference-delta-source benchmarks\reference-patent-delta\reference-delta-source.json --output-dir benchmarks\pre-submission-pipeline-reference-delta --case-id CASE-PRE-SUB-REF-001 --json`: passed.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline-reference-delta --json`: passed, with existing draft-support/source-manifest warnings only.
- `run_regression_gate.py --output-dir out\regression-gate --json`: passed with folder validators `63/63`, artifact manifests `95/95`, source compile `103/103`, JSON parse `414/414`, YAML parse `70/70`, structured sha256 placeholder scan `426/426`, structured dangerous-true scan `426/426`, forbidden scans `2/2`, `official_system_touched=false`, `official_submission_performed=false`, and `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 05:01 +08:00

Karpathy preflight:

- Assumptions: the downstream package/materials reference-delta chain is green; the full pre-submission pipeline still needs an explicit optional entrypoint for cited patents so raw-intake-to-approved-adapter-preflight runs can preserve the same boundary evidence end to end.
- Smallest sufficient action: add `--reference-delta-source` to the existing pre-submission orchestrator, create one new benchmark, and keep the default pipeline unchanged when the option is absent.
- Evidence check: the optional stage must generate `reference-patent-delta/`, pass its validator, feed the generated delta into draft generation, and preserve `reference_patent_delta_hash` through provenance, abnormal-risk, AI self-filing source, application materials, and the top-level result.
- Jagged-intelligence check: AI can generate a good reference-delta artifact but lose the applicant support files after copying it into the draft package; the draft generator now copies and de-duplicates reference-delta support files into the output package.
- Best-team lens: patent operations wants cited patents turned into boundary strategy before drafting; platform reliability wants the whole pre-submission pipeline to prove that strategy survived without enabling upload, signing, payment, submission, receipt, or application-number claims.
- Success criteria: old pre-submission benchmark, new reference-delta pre-submission benchmark, draft package old/new benchmarks, artifact manifests, source compile, JSON parsing, and full regression all pass with official-action/external-lawyer flags false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-045237-reference-delta-pre-submission-pipeline`

Changes recorded:

- Updated `scripts\orchestrate_pre_submission_pipeline.py` with optional `--reference-delta-source`.
- Added `materialize_reference_delta_source(...)` so the pipeline rewrites the reference-delta case ID and copies applicant support files into the local reference-delta stage before validation.
- Propagated reference-delta metadata into generated AI self-filing source materialization and top-level pre-submission result/report when present.
- Updated `scripts\generate_draft_package.py` to copy and de-duplicate reference-delta applicant support files into draft-package outputs so copied `reference-patent-delta.json` remains locally valid.
- Updated `scripts\validate_pre_submission_pipeline_benchmark.py` to validate optional `reference-patent-delta/`, require reference-delta hash presence in result/source/report, and preserve ordinary pre-submission benchmark compatibility.
- Registered `pre-submission-pipeline-reference-delta` in `scripts\build_case_queue.py`.
- Added `benchmarks\pre-submission-pipeline-reference-delta\` generated from raw pre-submission inputs plus `benchmarks\reference-patent-delta\reference-delta-source.json`.
- Updated `SKILL.md`, `references\workflow-orchestration.md`, and `test-prompts.json` to document the optional reference-delta pre-submission path.
- Removed generated `scripts\__pycache__`.

Verification:

- `orchestrate_pre_submission_pipeline.py ... --reference-delta-source benchmarks\reference-patent-delta\reference-delta-source.json --output-dir benchmarks\pre-submission-pipeline-reference-delta --case-id CASE-PRE-SUB-REF-001 --json`: passed.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline-reference-delta --json`: passed, with existing draft-support/source-manifest warnings only.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline --json`: passed, with existing warnings only.
- `validate_draft_package_generation_benchmark.py benchmarks\draft-package-generation --json`: passed.
- `validate_draft_package_generation_benchmark.py benchmarks\draft-package-reference-delta --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\pre-submission-pipeline-reference-delta\artifact-hashes.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\pre-submission-pipeline-reference-delta\draft-package-generation\artifact-hashes.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\pre-submission-pipeline-reference-delta\reference-patent-delta\artifact-hashes.json --json`: passed.
- `python -X utf8 -m py_compile scripts\generate_draft_package.py scripts\orchestrate_pre_submission_pipeline.py scripts\validate_pre_submission_pipeline_benchmark.py scripts\build_case_queue.py`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=61 failed=0`, `artifact_manifests.total=93 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=406 failed=0`, `yaml_parse.total=66 failed=0`, `structured_sha256_placeholders.total=414 failed=0`, `structured_dangerous_true_fields.total=414 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Cleanup check: `scripts\__pycache__` absent; backup folder present.

## 2026-06-03 04:50 +08:00

Karpathy preflight:

- Assumptions: the reference-patent delta has already been validated through draft generation, evidence provenance, and G8 abnormal-filing risk; downstream AI self-filing and application-materials stages must preserve that boundary evidence instead of reinterpreting reference patents as applicant support or filing authorization.
- Smallest sufficient action: add conditional reference-delta binding to the existing AI self-filing package and application-materials paths, plus three focused benchmarks for package, materials, and pipeline.
- Evidence check: downstream outputs must preserve the same `reference_patent_delta_hash`, `reference_delta_rows_count`, `reference_delta_claim_elements_count`, and `reference_delta_boundary_preserved=true` when the abnormal-risk assessment includes a reference delta.
- Jagged-intelligence check: AI can pass a prior-stage boundary check and still drop or blur that evidence later; cross-checking provenance and abnormal-risk summaries prevents a plausible final package from losing the anti-copying boundary.
- Best-team lens: patent operations keeps the prior-art/design-around story separate from applicant support; platform reliability makes the separation hash-bound through package validation, material generation, and quality-gate pipeline regression.
- Success criteria: old and new AI self-filing package benchmarks, old and new application-materials benchmarks, old and new pipeline benchmarks, source compilation, JSON parsing, artifact manifests, and full regression all pass with official-action/external-lawyer flags false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-044200-reference-delta-ai-package-materials-binding`

Changes recorded:

- Updated `scripts\prepare_ai_self_filing_package.py` to enrich abnormal-risk assessment references with reference-delta hash/count/boundary fields and render a Reference Delta Boundary report section.
- Updated `scripts\validate_ai_self_filing_authorization.py` and `scripts\validate_ai_self_filing_package_benchmark.py` so a packet cannot drop reference-delta metadata when the abnormal-risk artifact contains it.
- Updated `scripts\prepare_patent_application_materials.py` to carry reference-delta metadata into the document-generation plan, `evidence_provenance`, `abnormal_filing_risk_assessment`, and the application-materials report.
- Updated `scripts\validate_patent_application_materials.py` and `scripts\validate_patent_application_materials_benchmark.py` to require matching reference-delta hash/count/boundary fields across provenance and abnormal-risk summaries when present.
- Registered `ai-self-filing-package-reference-delta`, `ai-self-filing-application-materials-reference-delta`, and `application-materials-pipeline-reference-delta` in `scripts\build_case_queue.py`.
- Added generated benchmark folders for the three reference-delta downstream stages.
- Updated `SKILL.md`, `references\ai-self-filing-gate.md`, `references\application-materials-generation.md`, and `test-prompts.json` to document downstream reference-delta preservation.
- Removed generated `scripts\__pycache__`.

Verification:

- `validate_ai_self_filing_authorization.py benchmarks\ai-self-filing-package-reference-delta\ai-self-filing-source.json --json`: passed.
- `prepare_ai_self_filing_package.py benchmarks\draft-package-reference-delta benchmarks\ai-self-filing-package-reference-delta\ai-self-filing-source.json --output-dir benchmarks\ai-self-filing-package-reference-delta --json`: passed.
- `validate_ai_self_filing_package_benchmark.py benchmarks\ai-self-filing-package-validation --json`: passed.
- `validate_ai_self_filing_package_benchmark.py benchmarks\ai-self-filing-package-reference-delta --json`: passed.
- `prepare_patent_application_materials.py benchmarks\ai-self-filing-package-reference-delta --draft-package-dir benchmarks\draft-package-reference-delta --provenance-dir benchmarks\draft-reference-delta-evidence-provenance --output-dir benchmarks\ai-self-filing-application-materials-reference-delta --json`: passed.
- `validate_patent_application_materials.py benchmarks\ai-self-filing-application-materials-reference-delta\application-materials.json --json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials-reference-delta --json`: passed.
- `orchestrate_application_materials_pipeline.py benchmarks\ai-self-filing-package-reference-delta --draft-package-dir benchmarks\draft-package-reference-delta --provenance-dir benchmarks\draft-reference-delta-evidence-provenance --output-dir benchmarks\application-materials-pipeline-reference-delta --json`: passed.
- `validate_application_materials_pipeline_benchmark.py benchmarks\application-materials-pipeline --json`: passed.
- `validate_application_materials_pipeline_benchmark.py benchmarks\application-materials-pipeline-reference-delta --json`: passed.
- `validate_application_materials_quality_benchmark.py benchmarks\application-materials-pipeline-reference-delta\application-materials-quality-gate --json`: passed.
- New benchmark artifact manifests for package, materials, and pipeline all passed.
- `python -X utf8 -m py_compile` on the touched scripts: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=60 failed=0`, `artifact_manifests.total=79 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=350 failed=0`, `yaml_parse.total=59 failed=0`, `structured_sha256_placeholders.total=351 failed=0`, `structured_dangerous_true_fields.total=351 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Cleanup check: `scripts\__pycache__` absent; backup folder present.

## 2026-06-03 04:39 +08:00

Karpathy preflight:

- Assumptions: the abnormal-filing-risk gate must preserve `reference-patent-delta.json` as boundary and claim-strategy evidence only; it must not turn reference patents into applicant claim support, novelty guarantees, attorney review, authorization, or official filing evidence.
- Smallest sufficient action: extend the existing abnormal filing risk assessment to copy, validate, hash-bind, and report optional reference-delta evidence when present in a provenance package, plus add one focused benchmark.
- Evidence check: the gate must prove the delta hash/counts survive into `abnormal-filing-risk-assessment.json`, the copied delta still validates, and `reference_delta_boundary_preserved` passes without adding any official action or external-lawyer route.
- Jagged-intelligence check: AI can correctly draft around reference patents and still later blur the line between "distinguishing from prior art" and "supporting applicant claims"; this check keeps the boundary machine-verifiable.
- Best-team lens: patent operations checks abnormal-filing narratives and claim-support boundaries, while platform reliability checks artifact hashes, source copies, and regression registration.
- Success criteria: new reference-delta abnormal-risk benchmark, old abnormal-risk benchmark, assessment validator, artifact hash manifest, JSON prompt parsing, registered full regression, and no official-system/lawyer/submission flags.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-044000-reference-delta-abnormal-risk-binding`

Changes recorded:

- Updated `scripts\prepare_abnormal_filing_risk_assessment.py` to detect optional `reference-patent-delta.json`, validate it, copy its source/support files, preserve its hash/count metadata, and include a report section for the reference-delta boundary.
- Added `reference_delta_boundary_preserved` to the abnormal-filing risk checks when a reference delta is present.
- Updated `scripts\validate_abnormal_filing_risk_assessment.py` to validate reference-delta hash shape, positive row/element counts, and the required boundary check.
- Updated `scripts\validate_abnormal_filing_risk_benchmark.py` to validate copied reference deltas and require report/assessment evidence only for delta-bearing benchmarks.
- Added `benchmarks\abnormal-filing-risk-reference-delta\` generated from `benchmarks\draft-reference-delta-evidence-provenance\`.
- Registered `abnormal-filing-risk-reference-delta` in `scripts\build_case_queue.py` so full regression validates it.
- Updated `SKILL.md`, `references\draft-package-generation.md`, and `test-prompts.json` to document the reference-delta abnormal-risk binding.
- Removed generated `scripts\__pycache__`.

Verification:

- `prepare_abnormal_filing_risk_assessment.py benchmarks\draft-reference-delta-evidence-provenance --output-dir benchmarks\abnormal-filing-risk-reference-delta --json`: passed with official-action, official-submission, and external-lawyer flags false.
- `python -X utf8 -m py_compile scripts\prepare_abnormal_filing_risk_assessment.py scripts\validate_abnormal_filing_risk_assessment.py scripts\validate_abnormal_filing_risk_benchmark.py scripts\build_case_queue.py`: passed.
- `validate_abnormal_filing_risk_benchmark.py benchmarks\abnormal-filing-risk-reference-delta --json`: passed, with existing draft-support warnings only.
- `validate_abnormal_filing_risk_benchmark.py benchmarks\abnormal-filing-risk-gate --json`: passed, with existing draft-support warnings only.
- `validate_abnormal_filing_risk_assessment.py benchmarks\abnormal-filing-risk-reference-delta\abnormal-filing-risk-assessment.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\abnormal-filing-risk-reference-delta\artifact-hashes.json --json`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=57 failed=0`, `artifact_manifests.total=74 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=325 failed=0`, `yaml_parse.total=58 failed=0`, `structured_sha256_placeholders.total=325 failed=0`, `structured_dangerous_true_fields.total=325 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Cleanup check: `scripts\__pycache__` absent; backup folder present.

## 2026-06-03 04:31 +08:00

Karpathy preflight:

- Assumptions: once a draft consumes `reference-patent-delta.json`, downstream evidence provenance must preserve that delta as claim-strategy boundary evidence while continuing to prove applicant-owned evidence is the only claim support.
- Smallest sufficient action: extend draft evidence provenance to copy, validate, and hash-bind `reference-patent-delta.json` when present, plus add a dedicated benchmark.
- Evidence check: provenance must contain `reference_patent_delta_hash`, reference-delta row/count metadata, copied source/support files needed for independent validation, and a report section describing the boundary.
- Jagged-intelligence check: AI may correctly use reference deltas during drafting but lose the delta artifact before provenance; hash binding prevents that silent evidence break.
- Best-team lens: patent ops preserves the claim-strategy record, while platform reliability preserves reproducible paths and hashes for every artifact used to shape claim scope.
- Success criteria: new delta-bound provenance benchmark, old provenance benchmark, reference-delta validation, artifact manifests, JSON parsing, registered regression validator, and full regression all pass with official-action/external-lawyer flags false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-043000-reference-delta-provenance-binding`

Changes recorded:

- Updated `scripts\prepare_draft_evidence_provenance.py` to validate, copy, and hash-bind `reference-patent-delta.json` when present in a draft package.
- Added copying of reference-delta source/support files so the copied delta can still independently validate inside the provenance benchmark folder.
- Updated `draft-evidence-provenance.json` output to include `reference_patent_delta_hash`, `reference_delta_claim_elements_count`, and `reference_delta_rows_count` when a delta is present.
- Updated `scripts\validate_draft_evidence_provenance.py` and `scripts\validate_draft_evidence_provenance_benchmark.py` to validate optional reference-delta binding.
- Added `benchmarks\draft-reference-delta-evidence-provenance\` generated from `benchmarks\draft-package-reference-delta\`.
- Registered `draft-reference-delta-evidence-provenance` in `scripts\build_case_queue.py` so full regression validates it.
- Updated `SKILL.md`, `references\draft-package-generation.md`, and `test-prompts.json` to document the reference-delta provenance requirement.
- Removed generated `scripts\__pycache__`.

Verification:

- `prepare_draft_evidence_provenance.py benchmarks\draft-package-reference-delta benchmarks\draft-evidence-provenance-gate\source-material-manifest.yaml --output-dir benchmarks\draft-reference-delta-evidence-provenance --json`: passed.
- `python -X utf8 -m py_compile scripts\prepare_draft_evidence_provenance.py scripts\validate_draft_evidence_provenance.py scripts\validate_draft_evidence_provenance_benchmark.py scripts\build_case_queue.py`: passed.
- `validate_draft_evidence_provenance_benchmark.py benchmarks\draft-reference-delta-evidence-provenance --json`: passed.
- `validate_draft_evidence_provenance_benchmark.py benchmarks\draft-evidence-provenance-gate --json`: passed.
- `validate_reference_patent_delta.py benchmarks\draft-reference-delta-evidence-provenance\reference-patent-delta.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\draft-reference-delta-evidence-provenance\artifact-hashes.json --json`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=56 failed=0`, `artifact_manifests.total=73 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=318 failed=0`, `yaml_parse.total=57 failed=0`, `structured_sha256_placeholders.total=317 failed=0`, `structured_dangerous_true_fields.total=317 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 04:23 +08:00

Karpathy preflight:

- Assumptions: a reference-patent delta is not enough if it stays as a standalone report; claim drafting must consume the validated delta rows while preserving applicant evidence as the only claim-support source.
- Smallest sufficient action: add optional `--reference-delta` support to the draft generator, bind the validated delta into the draft package, and add a regression benchmark proving the draft and claim-support map use the delta rows.
- Evidence check: `reference-patent-delta.json` must validate, its case ID must match the disclosure, and the generated claim-support map must contain specific distinguishing features instead of generic prior-art placeholders.
- Jagged-intelligence check: AI can generate a plausible prior-art report but ignore it during claim drafting; the benchmark now fails if the draft package does not actually consume the delta.
- Best-team lens: a strong patent drafting team turns closest-reference analysis into claim architecture and fallback positions, while a strong platform team makes that transformation observable and testable.
- Success criteria: old draft benchmark, new reference-delta-bound draft benchmark, reference-delta validation, artifact manifests, JSON parsing, registered regression validator, and full regression all pass with official-action/external-lawyer flags false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-042300-draft-reference-delta-binding`

Changes recorded:

- Updated `scripts\generate_draft_package.py` with optional `--reference-delta` support.
- The draft generator now validates `reference-patent-delta.json`, requires the reference delta case ID to match the disclosure, copies/binds the delta into the output package, and uses its claim elements, distinguishing features, technical-effect evidence, claim strategies, and fallback positions in the draft and claim-support map.
- Updated `scripts\validate_draft_package_generation_benchmark.py` to validate embedded reference deltas and reject draft packages that still use generic prior-art comparison placeholders when a delta is supplied.
- Added `benchmarks\draft-package-reference-delta\` with applicant evidence, reference-delta source, generated reference delta, delta-bound draft, claim-support map, filing status, report, and hash manifest.
- Registered `draft-package-reference-delta` in `scripts\build_case_queue.py` so full regression validates it.
- Updated `SKILL.md`, `references\draft-package-generation.md`, `references\patent-generation-engine.md`, and `test-prompts.json` to document the delta-bound draft route.
- Removed generated `scripts\__pycache__`.

Verification:

- `prepare_reference_patent_delta.py benchmarks\draft-package-reference-delta\reference-delta-source.json --output-dir benchmarks\draft-package-reference-delta --json`: passed.
- `generate_draft_package.py benchmarks\draft-package-generation\invention-disclosure.json --output-dir benchmarks\draft-package-reference-delta --source-manifest invention-disclosure.json --reference-delta benchmarks\draft-package-reference-delta\reference-patent-delta.json --json`: passed.
- `python -X utf8 -m py_compile scripts\generate_draft_package.py scripts\validate_draft_package_generation_benchmark.py scripts\build_case_queue.py`: passed.
- `validate_draft_package_generation_benchmark.py benchmarks\draft-package-reference-delta --json`: passed, with three delta-bound draft claim rows.
- `validate_draft_package_generation_benchmark.py benchmarks\draft-package-generation --json`: passed.
- `validate_reference_patent_delta.py benchmarks\draft-package-reference-delta\reference-patent-delta.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\draft-package-reference-delta\artifact-hashes.json --json`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=55 failed=0`, `artifact_manifests.total=72 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=312 failed=0`, `yaml_parse.total=56 failed=0`, `structured_sha256_placeholders.total=310 failed=0`, `structured_dangerous_true_fields.total=310 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 04:12 +08:00

Karpathy preflight:

- Assumptions: cited patents should become a structured prior-art boundary and claim-strategy input, not a substitute for applicant evidence or a basis for patentability guarantees.
- Smallest sufficient action: add a local `reference-patent-delta` generator and validator with a benchmark based on the 13 cited CN publications.
- Evidence check: every proposed claim element must bind to applicant-owned local evidence by exact hash and every element must have a delta row against cited references.
- Jagged-intelligence check: AI can imitate similar patent wording or overclaim novelty; the gate rejects reference materials as applicant support and rejects novelty/patentability guarantee flags.
- Best-team lens: patent strategy teams use cited patents to map negative space and fallback ladders, while platform reliability teams require file-bound evidence and explicit no-filing boundaries.
- Success criteria: generator, validator, benchmark mutation tests, artifact manifests, JSON parsing, registered regression validator, and full regression all pass with official-action/external-lawyer flags false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-041000-reference-patent-delta-gate`

Changes recorded:

- Added `scripts/prepare_reference_patent_delta.py` to generate `reference-patent-delta.json`, `claim-strategy.md`, `reference-patent-delta-report.md`, and `artifact-hashes.json` from a cited-patent source package.
- Added `scripts/validate_reference_patent_delta.py` to validate cited CN publications, applicant-owned claim-element support files/hashes, per-element delta rows, no reference/prior-art support, no novelty/patentability guarantee, and no official action.
- Added `scripts/validate_reference_patent_delta_benchmark.py` with rejection coverage for missing delta rows, reference material used as claim support, novelty-guarantee claims, and source hash mismatch.
- Added `benchmarks\reference-patent-delta\` with the 13 cited CN publications, applicant evidence, generated delta package, claim strategy, report, and hash manifest.
- Registered `reference-patent-delta` in `scripts/build_case_queue.py` so full regression validates it.
- Updated `SKILL.md`, `references\patent-generation-engine.md`, `references\patent-workflows.md`, and `test-prompts.json` so cited patent sets now route through the reference-patent delta gate before claim drafting.
- Removed generated `scripts\__pycache__`.

Verification:

- `prepare_reference_patent_delta.py benchmarks\reference-patent-delta\reference-delta-source.json --output-dir benchmarks\reference-patent-delta --json`: passed.
- `python -X utf8 -m py_compile scripts\prepare_reference_patent_delta.py scripts\validate_reference_patent_delta.py scripts\validate_reference_patent_delta_benchmark.py scripts\build_case_queue.py`: passed.
- `validate_reference_patent_delta.py benchmarks\reference-patent-delta\reference-patent-delta.json --json`: passed.
- `validate_reference_patent_delta_benchmark.py benchmarks\reference-patent-delta --json`: passed, including missing-row, reference-support, novelty-guarantee, and source-hash rejection checks.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\reference-patent-delta\artifact-hashes.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=54 failed=0`, `artifact_manifests.total=71 failed=0`, `source_compile.total=103 failed=0`, `json_parse.total=307 failed=0`, `yaml_parse.total=56 failed=0`, `structured_sha256_placeholders.total=305 failed=0`, `structured_dangerous_true_fields.total=305 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 04:04 +08:00

Karpathy preflight:

- Assumptions: the application-materials quality review is only strong enough for official preflight if its dimension scores are derived from fixed evidence checks, not editable JSON claims.
- Smallest sufficient action: make the quality-review validator require exact expected check IDs for each dimension, reject duplicate or missing checks, and recompute each dimension score from `passed` checks.
- Evidence check: the existing generator already emits these check IDs; the change should harden validation and add rejection coverage without regenerating positive material artifacts.
- Jagged-intelligence check: an AI system can preserve a valid materials hash while forging quality-review scores or omitting hard checks; score recomputation closes that gap.
- Best-team lens: combine patent-ops rubric discipline with platform-style tamper resistance: every quality score must be traceable to a named check before official preflight can proceed.
- Success criteria: quality-review validator, quality benchmark mutation tests, nested application-materials pipeline, pre-submission pipeline, and full regression all pass with official-action/external-lawyer flags false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-040400-quality-review-check-id-score-binding`

Changes recorded:

- Updated `scripts/validate_application_materials_quality_review.py` to require exact expected check IDs per quality dimension, reject duplicate or missing IDs, and recompute each dimension score from the check pass/fail values.
- Updated `scripts/validate_application_materials_quality_benchmark.py` with missing-check and forged-score rejection mutations.
- Updated `SKILL.md`, `references\application-materials-generation.md`, and `test-prompts.json` so the quality gate contract requires exact check IDs and recomputed dimension scores.
- Removed generated `scripts\__pycache__`.

Verification:

- `python -X utf8 -m py_compile scripts\validate_application_materials_quality_review.py scripts\validate_application_materials_quality_benchmark.py`: passed.
- `validate_application_materials_quality_review.py benchmarks\application-materials-quality-gate\application-materials-quality-review.json --json`: passed.
- `validate_application_materials_quality_benchmark.py benchmarks\application-materials-quality-gate --json`: passed, including missing-check and forged-score rejection coverage.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `validate_application_materials_pipeline_benchmark.py benchmarks\application-materials-pipeline --json`: passed.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline --json`: passed.
- `validate_application_materials_quality_review.py benchmarks\pre-submission-pipeline\application-materials-pipeline\application-materials-quality-gate\application-materials-quality-review.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=53 failed=0`, `artifact_manifests.total=70 failed=0`, `source_compile.total=100 failed=0`, `json_parse.total=304 failed=0`, `yaml_parse.total=56 failed=0`, `structured_sha256_placeholders.total=302 failed=0`, `structured_dangerous_true_fields.total=302 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 03:59 +08:00

Karpathy preflight:

- Assumptions: after official-channel readiness is green, the next local non-submission step is approved-adapter preflight packaging; adapter execution, official login, upload, signature, payment, submission, receipt capture, and application-number capture remain out of scope.
- Smallest sufficient action: extend the existing pre-submission orchestrator to materialize an approved-adapter source, run `prepare_approved_adapter_preflight.py`, and stop at `approved_for_adapter_execution`.
- Evidence check: `prepare_approved_adapter_preflight.py` already validates ready status, validated package evidence, production adapter readiness, strict official session authorization, adapter request hashes, audit/docket plans, and artifact manifest.
- Jagged-intelligence check: the top-level pipeline now records `adapter_execution_performed=false` so approval-for-execution cannot be mistaken for actual execution.
- Best-team lens: treat this like a mature patent-ops release gate: the AI team produces a complete, auditable pre-execution packet while platform controls keep execution and official-system actions outside the one-click pipeline.
- Success criteria: top-level pre-submission validator, nested approved-adapter validator, queue dry-run, manifest checks, and full regression all pass with official-action/external-lawyer/adapter-execution/automatic-submission flags false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-035300-pre-submission-approved-adapter-preflight`

Changes recorded:

- Updated `scripts/orchestrate_pre_submission_pipeline.py` to generate `ai-self-filing-approved-adapter-preflight/approved-adapter-source.json`, run `prepare_approved_adapter_preflight.py`, and include `ai_self_filing_approved_adapter_preflight` in the full pre-submission chain.
- Updated the top-level pre-submission result to end at `approved_for_adapter_execution` with `decision=approved_for_adapter_execution_no_auto_submit`.
- Added top-level `adapter_execution_performed=false` to result and response payloads, and made the report explicitly state adapter execution was not performed.
- Updated `scripts/validate_pre_submission_pipeline_benchmark.py` to validate the nested approved-adapter stage, approved-adapter source case/status binding, `adapter_execution_performed=false`, and report boundary text.
- Updated `SKILL.md`, `references/workflow-orchestration.md`, and `test-prompts.json` so docs and prompt expectations match the new endpoint and no-execution invariant.
- Regenerated `benchmarks/pre-submission-pipeline/` with official-ready plus approved-adapter preflight stages included.
- Removed generated `scripts\__pycache__` and temporary queue-check output.

Verification:

- `orchestrate_pre_submission_pipeline.py ... --json`: passed with `status=approved_for_adapter_execution`, `official_system_touched=false`, `official_submission_performed=false`, `adapter_execution_performed=false`, `external_lawyer_involved=false`, and `automatic_submission_performed=false`.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline --json`: passed.
- `validate_generated_approved_adapter_preflight_benchmark.py benchmarks\pre-submission-pipeline\ai-self-filing-approved-adapter-preflight --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\pre-submission-pipeline\artifact-hashes.json --json`: passed.
- Queue dry-run from `benchmarks\pre-submission-pipeline`: passed with `decision=pre_submission_pipeline_passed`, `current_status=approved_for_adapter_execution`, `target_status=approved_for_adapter_execution`, `generator_adapter_execution_performed=false`, and no official action.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `python -X utf8 -m py_compile scripts\orchestrate_pre_submission_pipeline.py scripts\validate_pre_submission_pipeline_benchmark.py`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=53 failed=0`, `artifact_manifests.total=70 failed=0`, `source_compile.total=100 failed=0`, `json_parse.total=304 failed=0`, `yaml_parse.total=56 failed=0`, `structured_sha256_placeholders.total=302 failed=0`, `structured_dangerous_true_fields.total=302 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 03:51 +08:00

Karpathy preflight:

- Assumptions: after the full pre-submission pipeline generates application materials and quality review, the remaining non-submission local step is official-channel preflight readiness. Automatic submission, official login, upload, signature, payment, receipt capture, and application-number capture remain out of scope.
- Smallest sufficient action: extend the existing pre-submission orchestrator to materialize an official-preflight source, run `prepare_ready_for_authorized_filing.py`, and stop at `ready_for_authorized_filing` without adapter execution.
- Evidence check: `prepare_ready_for_authorized_filing.py` already validates the package, AI self-filing authorization, application-materials path/hash, official-channel preflight source, receipt-capture plan, filing status transition, and artifact manifest.
- Jagged-intelligence check: the new official-preflight source must bind to the freshly generated `application-materials.json`; stale benchmark hashes cannot be reused after regenerating the full pipeline.
- Best-team lens: treat official readiness as a controlled docket state, not a submission. The pipeline prepares auditable handoff evidence like a mature patent operations team, but preserves platform-style action boundaries: no external lawyer, no official-system touch, no automatic submit.
- Success criteria: pre-submission pipeline reaches `ready_for_authorized_filing`, nested official-ready validator passes, queue status remains ready without submission, full regression remains green, and official-action/external-lawyer/automatic-submission flags stay false.
- Stop rule: do not execute an approved adapter, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number.

Backup:

- `<skill-root>\backups\20260603-034400-pre-submission-official-ready`

Changes recorded:

- Updated `scripts/orchestrate_pre_submission_pipeline.py` to generate `ai-self-filing-official-ready/official-preflight-source.json`, run `prepare_ready_for_authorized_filing.py`, and include `ai_self_filing_official_ready` as the final local pre-submission stage.
- Updated the top-level pre-submission result to end at `ready_for_authorized_filing` with `decision=ready_for_authorized_filing_no_auto_submit`.
- Added optional `--official-preflight-source-template` support while keeping the repo benchmark template as the default.
- Updated `scripts/validate_pre_submission_pipeline_benchmark.py` to validate the nested official-ready stage, official-preflight source application-materials path/hash binding, ready status, and no-auto-submit decision.
- Updated `scripts/build_case_queue.py` and `scripts/run_case_queue.py` so pre-submission queue items preserve the `ready_for_authorized_filing` status and next action stays at approved-adapter preflight or authorized handoff only.
- Updated `SKILL.md`, `references/workflow-orchestration.md`, and `test-prompts.json` to document the new endpoint and invariants.
- Regenerated `benchmarks/pre-submission-pipeline/` with the official-ready stage included.

Verification:

- `py_compile scripts\orchestrate_pre_submission_pipeline.py scripts\validate_pre_submission_pipeline_benchmark.py scripts\build_case_queue.py scripts\run_case_queue.py`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `orchestrate_pre_submission_pipeline.py ... --output-dir benchmarks\pre-submission-pipeline --json`: passed with `ok=true`, `status=ready_for_authorized_filing`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`, and `automatic_submission_performed=false`.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline --json`: passed; warnings are expected for prior-art material not usable as claim support and draft-only claim-support rows.
- `validate_ready_for_authorized_filing_benchmark.py benchmarks\pre-submission-pipeline\ai-self-filing-official-ready --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\pre-submission-pipeline\artifact-hashes.json --json`: passed.
- Queue integration check: `build_case_queue.py` inferred `expected_outcome=pre_submission_pipeline` with current/target status `ready_for_authorized_filing`; `run_case_queue.py` returned `pre_submission_pipeline_passed` and kept official-system/submission/generator action flags false.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=53 failed=0`, `artifact_manifests.total=69 failed=0`, `source_compile.total=100 failed=0`, `json_parse.total=299 failed=0`, `yaml_parse.total=54 failed=0`, `structured_sha256_placeholders.total=295 failed=0`, `structured_dangerous_true_fields.total=295 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 03:43 +08:00

Karpathy preflight:

- Assumptions: the user wants every local step before automatic submission completed, while automatic submission, official login, upload, signature, payment, receipt capture, and application-number capture remain out of scope for this step.
- Smallest sufficient action: add a thin full pre-submission orchestrator that composes existing validated stages instead of rewriting intake, drafting, legal gate, package validation, materials generation, and quality review.
- Evidence check: existing stage APIs already validate case package, disclosure confirmation, draft package, evidence provenance, abnormal filing risk, AI self-filing package validation, and application-materials quality. The missing evidence was a single command proving the whole chain composes with fresh hashes.
- Jagged-intelligence check: AI can reuse stale hashes when a draft is regenerated, or let an abnormal-risk artifact path validate in one directory but fail after package copying. The new orchestrator rewrites scaffold, draft, abnormal-risk, AI legal gate, and package-source hashes at runtime and stores raw-input evidence in the top-level benchmark.
- Best-team lens: run it like a top patent operations team would run a docket SOP, like a platform reliability team would run a state machine, and like an audit team would require file-bound manifests. No persona or AI review is allowed to claim lawyer or patent-agent authority.
- Success criteria: one command creates every local pre-submission stage, every nested validator passes, queue recognition returns `pre_submission_pipeline_passed`, full regression remains green, and all official-action/external-lawyer/automatic-submission flags stay false.
- Stop rule: do not run official-channel preflight, do not log in, do not upload, do not sign, do not pay, do not submit, do not capture a receipt, and do not claim an application number from this pipeline.

Backup:

- `<skill-root>\backups\20260603-023000-pre-submission-pipeline`

Changes recorded:

- Added `scripts/orchestrate_pre_submission_pipeline.py` to run raw input copying, case packaging, disclosure scaffolding, AI-only disclosure confirmation, draft package generation, draft-evidence provenance, abnormal-filing risk assessment, AI self-filing package validation, application-materials generation, independent quality review, top-level report, and top-level artifact manifest.
- Added `scripts/validate_pre_submission_pipeline_benchmark.py` to validate every nested stage plus `pre-submission-pipeline-result.json`, `pre-submission-pipeline-report.md`, the AI self-filing source path/hash binding, and top-level `artifact-hashes.json`.
- Added `benchmarks/pre-submission-pipeline/` generated from the existing raw benchmark source files and AI-only confirmation/self-filing templates with runtime-recomputed scaffold, draft, abnormal-risk, legal-gate, package, materials, and quality hashes.
- Updated `scripts/build_case_queue.py` to register `pre-submission-pipeline`, infer `expected_outcome=pre_submission_pipeline`, and bind it to `validate_pre_submission_pipeline_benchmark`.
- Updated `scripts/run_case_queue.py` to run the new validator and return `pre_submission_pipeline_passed` while keeping official-action and generator-action flags false.
- Updated `SKILL.md`, `references/workflow-orchestration.md`, and `test-prompts.json` to document the full local pre-submission command, outputs, invariants, and benchmark expectations.

Verification:

- `py_compile scripts\orchestrate_pre_submission_pipeline.py scripts\validate_pre_submission_pipeline_benchmark.py scripts\build_case_queue.py scripts\run_case_queue.py`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `orchestrate_pre_submission_pipeline.py benchmarks\case-package-orchestration-dry-run\case-package\00-intake\source-files --confirmation-packet-template benchmarks\scaffold-confirmation-to-disclosure\disclosure-confirmation-packet.json --ai-self-filing-source-template benchmarks\ai-self-filing-package-validation\ai-self-filing-source.json --output-dir benchmarks\pre-submission-pipeline --case-id CASE-PRE-SUB-001 --received-from "Patent Capital OS benchmark" --json`: passed with `ok=true`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`, and `automatic_submission_performed=false`.
- `validate_pre_submission_pipeline_benchmark.py benchmarks\pre-submission-pipeline --json`: passed; warnings are expected for prior-art material not usable as claim support and draft-only claim-support rows.
- `validate_artifact_hash_manifest.py benchmarks\pre-submission-pipeline\artifact-hashes.json --json`: passed.
- `validate_application_materials_pipeline_benchmark.py benchmarks\pre-submission-pipeline\application-materials-pipeline --json`: passed.
- `validate_ai_self_filing_package_benchmark.py benchmarks\pre-submission-pipeline\ai-self-filing-package-validation --json`: passed.
- Queue integration check: `build_case_queue.py` inferred `expected_outcome=pre_submission_pipeline`; `run_case_queue.py` returned `pre_submission_pipeline_passed`, kept output status at `package_valid_official_preflight_pending`, and kept official-system/submission/generator action flags false.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=53 failed=0`, `artifact_manifests.total=68 failed=0`, `source_compile.total=100 failed=0`, `json_parse.total=296 failed=0`, `yaml_parse.total=52 failed=0`, `structured_sha256_placeholders.total=290 failed=0`, `structured_dangerous_true_fields.total=290 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 02:21 +08:00

Karpathy preflight:

- Assumptions: the next production-grade step is not direct official submission; it is a local, auditable pipeline that joins validated AI self-filing package evidence to generated application materials and an independent quality gate.
- Smallest sufficient action: add one orchestrator, one benchmark validator, queue recognition, documentation, and test prompt coverage without changing official submission, payment, signature, receipt, or application-number behavior.
- Evidence check: the existing validated package, draft package, draft-evidence provenance, application-materials generator, quality review generator, and artifact hash manifest validators are already green and can be composed.
- Jagged-intelligence check: AI may claim a filing-ready state too early, may trust its own generated materials, or may lose hash binding across nested outputs. The new pipeline recomputes and validates top-level and nested manifests and keeps official-channel preflight separate.
- Success criteria: pipeline generation passes, nested materials and quality validators pass, queue builder/runner identify `application_materials_pipeline`, full regression remains green, and all official-action/external-lawyer flags stay false.
- Stop rule: do not let this pipeline log in, upload, sign, pay, submit, capture receipt, claim an application number, or treat quality review as legal advice/lawyer/patent-agent review.

Backup:

- `<skill-root>\backups\20260603-021342-application-materials-pipeline`

Changes recorded:

- Added `scripts/orchestrate_application_materials_pipeline.py` to run application-materials generation plus independent quality review in one local command and write `application-materials-pipeline-result.json`, `application-materials-pipeline-report.md`, and top-level `artifact-hashes.json`.
- Added `scripts/validate_application_materials_pipeline_benchmark.py` to validate the nested application-materials folder, nested quality-gate folder, top-level pipeline result, report, and artifact manifest.
- Registered `application-materials-pipeline` in `scripts/build_case_queue.py` and `scripts/run_case_queue.py` with `expected_outcome=application_materials_pipeline`, `decision=application_materials_pipeline_passed`, and official-action flags false.
- Updated `scripts/build_case_queue.py` to create the parent directory for `--output` automatically.
- Added `benchmarks/application-materials-pipeline/` generated from the positive AI self-filing package, draft package, and draft-evidence provenance fixtures.
- Updated `SKILL.md`, `references/application-materials-generation.md`, `references/workflow-orchestration.md`, and `test-prompts.json` to document the one-command local pipeline, validation commands, queue behavior, and official-channel preflight boundary.

Verification:

- `py_compile scripts\orchestrate_application_materials_pipeline.py scripts\validate_application_materials_pipeline_benchmark.py scripts\build_case_queue.py scripts\run_case_queue.py`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `orchestrate_application_materials_pipeline.py benchmarks\ai-self-filing-package-validation --draft-package-dir benchmarks\draft-package-generation --provenance-dir benchmarks\ai-self-filing-draft-evidence-provenance --output-dir benchmarks\application-materials-pipeline --json`: passed with `ok=true`, `official_system_touched=false`, `official_submission_performed=false`, and `external_lawyer_involved=false`.
- `validate_application_materials_pipeline_benchmark.py benchmarks\application-materials-pipeline --json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\application-materials-pipeline\application-materials --json`: passed.
- `validate_application_materials_quality_benchmark.py benchmarks\application-materials-pipeline\application-materials-quality-gate --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\application-materials-pipeline\artifact-hashes.json --json`: passed.
- Queue integration check: `build_case_queue.py` inferred `expected_outcome=application_materials_pipeline`; `run_case_queue.py` returned `application_materials_pipeline_passed`, kept output status at `package_valid_official_preflight_pending`, and kept official-system/submission/generator action flags false.
- Parent directory creation check: `build_case_queue.py --output out\application-materials-pipeline-parent-autocreate-check\case-queue.json` passed without pre-creating the parent directory.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=52 failed=0`, `artifact_manifests.total=57 failed=0`, `source_compile.total=98 failed=0`, `json_parse.total=254 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=245 failed=0`, `structured_dangerous_true_fields.total=245 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 02:10 +08:00

Karpathy preflight:

- Assumptions: structure validation proves application materials are file-bound and safe-shaped, but a production-grade patent workflow still needs an independent quality gate before official-channel preflight.
- Smallest sufficient action: add a deterministic application-materials quality review generator, validator, benchmark, and queue integration without changing the official submission boundary.
- Evidence check: the existing AI self-filing application-materials benchmark already has source-bound claims, specification, abstract, drawings, request metadata, XML readiness, evidence provenance, abnormal-risk, and legal/safety flags.
- Jagged-intelligence check: AI can overrate its own drafting unless quality criteria are explicit and recomputed. The new gate separates generation from review and recomputes the reviewed `application-materials.json` hash.
- Success criteria: quality review passes on the positive benchmark, rejects hash mismatch, low dimension score, and failed gate mutations, integrates with queue build/run, full regression remains green, and official-action/external-lawyer flags stay false.
- Stop rule: do not let quality review submit, upload, sign, pay, claim legal advice, claim lawyer/patent-agent review, claim receipt, or create an application number.

Backup:

- `<skill-root>\backups\20260603-020440-application-materials-quality-gate`

Changes recorded:

- Added `scripts/prepare_application_materials_quality_review.py` to create `application-materials-quality-review.json`, `application-materials-quality-report.md`, and `artifact-hashes.json`.
- Added `scripts/validate_application_materials_quality_review.py` to recompute the reviewed application-materials hash, validate the underlying materials, enforce weighted score and per-dimension thresholds, and keep official-action/external-lawyer flags false.
- Added `scripts/validate_application_materials_quality_benchmark.py` with negative checks for application-materials hash mismatch, low claim-architecture dimension score, and failed quality gate status.
- Added `benchmarks/application-materials-quality-gate/` generated from the positive AI self-filing application-materials bundle.
- Registered `application-materials-quality-gate` in `scripts/build_case_queue.py` and added queue/runner handling for `application_materials_quality`.
- Updated `references/application-materials-generation.md`, `references/quality-rubric.md`, `SKILL.md`, and `test-prompts.json` to require the independent quality review before official-channel preflight.

Verification:

- `py_compile scripts\prepare_application_materials_quality_review.py scripts\validate_application_materials_quality_review.py scripts\validate_application_materials_quality_benchmark.py scripts\build_case_queue.py scripts\run_case_queue.py`: passed.
- JSON parsing for `benchmarks\application-materials-quality-gate\application-materials-quality-review.json`, `benchmarks\application-materials-quality-gate\artifact-hashes.json`, and `test-prompts.json`: passed.
- `prepare_application_materials_quality_review.py benchmarks\ai-self-filing-application-materials --output-dir benchmarks\application-materials-quality-gate --json`: passed.
- `validate_application_materials_quality_review.py benchmarks\application-materials-quality-gate\application-materials-quality-review.json --json`: passed.
- `validate_application_materials_quality_benchmark.py benchmarks\application-materials-quality-gate --json`: passed, including the negative checks.
- `validate_artifact_hash_manifest.py benchmarks\application-materials-quality-gate\artifact-hashes.json --json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- Queue integration check: `build_case_queue.py` inferred `expected_outcome=application_materials_quality`; `run_case_queue.py` returned `application_materials_quality_gate_passed` with official-system and submission flags false; temp queue directory was safely removed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=51 failed=0`, `artifact_manifests.total=54 failed=0`, `source_compile.total=96 failed=0`, `json_parse.total=242 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=233 failed=0`, `structured_dangerous_true_fields.total=233 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-03 02:01 +08:00

Karpathy preflight:

- Assumptions: a generated application-material file with a correct path and hash can still be useless if it only says a source-draft section was missing.
- Smallest sufficient action: add content-level checks for the four generated prose material types and prove a hash-correct placeholder file is rejected.
- Evidence check: the positive AI self-filing application-materials benchmark already contains the required Claims, Technical Problem/Solution/Detailed Embodiments, Abstract, and Brief Description Of Drawings markers.
- Jagged-intelligence check: AI can over-trust file hashes and miss that the text is a placeholder. The validator now reads generated Markdown content after hash validation.
- Success criteria: positive application materials still validate; a hash-correct missing-section placeholder material fails; temporary fixture files are cleaned; full regression remains green with no official action or external lawyer marker.
- Stop rule: do not accept filing materials that lack source-draft section markers or contain "section not found in source draft" placeholder text, and do not touch official systems, submit, sign, pay, or claim receipt/application-number evidence.

Backup:

- `<skill-root>\backups\20260603-015644-application-material-content-gate`

Changes recorded:

- Added content-level generated-document checks to `scripts/validate_patent_application_materials.py`.
- Extended `scripts/validate_patent_application_materials_rejection_benchmark.py` with safe temporary material fixtures that are written inside the materials root and removed after validation.
- Added `benchmarks/patent-application-materials-rejection/placeholder-claims-material.md` and a `placeholder_generated_claims_material_rejected` case whose path/hash are valid but content is a missing-section placeholder.
- Refreshed `benchmarks/patent-application-materials-rejection/artifact-hashes.json`.
- Updated `references/application-materials-generation.md`, `references/patent-generation-engine.md`, `SKILL.md`, and `test-prompts.json` to require source-draft section markers and reject missing-section placeholders.

Verification:

- `py_compile scripts\validate_patent_application_materials.py scripts\validate_patent_application_materials_rejection_benchmark.py`: passed.
- JSON parsing for `benchmarks\patent-application-materials-rejection\rejection-cases.json`, `benchmarks\patent-application-materials-rejection\artifact-hashes.json`, and `test-prompts.json`: passed.
- `validate_patent_application_materials.py benchmarks\ai-self-filing-application-materials\application-materials.json --json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_patent_application_materials_rejection_benchmark.py benchmarks\patent-application-materials-rejection --json`: passed, including the hash-correct placeholder material rejection.
- `validate_artifact_hash_manifest.py benchmarks\patent-application-materials-rejection\artifact-hashes.json --json`: passed.
- Temporary generation check with `prepare_patent_application_materials.py` into `out\application-material-content-gate-check`: passed and the temp directory was safely removed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=50 failed=0`, `artifact_manifests.total=53 failed=0`, `source_compile.total=93 failed=0`, `json_parse.total=240 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=231 failed=0`, `structured_dangerous_true_fields.total=231 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.

## 2026-06-03 01:53 +08:00

Karpathy preflight:

- Assumptions: the offline case queue runner must never become the real official adapter executor; it may only validate independently supplied adapter execution evidence.
- Smallest sufficient action: add a guarded `approved_adapter_evidence_mode=true` path, keep missing evidence mode rejected, and add one benchmark proving local evidence validation.
- Evidence check: no existing queue used `execution_mode=approved_adapter`, so this creates the first positive contract without altering old positive fixtures.
- Jagged-intelligence check: AI can confuse "adapter evidence says submitted" with "this runner submitted"; generator and runner action flags now stay separately false in queue results.
- Success criteria: evidence-mode queue validates supplied adapter execution evidence, non-evidence approved-adapter queues are rejected, full regression remains green, and no official system touch/submission or external lawyer marker appears.
- Stop rule: do not log in, upload, sign, pay, submit, execute an adapter, claim a receipt, claim acceptance, or create an application number from the local runner.

Backup:

- `<skill-root>\backups\20260603-014642-approved-adapter-evidence-queue`

Changes recorded:

- Added `approved_adapter_evidence_mode=true` requirements to `scripts/validate_case_queue.py` and `scripts/validate_batch_processor_result.py`.
- Updated `scripts/run_case_queue.py` so `approved_adapter` is local evidence validation only; missing evidence mode remains a batch error.
- Updated `scripts/build_case_queue.py` to register `approved-adapter-evidence-queue` and emit `approved_adapter_evidence_mode=true` when building approved-adapter evidence queues.
- Added `scripts/validate_approved_adapter_evidence_queue_benchmark.py` and `benchmarks/approved-adapter-evidence-queue/` with queue, runner result, and artifact hash manifest.
- Updated `references/case-queue-batch-processor.md`, `references/filing-adapter-interface.md`, `SKILL.md`, and `test-prompts.json` to document the evidence-only approved-adapter queue boundary.

Verification:

- `py_compile scripts\run_case_queue.py scripts\validate_case_queue.py scripts\validate_batch_processor_result.py scripts\build_case_queue.py scripts\validate_approved_adapter_evidence_queue_benchmark.py`: passed.
- JSON parsing for the new benchmark files and `test-prompts.json`: passed after rewriting `artifact-hashes.json` as UTF-8 without BOM.
- `run_case_queue.py benchmarks\approved-adapter-evidence-queue\case-queue.json --output benchmarks\approved-adapter-evidence-queue\runner-result.json --json`: passed with runner/generator official-action flags false.
- `validate_case_queue.py benchmarks\approved-adapter-evidence-queue\case-queue.json --json`: passed.
- `validate_batch_processor_result.py benchmarks\approved-adapter-evidence-queue\runner-result.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\approved-adapter-evidence-queue\artifact-hashes.json --json`: passed.
- `validate_approved_adapter_evidence_queue_benchmark.py benchmarks\approved-adapter-evidence-queue --json`: passed.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\approved-adapter-to-submitted-pending-receipt --json`: passed with expected mock/pending-receipt warnings.
- `validate_case_queue_benchmark.py benchmarks\case-queue-batch-processor --json`: passed.
- Negative checks: a queue missing `approved_adapter_evidence_mode` is rejected by both queue validation and runner; a queue targeting `official_receipt_received` is rejected before execution.
- Builder check: `build_case_queue.py --execution-mode approved_adapter` on the adapter execution evidence folder emits `approved_adapter_evidence_mode=true` and validates.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=50 failed=0`, `artifact_manifests.total=53 failed=0`, `source_compile.total=93 failed=0`, `json_parse.total=240 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=231 failed=0`, `structured_dangerous_true_fields.total=231 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- `scripts\__pycache__` was generated by compile checks, resolved inside the skill workspace, and was safely removed; final pycache scan was empty.

## 2026-06-03 01:40 +08:00

Karpathy preflight:

- Assumptions: raw intake copying is the first filesystem boundary; even if source-material manifests are safe, a raw input symlink could still cause package-external files to be copied into applicant evidence.
- Smallest sufficient action: harden only `scripts/prepare_case_package.py` source-file enumeration and copy target checks, then update the intake contracts.
- Evidence check: pre-scan of benchmark raw inputs found 0 symlinks, so rejecting linked files does not affect current positive fixtures.
- Jagged-intelligence check: AI can treat a copied file as trustworthy after hashing, but a linked raw file may make the package hash a package-external artifact. The intake copier now rejects symlinks and checks resolved source/target roots before hashing.
- Success criteria: normal raw intake still packages successfully; symlink rejection branch is proven; case package and intake orchestration benchmarks pass; full regression remains green with no official action or external lawyer marker.
- Stop rule: do not follow linked raw files, do not copy files resolving outside raw input, do not write package targets outside `00-intake/source-files`, and do not touch official systems, submit, sign, pay, or claim receipt/application-number evidence.

Backup:

- `<skill-root>\backups\20260603-013800-case-package-source-resolve-gate`

Changes recorded:

- Added `is_relative_to` and resolved source/target root checks to `scripts/prepare_case_package.py`.
- `copy_sources` now rejects symlinked raw files, source files resolving outside the raw input directory, and targets resolving outside `00-intake/source-files`.
- Updated `references/case-package-protocol.md`, `references/case-intake-orchestration.md`, `SKILL.md`, and `test-prompts.json` to require safe raw intake copying.

Verification:

- Benchmark symlink pre-scan: 0 symlinks found.
- Normal temp raw file package generation: passed and cleaned up.
- OS symlink creation attempt was blocked by Windows privileges, so a controlled monkeypatch proved `source_file_is_symlink` is rejected by `prepare_case_package.py`.
- `py_compile scripts\prepare_case_package.py`: passed.
- `validate_case_package_benchmark.py benchmarks\case-package-intake-dry-run --json`: passed.
- `validate_case_intake_orchestration_benchmark.py benchmarks\case-package-orchestration-dry-run --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=228 failed=0`, `structured_dangerous_true_fields.total=228 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Temp raw-intake test directories were absent after cleanup; final regression generated `scripts\__pycache__`, resolved path stayed inside the skill workspace, and the directory was safely removed.

## 2026-06-03 01:36 +08:00

Karpathy preflight:

- Assumptions: source-material manifests are the earliest applicant-evidence boundary; material filenames must not let a manifest reference arbitrary absolute paths or escape the case/source-material base with `..`.
- Smallest sufficient action: harden `scripts/validate_source_material_manifest.py` path resolution, update the two downstream material-file copiers to use the same safe resolver, and add rejection benchmark cases.
- Evidence check: pre-scan of current source-material manifests found 8 benchmark manifests with 0 absolute or path-traversing filenames.
- Jagged-intelligence check: AI can produce correct-looking hashes and filenames while quietly pointing outside the case package. Safe relative path checks plus hash recomputation block package-external evidence substitution before drafting.
- Success criteria: absolute and `..` material filenames are rejected; normal source manifest, case package, draft-evidence provenance, abnormal-risk, artifact manifest, and full regression checks still pass; no official action or external lawyer marker appears.
- Stop rule: do not break the standard `01-normalized` manifest-parent workflow; do not copy source files from absolute or path-traversing locations; do not touch official systems, submit, sign, pay, or claim receipt/application-number evidence.

Backup:

- `<skill-root>\backups\20260603-013401-source-material-safe-path-gate`

Changes recorded:

- Added safe material path resolution to `scripts/validate_source_material_manifest.py`; material filenames now reject absolute paths and `..`, and only the standard `01-normalized` manifest-parent fallback is allowed.
- Updated `scripts/prepare_draft_evidence_provenance.py` and `scripts/prepare_abnormal_filing_risk_assessment.py` to reuse the safe source-material resolver before copying material files.
- Added `absolute_material_path_rejected` and `traversal_material_path_rejected` to `benchmarks/source-material-file-binding-rejection/rejection-cases.json` and refreshed its `artifact-hashes.json`.
- Updated `references/case-package-protocol.md`, `SKILL.md`, and `test-prompts.json` to require safe relative source-material filenames.

Verification:

- Pre-scan: 8 benchmark source-material manifests checked, 0 unsafe filenames.
- `py_compile scripts\validate_source_material_manifest.py scripts\prepare_draft_evidence_provenance.py scripts\prepare_abnormal_filing_risk_assessment.py`: passed.
- `validate_source_material_file_binding_rejection_benchmark.py benchmarks\source-material-file-binding-rejection --json`: passed, including the new absolute-path and traversal-path rejection cases.
- `validate_source_material_manifest.py benchmarks\incoming-disclosure-to-application\source-material-manifest.yaml --json`: passed.
- `validate_case_package_benchmark.py benchmarks\case-package-intake-dry-run --json`: passed.
- `validate_draft_evidence_provenance_benchmark.py benchmarks\ai-self-filing-draft-evidence-provenance --json`: passed.
- `validate_abnormal_filing_risk_benchmark.py benchmarks\ai-self-filing-abnormal-risk-gate --json`: passed.
- `validate_abnormal_filing_risk_rejection_benchmark.py benchmarks\abnormal-filing-risk-rejection --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\source-material-file-binding-rejection\artifact-hashes.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=228 failed=0`, `structured_dangerous_true_fields.total=228 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Final source-material path scan found 0 unsafe filenames; final regression generated `scripts\__pycache__`, resolved path stayed inside the skill workspace, and the directory was safely removed.

## 2026-06-03 01:30 +08:00

Karpathy preflight:

- Assumptions: generated application-material files are local package artifacts; source package directories may legitimately point to an upstream package, but copied provenance, copied abnormal-risk evidence, request metadata, generated documents, XML readiness, and filing status should not resolve outside the materials bundle.
- Smallest sufficient action: harden `scripts/validate_patent_application_materials.py` for internal generated-artifact paths and copied evidence hashes only; leave source package directory resolution unchanged.
- Evidence check: pre-scan of the current `application-materials.json` benchmark found all internal generated paths relative, in-root, and safe.
- Jagged-intelligence check: AI can produce plausible `path/hash` pairs that reference files outside the package. Local in-root path checks plus hash recomputation make the materials bundle self-contained before official preflight.
- Success criteria: baseline materials still validate; negative in-memory mutations for absolute paths, `..` traversal, evidence hash mismatch, missing abnormal-risk file, and filing-status traversal all fail; full regression remains green with no official action or external lawyer marker.
- Stop rule: do not block the intended upstream source package reference; do not allow generated materials to escape the bundle; do not touch official systems, submit, sign, pay, or claim receipt/application-number evidence.

Backup:

- `<skill-root>\backups\20260603-012832-application-materials-internal-path-gate`

Changes recorded:

- Added `resolve_internal_artifact` and in-root path checks to `scripts/validate_patent_application_materials.py`.
- Made generated material references reject absolute paths, `..` traversal, and paths resolving outside the materials output directory.
- Added hash/file validation for copied `evidence_provenance.path` and `abnormal_filing_risk_assessment.path`.
- Updated `references/application-materials-generation.md`, `SKILL.md`, and `test-prompts.json` to require internal generated-material path binding.

Verification:

- Pre-scan: 1 application-materials benchmark checked, 0 internal path errors.
- Negative self-check: absolute document path, request metadata `..` path, evidence provenance hash mismatch, missing abnormal-risk file, and filing-status `..` path were all rejected with expected errors.
- `py_compile scripts\validate_patent_application_materials.py`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=228 failed=0`, `structured_dangerous_true_fields.total=228 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Final regression generated `scripts\__pycache__`; resolved path stayed inside the skill workspace and the directory was safely removed.

## 2026-06-03 01:26 +08:00

Karpathy preflight:

- Assumptions: `artifact-hashes.json` is the local evidence bundle trust anchor; validating content hashes alone is insufficient if a manifest can name unsafe paths, duplicate entries, malformed hash strings, or invalid byte counts.
- Smallest sufficient action: harden only `scripts/validate_artifact_hash_manifest.py` and update the regression contract references; do not alter artifact generation semantics.
- Evidence check: pre-scan of 53 current manifests found no unsafe paths, duplicate paths, malformed hashes, or invalid byte counts before the edit.
- Jagged-intelligence check: AI can produce convincing audit manifests with correct-looking fields but brittle path and hash shapes. The validator now rejects malformed evidence before any package can treat it as reliable.
- Success criteria: targeted negative manifests fail for absolute paths, `..` traversal, duplicate paths, bad hashes, and invalid byte counts; all current benchmark manifests and the regression evidence bundle still validate; no official action or external lawyer marker appears.
- Stop rule: do not loosen hash matching, do not allow paths outside the manifest root, and do not touch any official system, submit, sign, pay, or claim receipt/application-number evidence.

Backup:

- `<skill-root>\backups\20260603-012451-artifact-manifest-structure-gate`

Changes recorded:

- Added exact lowercase `sha256:<64 hex>` validation to `scripts/validate_artifact_hash_manifest.py`.
- Added rejection for missing/invalid paths, absolute paths, `..` traversal, resolved paths outside the manifest root, duplicate artifact paths, non-file artifacts, invalid byte counts, malformed JSON, and non-object manifests.
- Updated `references/regression-gate.md`, `SKILL.md`, and `test-prompts.json` so artifact manifest validation explicitly includes path, hash-shape, duplicate, and byte-count checks.

Verification:

- Pre-scan: 53 manifests checked, 0 structural errors.
- Negative self-check: absolute path, `..` traversal, duplicate path, bad `sha256`, and boolean `bytes` cases were all rejected with expected errors.
- `py_compile scripts\validate_artifact_hash_manifest.py`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=228 failed=0`, `structured_dangerous_true_fields.total=228 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Temp negative directory `out\artifact-manifest-negative-root`: absent after cleanup.
- Final regression generated `scripts\__pycache__`; resolved path stayed inside the skill workspace and the directory was safely removed.

## 2026-06-03 01:22 +08:00

Karpathy preflight:

- Assumptions: YAML files under `assets`, `benchmarks`, and `schemas` are structured workflow evidence or contracts; malformed YAML should fail centrally instead of surfacing late in package generation or validation.
- Smallest sufficient action: add one YAML parse check to `scripts/run_regression_gate.py`, reuse the existing structured loader, and update only the regression contract documents and prompt expectations.
- Evidence check: a manual pre-scan found 49 YAML files and 0 parse failures before the edit; the negative temp YAML self-check failed as expected after the edit.
- Jagged-intelligence check: AI often writes YAML-looking text that is brittle around indentation, list syntax, and nested values. A central parse gate catches that class of error without changing patent drafting or filing behavior.
- Success criteria: invalid YAML fails the new check, full regression reports `yaml_parse.ok=true`, the evidence manifest validates, no temp/cache residue remains, and no official action or external lawyer marker appears.
- Stop rule: do not include temporary negative fixtures in benchmark evidence; do not touch any official system, submit, sign, pay, or claim a receipt/application number.

Backup:

- `<skill-root>\backups\20260603-011934-regression-yaml-parse-gate`

Changes recorded:

- Added `run_yaml_parse` to `scripts/run_regression_gate.py`; it parses `*.yaml` and `*.yml` under `assets`, `benchmarks`, and `schemas`.
- Added the `yaml_parse` check to the regression gate output.
- Updated `references/regression-gate.md`, `SKILL.md`, and `test-prompts.json` so regression verification explicitly requires `yaml_parse.ok=true`.

Verification:

- Negative temp YAML self-check detected an invalid YAML parse error as expected.
- `py_compile scripts\run_regression_gate.py`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `yaml_parse.total=49 failed=0`, `structured_sha256_placeholders.total=228 failed=0`, `structured_dangerous_true_fields.total=228 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Temp negative directory `out\yaml-parse-negative-root`: absent after cleanup.
- Final regression generated `scripts\__pycache__`; resolved path stayed inside the skill workspace and the directory was safely removed.

## 2026-06-03 01:17 +08:00

Karpathy preflight:

- Assumptions: positive structured benchmarks should never carry generator-side official action, external-lawyer involvement, credential leakage, or official-control bypass flags as `true`; intentional rejection fixtures may contain those values only to prove validators reject them.
- Smallest sufficient action: add a structured dangerous-boolean scan to `scripts/run_regression_gate.py`, share the same intentional negative fixture exclusion used by the hash-placeholder scan, and update the regression contract.
- Evidence check: text scan found no current positive matches, but the first regression run correctly exposed intentional `unsafe-rejection` fixtures, so the exclusion rule was refined to skip paths containing rejection markers rather than weakening the dangerous-field list.
- Jagged-intelligence check: AI can easily emit plausible JSON with a dangerous `true` value in a nested field. A structured key-aware scan is more precise than broad text grep and avoids blocking deliberate rejection fixtures.
- Success criteria: in-memory negative self-check catches dangerous true fields, intentional rejection fixture paths are excluded, `structured_dangerous_true_fields.ok=true`, full regression passes, and no official action or external lawyer marker is reported.
- Stop rule: do not allow positive benchmarks to normalize generator official action, credential leakage, access-control bypass, or external-lawyer involvement; do not touch any official system.

Backup:

- `<skill-root>\backups\20260603-011447-regression-structured-dangerous-true-gate`

Changes recorded:

- Added `structured_dangerous_true_fields` to `scripts/run_regression_gate.py`; it scans positive benchmark JSON/YAML files for dangerous true booleans including generator official actions, external-lawyer involvement, credential leakage, and access-control bypass flags.
- Added `is_intentional_negative_fixture` so both structured scans exclude intentional rejection fixtures, including `unsafe-rejection`, `mock-rejection`, and other paths containing rejection markers.
- Updated `references/regression-gate.md`, `SKILL.md`, and `test-prompts.json` so regression verification explicitly requires both structured `sha256:*` placeholder and dangerous true boolean scans to pass.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- In-memory negative self-check detected `status.generator_official_system_touched=true` and `adapter.bypasses_access_controls=true`.
- Exclusion self-check confirmed intentional negative fixtures such as `unsafe-rejection` and `rejection-cases.json` are skipped.
- `py_compile scripts\run_regression_gate.py`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `structured_sha256_placeholders.total=228 failed=0`, `structured_dangerous_true_fields.total=228 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 01:12 +08:00

Karpathy preflight:

- Assumptions: top-tier IP operations and reliability teams turn repeated manual evidence checks into automated gates; relying on a remembered one-off scan would let future positive benchmarks reintroduce fake `sha256:*` evidence.
- Smallest sufficient action: add one structured benchmark hash-placeholder check to `scripts/run_regression_gate.py`, excluding intentional rejection case fixtures and leaving template placeholders alone.
- Evidence check: the previous manual scan showed positive structured benchmarks were clean after the approved-adapter plan fix; this change preserves that invariant in the regression gate itself.
- Jagged-intelligence check: AI is good at generating consistent-looking JSON/YAML, but brittle at distinguishing evidence hashes from descriptive placeholders. The regression check now fails positive structured benchmarks that contain any non-exact `sha256:*`.
- Success criteria: the new check detects a fake in-memory hash, full regression reports `structured_sha256_placeholders.ok=true`, the evidence bundle manifest validates, and no official action or external-lawyer marker appears.
- Stop rule: do not scan intentional rejection cases as failures, do not treat templates as production evidence, and do not touch any official system.

Backup:

- `<skill-root>\backups\20260603-011044-regression-structured-sha256-placeholder-gate`

Changes recorded:

- Added `structured_sha256_placeholders` to `scripts/run_regression_gate.py`; it parses positive benchmark JSON/YAML files, skips `rejection-cases.json`, and rejects any `sha256:*` string that is not exact lowercase `sha256:<64 hex>`.
- Updated `references/regression-gate.md` so the regression gate contract includes the positive structured benchmark hash-placeholder scan.
- Updated `SKILL.md` and `test-prompts.json` so regression verification explicitly requires `structured_sha256_placeholders.ok=true`.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- Negative in-memory self-check detected `sha256:not-a-real-hash` at `evidence.artifact_hash`.
- `py_compile scripts\run_regression_gate.py`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `structured_sha256_placeholders.total=241 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 01:07 +08:00

Karpathy preflight:

- Assumptions: approved-adapter audit and docket plans are pre-execution evidence plans; they should record exact upstream hashes but must not invent descriptive `sha256:*` values for downstream artifacts that are not materialized yet.
- Smallest sufficient action: remove non-exact internal audit/docket plan hashes from the old positive benchmark, harden its benchmark validator, refresh dependent preflight/request/result/lifecycle hashes, and update narrow documentation.
- Evidence check: structured hash scan found `sha256:approved-adapter-preflight-v1` and `sha256:adapter-request-v1` only in `benchmarks/approved-adapter-preflight-ready` positive plan artifacts after excluding intentional rejection cases and templates.
- Jagged-intelligence check: AI is good at making plausible audit trails, but brittle around circular hash dependencies. The corrected pattern uses exact hashes for known upstream inputs and a plain `pending` marker for downstream materialization instead of fake hashes.
- Success criteria: approved-adapter benchmark rejects fake internal plan hashes, downstream adapter-execution mock hashes align with the refreshed preflight/request, lifecycle trace hashes match referenced artifacts, full regression passes, and no positive structured benchmark has non-exact `sha256:*` placeholders.
- Stop rule: do not create circular hashes, execute an adapter, touch an official system, submit, pay, claim receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-010137-approved-adapter-plan-internal-hash-gate`

Changes recorded:

- Hardened `scripts/validate_approved_adapter_benchmark.py` to scan audit/docket plan internals for non-exact `sha256:*` strings, require expected upstream input hashes in the audit plan, allow only plain pending markers or exact hashes for docket `source_hash`, and reject pre-execution application numbers in docket plans.
- Updated `benchmarks/approved-adapter-preflight-ready/audit-log-entry-plan.yaml` to remove fake preflight/request hashes and preserve exact known upstream hashes.
- Updated `benchmarks/approved-adapter-preflight-ready/docket-entry-plan.yaml` to use `source_hash: "pending"` instead of a fake `sha256:*` value.
- Refreshed `benchmarks/approved-adapter-preflight-ready/approved-adapter-preflight.json`, `filing-adapter-request.json`, and `artifact-hashes.json` after audit/docket plan hashes changed.
- Refreshed downstream `benchmarks/adapter-execution-mock-submitted/adapter-execution-result.json`, `filing-adapter-response.json`, and `artifact-hashes.json` so request/preflight/result hashes remain consistent.
- Updated `benchmarks/case-lifecycle-trace-mock/case-lifecycle-trace.json` and its artifact manifest for the changed approved-adapter and adapter-execution stage hashes.
- Updated `references/approved-adapter-preflight.md`, `SKILL.md`, and `test-prompts.json` with the exact audit/docket plan hash rule and the non-hash `pending` marker rule.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `validate_approved_adapter_benchmark.py benchmarks\approved-adapter-preflight-ready --json`: passed.
- `validate_adapter_execution_benchmark.py benchmarks\adapter-execution-mock-submitted --json`: passed with only expected mock submission/receipt-follow-up warnings.
- `validate_case_lifecycle_benchmark.py benchmarks\case-lifecycle-trace-mock --json`: passed.
- Affected artifact manifests and `out\regression-gate\artifact-hashes.json` passed `scripts/validate_artifact_hash_manifest.py`.
- Negative mutation self-check rejected fake audit-plan sha256, fake docket source sha256, and missing audit final-package input hash.
- Positive structured benchmark scan after excluding intentional rejection cases found `count=0` non-exact `sha256:*` placeholders.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 00:57 +08:00

Karpathy preflight:

- Assumptions: ready-or-later filing statuses and official-channel preflight packets are evidence-bearing artifacts; descriptive hashes such as `sha256:filing-package-v1` can make a placeholder look like a real package hash.
- Smallest sufficient action: scan ready-or-later statuses for non-exact final/reviewed hashes, harden the shared status validator and official-channel preflight validator, replace only the two old placeholder benchmark hashes, and refresh dependent manifests.
- Evidence check: only `benchmarks/official-channel-preflight-to-ready/filing-status.json` and `benchmarks/receipt-capture-mock/filing-status.json` had non-exact ready-or-later package hashes; `official-channel-preflight.yaml` also had descriptive package and attachment hashes.
- Jagged-intelligence check: AI is good at carrying labels like "final_package_hash", but brittle at distinguishing exact hash evidence from descriptive placeholders. Shape validation now rejects placeholder hashes before readiness or receipt states can pass.
- Success criteria: no ready-or-later filing status contains non-exact final/reviewed hashes; official-channel preflight rejects descriptive package hashes; focused validators and full regression pass.
- Stop rule: do not represent benchmark-shape hashes as production file binding, official filing, receipt, acceptance, or application-number evidence.

Backup:

- `<skill-root>\backups\20260603-005314-filing-status-final-hash-shape-gate`

Changes recorded:

- Hardened `scripts/validate_filing_status_transition.py` so ready-or-later states require exact lowercase `sha256:<64 hex>` values for both `final_package_hash` and `reviewed_package_hash`.
- Hardened `scripts/validate_official_channel_preflight.py` so `package.final_package_hash`, `package.reviewed_package_hash`, and `package.attachment_list_hash` reject descriptive placeholders.
- Replaced `sha256:filing-package-v1` and `sha256:attachment-list-v1` in `benchmarks/official-channel-preflight-to-ready/official-channel-preflight.yaml` with deterministic benchmark-shape exact hashes.
- Updated `benchmarks/official-channel-preflight-to-ready/filing-status.json` and `benchmarks/receipt-capture-mock/filing-status.json` to use exact final/reviewed package hash values.
- Refreshed affected artifact manifests and updated `benchmarks/case-lifecycle-trace-mock/case-lifecycle-trace.json` because it referenced the old official preflight artifact hash.
- Updated `SKILL.md`, `references/case-processor-state-machine.md`, and `test-prompts.json` with exact hash-shape requirements.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- Ready-or-later filing-status scan found `count=0` non-exact final/reviewed package hashes after the change.
- Negative mutation self-check rejected descriptive filing-status package hashes and descriptive official-channel attachment hashes.
- `validate_filing_status_transition.py`, `validate_official_channel_preflight.py`, `validate_official_ready_benchmark.py`, `validate_receipt_capture_benchmark.py`, and `validate_case_lifecycle_benchmark.py` passed for affected benchmarks.
- Affected artifact manifests and `out\regression-gate\artifact-hashes.json` passed `scripts/validate_artifact_hash_manifest.py`.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 00:51 +08:00

Karpathy preflight:

- Assumptions: `validate_filing_status_transition.py` is the shared boundary for status truth; if it only checks state names, later stages can preserve legal gate text while losing official-action truth or AI self-filing no-external-lawyer constraints.
- Smallest sufficient action: harden the shared filing-status validator, add missing explicit official-action booleans to old benchmarks, refresh dependent hashes/lifecycle traces, and update narrow skill/reference/test-prompt wording.
- Evidence check: all current benchmark `filing-status.json` files were scanned; five statuses lacked explicit `official_system_touched`, and `authorized-cn-ready-for-filing` lacked the `official_channel_preflight=passed` field required by the shared ready-state validator.
- Jagged-intelligence check: AI is good at producing plausible lifecycle states, but brittle at distinguishing generator behavior from official evidence. The gate now separates `official_system_touched=true` evidence states from `generator_official_system_touched=false` local generation.
- Success criteria: every `filing-status.json` passes the shared transition validator; dangerous mutations are rejected; affected folder validators, lifecycle validators, artifact manifests, and full regression pass.
- Stop rule: do not touch an official system, submit, pay, sign, claim a real receipt, or claim a real application number from local generation.

Backup:

- `<skill-root>\backups\20260603-004335-filing-status-transition-legal-official-gate`

Changes recorded:

- Hardened `scripts/validate_filing_status_transition.py` to require explicit pre-official `official_system_touched=false` and `official_submission_performed=false`, post-submission `official_system_touched=true` and `official_submission_performed=true`, AI self-filing `external_lawyer_involved=false`, no generator-side official action flags, and no application number at `submitted_pending_receipt`.
- Updated `scripts/prepare_receipt_capture.py` so generated receipt-status evidence explicitly records `official_system_touched=true` while generator flags remain false.
- Updated `scripts/validate_authorized_ready_benchmark.py` so the authorized-ready benchmark calls the shared filing-status transition validator.
- Added missing status fields to `benchmarks/official-channel-preflight-to-ready`, `benchmarks/case-processor-dry-run`, `benchmarks/receipt-capture-mock`, `benchmarks/submitted-pending-receipt-to-official-receipt`, `benchmarks/ai-self-filing-submitted-pending-receipt-to-official-receipt`, and `benchmarks/authorized-cn-ready-for-filing`.
- Refreshed affected `artifact-hashes.json` entries and regenerated `benchmarks/generated-case-lifecycle-trace/*` plus `benchmarks/ai-self-filing-lifecycle-trace/*`.
- Updated `SKILL.md`, `references/case-processor-state-machine.md`, and `test-prompts.json` to document the shared status truth boundary.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- All benchmark `filing-status.json` files passed `scripts/validate_filing_status_transition.py`.
- Negative mutation self-check rejected 5 unsafe states: pre-official official-touch true, post-submission missing official-touch true, AI self-filing external lawyer true, generator official-touch true, and `submitted_pending_receipt` with an application number.
- `py_compile` passed for modified validator/generator scripts.
- Focused validators passed for authorized-ready, official-ready, case processor, receipt capture, generated receipt capture, generated lifecycle, AI self-filing lifecycle, and lifecycle rejection.
- Affected artifact manifests and `out\regression-gate\artifact-hashes.json` passed `scripts/validate_artifact_hash_manifest.py`.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 00:40 +08:00

Karpathy preflight:

- Assumptions: raw intake and disclosure scaffold are source-of-truth stages; if they do not carry AI self-filing legal metadata, later drafting, queueing, package validation, and lifecycle traces can lose the no-external-lawyer route context.
- Smallest sufficient action: add legal-gate metadata to case-package filing status and disclosure scaffold outputs, harden scaffold/intake validators, regenerate affected intake/scaffold benchmarks, and refresh lifecycle hashes that depend on intake artifacts.
- Evidence check: case package manifest already had `legal_gate_mode=ai_self_filing_no_external_lawyer` and `external_lawyer_involved=false`, but `filing-status.json`, scaffold top level, intake queue items, and batch result rows were not all validated for those fields.
- Jagged-intelligence check: AI is strong at generating structured intake artifacts, but brittle at preserving route metadata across stage boundaries; requiring the same fields in package status, scaffold, queue, result, and lifecycle evidence closes that gap.
- Success criteria: case-package intake, disclosure normalization, case-intake orchestration, generated lifecycle, and AI self-filing lifecycle benchmarks validate; full regression passes; no official action or external-lawyer true marker appears.
- Stop rule: do not allow intake or scaffold stages to draft, file, submit, sign, pay, claim receipt, or claim an application number.

Backup:

- `<skill-root>\backups\20260603-003200-intake-scaffold-legal-metadata-binding`

Changes recorded:

- Updated `scripts/prepare_case_package.py` so generated `filing-status.json` preserves `legal_gate_mode=ai_self_filing_no_external_lawyer` and `external_lawyer_involved=false` at intake.
- Updated `scripts/normalize_invention_disclosure.py` so generated scaffold top level and `scaffold_controls` preserve the same AI self-filing legal metadata while keeping filing and draft generation disabled.
- Hardened `scripts/validate_case_package_benchmark.py`, `scripts/validate_invention_disclosure_scaffold.py`, `scripts/validate_disclosure_normalization_benchmark.py`, and `scripts/validate_case_intake_orchestration_benchmark.py` to reject missing legal-gate metadata or any non-false external-lawyer marker in intake/scaffold stages.
- Updated `scripts/orchestrate_case_intake.py` to include report-level legal-gate metadata evidence without introducing old reviewed-route defaults.
- Regenerated `benchmarks/case-package-intake-dry-run/case-package/*`, `benchmarks/disclosure-normalization-scaffold/*`, and `benchmarks/case-package-orchestration-dry-run/*`.
- Regenerated `benchmarks/generated-case-lifecycle-trace/*` and `benchmarks/ai-self-filing-lifecycle-trace/*` so lifecycle stage hashes match the refreshed intake package manifest.
- Updated `references/case-package-protocol.md`, `references/case-intake-orchestration.md`, `references/disclosure-normalization.md`, `SKILL.md`, and `test-prompts.json` with the source-stage legal metadata invariants.
- Removed generated `scripts\__pycache__` and temporary regeneration directories under `out\` after validation.

Verification:

- `validate_case_package_benchmark.py benchmarks\case-package-intake-dry-run --json`: passed with only expected prior-art not-claim-support warnings.
- `validate_invention_disclosure_scaffold.py benchmarks\disclosure-normalization-scaffold\invention-disclosure-scaffold.json --json`: passed.
- `validate_disclosure_normalization_benchmark.py benchmarks\disclosure-normalization-scaffold --json`: passed.
- `validate_case_intake_orchestration_benchmark.py benchmarks\case-package-orchestration-dry-run --json`: passed with only expected prior-art not-claim-support warnings.
- `validate_case_lifecycle_benchmark.py` passed for `benchmarks\generated-case-lifecycle-trace` and `benchmarks\ai-self-filing-lifecycle-trace`.
- `validate_case_lifecycle_rejection_benchmark.py benchmarks\case-lifecycle-rejection-gate --json`: passed.
- `validate_artifact_hash_manifest.py` passed for affected intake, scaffold, lifecycle, and regression evidence-bundle manifests.
- `py_compile` for modified intake/scaffold scripts and validators: passed.
- Static scan over affected benchmarks/scripts found no true external-lawyer or official-action markers.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 00:30 +08:00

Karpathy preflight:

- Assumptions: queue builder, batch runner, and workflow orchestration are long-running entrypoints; they must carry the no-external-lawyer AI self-filing legal/compliance mode as auditable metadata, not just avoid official submission.
- Smallest sufficient action: update queue generation/result propagation, three queue-entry validators, the three queue-entry dry-run benchmarks, and narrow reference/prompt/skill wording.
- Evidence check: existing builder/workflow queue items lacked `legal_gate_mode` and `external_lawyer_involved`; validators checked official-action boundaries but did not reject missing legal-gate metadata.
- Jagged-intelligence check: AI can keep a top-level R10 route while losing legal-mode context across generated queues and batch results; explicit item/result metadata plus benchmark validation closes that handoff risk.
- Success criteria: builder, batch, and workflow dry-run queues/results preserve `legal_gate_mode=ai_self_filing_no_external_lawyer`, keep `external_lawyer_involved=false`, pass focused validators, pass artifact hash validation, and pass full regression with no official action.
- Stop rule: do not touch an official system, do not submit/sign/pay, do not claim receipt/application number, and do not reintroduce default attorney/lawyer/counsel/patent-agent review wording.

Backup:

- `<skill-root>\backups\20260603-002000-queue-legal-gate-metadata-binding`

Changes recorded:

- Updated `scripts/build_case_queue.py` to infer and write `legal_gate_mode` and `external_lawyer_involved` on generated queue items, defaulting missing cases to the AI self-filing no-external-lawyer route.
- Updated `scripts/run_case_queue.py` to preserve queue item legal-gate metadata into batch result rows.
- Updated `scripts/orchestrate_case_workflow.py` to include report-level legal-gate metadata evidence without introducing plain-text old review defaults.
- Hardened `scripts/validate_case_queue_benchmark.py`, `scripts/validate_case_queue_builder_benchmark.py`, and `scripts/validate_workflow_orchestration_benchmark.py` to reject missing `legal_gate_mode` or any non-false `external_lawyer_involved` value in the AI self-filing dry-run path.
- Regenerated `benchmarks/case-queue-builder-dry-run/generated-case-queue.json` using AI self-filing dry-run examples and updated `builder-report.md`.
- Regenerated `benchmarks/case-queue-batch-processor/case-queue.json`, `runner-result.json`, and `batch-processor-result.json` using the same no-external-lawyer AI self-filing examples; updated `batch-report.md`.
- Regenerated `benchmarks/workflow-orchestration-dry-run/case-queue.json`, `batch-processor-result.json`, `orchestration-report.md`, and `artifact-hashes.json`.
- Refreshed builder and batch artifact manifests with compatible SHA-256 generation and no BOM UTF-8 output after PowerShell `SHA256.HashData` proved unavailable in this runtime.
- Updated `references/workflow-orchestration.md`, `references/case-queue-batch-processor.md`, `SKILL.md`, and `test-prompts.json` so queue-entry workflows require legal-gate metadata and no external professional involvement on the AI self-filing path.
- Removed generated `scripts\__pycache__` after compile/regression validation.

Verification:

- `validate_case_queue.py benchmarks\case-queue-builder-dry-run\generated-case-queue.json --json`: passed.
- `validate_case_queue_builder_benchmark.py benchmarks\case-queue-builder-dry-run --json`: passed.
- `validate_case_queue_benchmark.py benchmarks\case-queue-batch-processor --json`: passed.
- `validate_workflow_orchestration_benchmark.py benchmarks\workflow-orchestration-dry-run --json`: passed.
- `py_compile` for modified queue/orchestration validators and generators: passed.
- `validate_artifact_hash_manifest.py` passed for builder, batch, workflow, and regression evidence-bundle manifests.
- Static scans over modified queue-entry benchmarks/references found no true external-lawyer or official-action markers and no old reviewed-route default trigger wording.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 00:16 +08:00

Karpathy preflight:

- Assumptions: the no-external-lawyer route is now the default path, but the legal/compliance step, applicant authorization, package hashes, and official-channel boundaries remain mandatory.
- Smallest sufficient action: update only foundational preflight, production architecture, and advisory-board wording that still implied counsel or patent-agent review as the default filing precondition.
- Evidence check: `SKILL.md` defines R10 as AI self-filing with no external lawyer, while `references/karpathy-preflight.md` and `references/production-architecture.md` still had filing preflight/state-machine wording centered on counsel review.
- Jagged-intelligence check: AI can follow a top-level R10 route but regress when lower-level preflight docs say "counsel review" as the default; the fix binds lower-level guardrails to selected legal gate mode instead.
- Success criteria: modified references have no old default counsel-review trigger wording, full regression passes, evidence-bundle hashes validate, and no official-system or external-lawyer true marker appears.
- Stop rule: do not weaken legal/compliance gates, applicant authority, filing-channel, signature, payment, receipt, or evidence-hash requirements.

Backup:

- `<skill-root>\backups\20260603-001449-foundational-ai-only-preflight-docs`

Changes recorded:

- Updated `references/karpathy-preflight.md` so filing preflight verifies the selected legal gate: validated AI self-filing legal/compliance authorization for the no-external-lawyer route, or counsel/patent-agent review only for an explicit reviewed-package route.
- Updated `references/production-architecture.md` so the drafting/legal/state-machine/hard-gate model defaults to AI self-filing authorization-ready packages and selected legal gate evidence rather than counsel review.
- Added the AI legal/compliance gate role to the production team model and made attorney/patent-agent review optional for the explicit reviewed route.
- Updated `references/advisory-board-agent-team.md` so product/persona review points at AI self-filing authorization-ready UX and replaces the previous generic legal-review decision token with `reviewed_package_gate_needed`.
- Removed generated `scripts\__pycache__` after final regression validation.

Verification:

- Focused scan over modified references found no legacy counsel-review default trigger wording.
- Focused scan over modified references found no true external-lawyer or official-action markers.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 00:10 +08:00

Karpathy preflight:

- Assumptions: batch/queue processing is the path that lets the system run for long periods without asking the user, so draft-only queue next actions must not drift back to counsel or patent-agent review by default.
- Smallest sufficient action: update only the case-queue batch reference, static benchmark result/report, validator coverage, and narrow prompt/skill text; keep official filing, adapter execution, receipt, and application-number boundaries unchanged.
- Evidence check: `case-queue-batch-processor` must validate with no old review-default wording, dry-run official actions remain false, and the artifact hash manifest must match changed files.
- Jagged-intelligence check: AI workflows can generate correct draft artifacts but later route a batch item to the wrong next action; scanning batch result, runner result, and report text closes that brittle handoff point.
- Success criteria: case queue focused validator passes, artifact manifest validates, full regression passes, scans find no old counsel/patent-agent review defaults, and no official/external-lawyer true flags appear in the batch benchmark.
- Stop rule: do not alter queue execution into real official action, do not weaken validators, and do not create submitted/receipt/application-number status from dry-run batch processing.

Backup:

- `<skill-root>\backups\20260603-001200-case-queue-ai-only-default`

Changes recorded:

- Updated `references/case-queue-batch-processor.md` so `draft_package` means AI self-filing legal/compliance authorization artifacts, not counsel review.
- Updated `benchmarks/case-queue-batch-processor/batch-processor-result.json` and `batch-report.md` so the draft-only case next action is AI self-filing legal/compliance authorization plus applicant/package gates.
- Hardened `scripts/validate_case_queue_benchmark.py` to scan batch result, runner result, and batch report for old attorney/lawyer/counsel/patent-agent default review wording.
- Updated `SKILL.md` and `test-prompts.json` so queue benchmarks require draft-only next actions to stay on the AI self-filing legal/compliance authorization path.
- Recomputed `benchmarks/case-queue-batch-processor/artifact-hashes.json`.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `validate_case_queue_benchmark.py benchmarks\case-queue-batch-processor --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\case-queue-batch-processor\artifact-hashes.json --json`: passed.
- `python -X utf8 -m py_compile scripts\validate_case_queue_benchmark.py`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Static scans over `benchmarks\case-queue-batch-processor` and `references\case-queue-batch-processor.md` found no old counsel/patent-agent review defaults.
- Static scan found no `external_lawyer_involved=true`, `official_submission_performed=true`, or `official_system_touched=true` in the batch benchmark; residual `__pycache__` scan found no directories after cleanup.

## 2026-06-03 00:06 +08:00

Karpathy preflight:

- Assumptions: `incoming-disclosure-to-application` is the first static benchmark for "received materials become patent draft materials" and therefore must follow the no-external-lawyer AI self-filing default path; the separate counsel/agent reviewed package route remains valid only when explicitly supplied.
- Smallest sufficient action: remove legacy counsel-ready defaults from the incoming-disclosure benchmark, harden only its validator, refresh directly affected hash manifests, and update the narrow patent-generation reference wording.
- Evidence check: the incoming benchmark must use `ai_legal_compliance_questions`, `Draft status: ai_self_filing_authorization_needed`, `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, `official_system_touched=false`, and no official submission.
- Jagged-intelligence check: AI can generate plausible drafts while leaving old legal-review affordances in headings, status, source manifests, and lifecycle traces; the validator and lifecycle hash refresh close that brittle point.
- Success criteria: incoming benchmark validator passes, lifecycle trace mock hashes are refreshed, full regression passes, artifact-hash manifests validate, and scans find no old counsel/default review wording in the incoming benchmark.
- Stop rule: do not upload, sign, pay, submit, claim a real receipt, claim a real application number, involve an external lawyer, or relax lifecycle hash checks.

Backup:

- `<skill-root>\backups\20260603-000500-incoming-disclosure-ai-only-gate`
- Extra lifecycle hash backup: `<skill-root>\backups\20260603-000500-incoming-disclosure-ai-only-gate\case-lifecycle-trace-mock-hash-refresh`

Changes recorded:

- Updated `benchmarks/incoming-disclosure-to-application/invention-disclosure.json` to use an AI self-filing legal/compliance-ready business goal and `ai_legal_compliance_questions` instead of `counsel_questions`.
- Updated the incoming patent draft from `counsel_review_needed` / `## Counsel Questions` to `ai_self_filing_authorization_needed` / `## AI Legal/Compliance Questions`.
- Updated incoming claim-support and source-manifest wording so missing readiness materials require AI self-filing legal/compliance authorization, not counsel or patent-agent review.
- Added `legal_gate_mode=ai_self_filing_no_external_lawyer`, `draft_generation_allowed=true`, `filing_allowed=false`, `external_lawyer_involved=false`, and `official_system_touched=false` to incoming filing status.
- Hardened `scripts/validate_incoming_application_benchmark.py` to reject legacy default review wording, require AI legal/compliance questions, require no-external-lawyer status fields, and scan draft/claim/source text for old defaults.
- Updated `references/patent-generation-engine.md`, `SKILL.md`, and `test-prompts.json` so patent generation defaults to AI self-filing authorization-ready artifacts.
- Recomputed `benchmarks/incoming-disclosure-to-application/artifact-hashes.json` and refreshed `benchmarks/case-lifecycle-trace-mock` stage hashes that reference the changed incoming source manifest and draft.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `validate_incoming_application_benchmark.py benchmarks\incoming-disclosure-to-application --json`: passed with only expected draft/prior-art warnings.
- `validate_artifact_hash_manifest.py benchmarks\incoming-disclosure-to-application\artifact-hashes.json --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\case-lifecycle-trace-mock --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\case-lifecycle-trace-mock\artifact-hashes.json --json`: passed.
- `python -X utf8 -m py_compile scripts\validate_incoming_application_benchmark.py`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Static scans over `benchmarks\incoming-disclosure-to-application` found no `counsel_questions`, `counsel_review_needed`, `## Counsel Questions`, counsel-ready, counsel review, attorney review, lawyer review, patent-agent review, or patent agent review defaults.
- Static scan found no `external_lawyer_involved=true`, `official_submission_performed=true`, or `official_system_touched=true` in the incoming benchmark; residual `__pycache__` scan found no directories after cleanup.

## 2026-06-02 23:58 +08:00

Karpathy preflight:

- Assumptions: upstream intake/scaffold should default to the no-external-lawyer AI self-filing route, while the separate counsel/agent reviewed route remains available only when explicitly supplied; legal/compliance gates remain mandatory.
- Smallest sufficient action: remove default counsel/patent-agent wording from intake, normalization, scaffold confirmation, templates, and draft question flow; add validators that fail if old defaults reappear; refresh only hash-bound benchmark artifacts affected by the upstream field change.
- Evidence check: generated upstream artifacts must use `ai_legal_compliance_questions`, `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, no official action flags, and exact source/material/application hash binding through downstream AI self-filing benchmarks.
- Jagged-intelligence check: AI can produce plausible patent materials while silently carrying legacy review-role defaults or stale hashes; validators, source-file-bound material generation, and full regression close those brittle points.
- Success criteria: focused upstream/downstream validators pass, full regression passes, evidence bundle hash manifest validates, old default review terms do not appear in upstream generated artifacts, and no real official/external-lawyer flags are introduced.
- Stop rule: do not upload, sign, pay, submit, claim a real receipt, claim a real application number, involve an external lawyer, or loosen validators to hide stale hash drift.

Backup:

- `<skill-root>\backups\20260602-233000-intake-scaffold-ai-only-default`
- Extra backup for later touched confirmation/template/generator files: `<skill-root>\backups\20260602-233000-intake-scaffold-ai-only-default\extra-confirmation-template-generator`

Changes recorded:

- Updated intake and normalization generation so missing legal materials and scaffold questions default to AI legal/compliance confirmation, not counsel or patent-agent review.
- Hardened `validate_case_package_benchmark.py`, `validate_case_intake_orchestration_benchmark.py`, and `validate_disclosure_normalization_benchmark.py` to reject old default review wording and require AI self-filing legal gate fields.
- Tightened `validate_disclosure_confirmation_packet.py` so confirmation packets must use non-empty `ai_legal_compliance_questions` and must not use `counsel_questions`.
- Updated `confirm_invention_disclosure.py` and `generate_draft_package.py` so old `counsel_questions` are cleaned or ignored and cannot flow into new draft packages.
- Updated disclosure confirmation and invention-disclosure templates to default to AI legal/compliance reviewer/questions and `external_lawyer_involved=false`.
- Updated `references/case-package-protocol.md`, `references/case-intake-orchestration.md`, `references/disclosure-normalization.md`, `SKILL.md`, and `test-prompts.json` for the AI-only default intake/scaffold path.
- Regenerated intake, orchestration, disclosure normalization, scaffold confirmation, draft package, draft-evidence provenance, abnormal-filing risk, AI self-filing package validation, application materials, official-ready, approved-adapter, mock adapter execution, mock receipt, mock application-number, and lifecycle benchmark artifacts.
- Recomputed source-bound hashes for draft, abnormal-risk assessment, final package, reviewed artifacts, review record, application materials, official-ready source, and application-number source.
- Restored required mock evidence files from backup for adapter/receipt/application-number benchmark regeneration and removed generated `scripts\__pycache__`.

Verification:

- Focused validators passed for case package intake, case intake orchestration, disclosure normalization, scaffold confirmation, disclosure-confirmation rejection, draft package, both draft-evidence provenance gates, both abnormal-risk gates, AI self-filing package validation, application materials, official-ready, approved-adapter, adapter execution, receipt capture, application-number evidence, and both lifecycle traces.
- `python -X utf8 -m py_compile` on touched scripts: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=237 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Static scans over upstream generated reports/scaffolds/disclosure/draft outputs found no `counsel_questions`, default counsel/lawyer/attorney/patent-agent wording, `external_lawyer_involved=true`, or real official-action true flags in the checked non-official stages.
- Residual `__pycache__` scan after cleanup: no directories found.

## 2026-06-02 23:24 +08:00

Karpathy preflight:

- Assumptions: the no-external-lawyer default route should not generate draft-package outputs that tell the operator to send drafts to an attorney, counsel, or patent agent; legal/compliance authorization remains mandatory through the AI self-filing gate.
- Smallest sufficient action: harden draft-package generation and validation, refresh only the directly hash-bound downstream AI self-filing benchmark chain, and avoid changing the optional reviewed-package route in this pass.
- Evidence check: generated draft package outputs must carry `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved=false`, no official action flags, and no default attorney/lawyer/counsel/patent-agent wording in the draft, claim support map, report, status, or runner result.
- Jagged-intelligence check: AI can produce polished draft language while leaving old human-review defaults in status fields, queue decisions, and downstream hash-bound artifacts; validators and full-chain hash regeneration close that brittle point.
- Success criteria: draft package focused validator passes; AI self-filing package, application materials, official-ready, adapter, receipt, application-number, and lifecycle validators pass after hash refresh; full regression passes; extra scans find no default lawyer-review wording in draft outputs and no true official/external-lawyer flags.
- Stop rule: do not upload, sign, pay, submit, claim a receipt, claim an application number, involve an external lawyer, or loosen validators to hide hash drift.

Backup:

- `<skill-root>\backups\20260602-230000-draft-package-ai-only-gate`

Changes recorded:

- Updated `scripts/generate_draft_package.py` so generated draft packages now route to AI self-filing legal/compliance authorization instead of attorney/counsel/patent-agent review.
- Added `legal_gate_mode=ai_self_filing_no_external_lawyer` and `external_lawyer_involved=false` to generated draft-package filing status and response paths.
- Updated generated draft, claim support map, filing gate, report, and status wording to keep draft-only and do-not-file boundaries while removing default lawyer/agent review instructions.
- Updated `scripts/validate_patent_application_draft.py` to accept `ai_self_filing_authorization_needed` and the `## AI Legal/Compliance Questions` heading while preserving compatibility with older historical drafts.
- Updated `scripts/validate_draft_package_generation_benchmark.py` to require AI self-filing legal-gate mode, external-lawyer false, AI self-filing report text, and no default attorney/lawyer/counsel/patent-agent wording in generated draft-package outputs.
- Updated `scripts/run_case_queue.py` so draft-package queue decisions and next actions point to AI self-filing legal/compliance authorization.
- Updated `references/draft-package-generation.md`, `SKILL.md`, and `test-prompts.json` for the AI-only draft-package path.
- Regenerated `benchmarks/draft-package-generation/` plus its queue and runner output.
- Refreshed hash-bound downstream artifacts after the draft hash changed: draft evidence provenance, abnormal-filing risk, AI self-filing package validation, application materials, official-ready, approved-adapter preflight, adapter execution, receipt capture, application-number evidence, AI self-filing lifecycle trace, and generated lifecycle trace.
- Updated AI self-filing source and official/application-number source hashes that bind the refreshed draft package, application materials, and final package hash.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `python -X utf8 -m py_compile` on touched draft/package/queue scripts: passed.
- `python -X utf8 -m json.tool` on touched JSON prompts/status/manifests: passed.
- `generate_draft_package.py` regenerated `benchmarks\draft-package-generation` with `ok=true`, `draft_generation_allowed=true`, `filing_allowed=false`, `external_lawyer_involved=false`, `official_system_touched=false`, and `official_submission_performed=false`.
- `validate_draft_package_generation_benchmark.py benchmarks\draft-package-generation --json`: passed with only the expected `draft_supported` warning.
- Draft-package targeted scan over `patent-application-draft.md`, `claim-support-map.md`, `draft-package-report.md`, `filing-status.json`, and `generated-runner-result.json`: zero default attorney/lawyer/counsel/patent-agent terms.
- `build_case_queue.py` plus `run_case_queue.py` for draft-package generation: passed.
- First full regression exposed real downstream hash drift: AI self-filing source still had the old draft hash and lifecycle traces had old stage hashes.
- Refreshed AI self-filing source/package/lifecycle chain; second full regression exposed application-material source-manifest drift.
- Refreshed draft evidence provenance and abnormal-risk gates, regenerated AI package/materials/official-ready/adapter/receipt/application-number/lifecycle chain, and updated official/application-number source hashes.
- Focused downstream validators passed for draft package, both draft-evidence provenance gates, both abnormal-risk gates, AI self-filing package validation, abnormal-risk binding rejection, application materials, materials rejection, official-ready, approved adapter, adapter execution, receipt capture, application-number evidence, both lifecycle traces, and lifecycle rejection gate: 17 validators passed.
- Final `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=259 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Extra scans for default lawyer-review wording in draft-package generated outputs, real official-system touch, real official submission, external-lawyer true flags, and residual `__pycache__`: no matches.

## 2026-06-02 22:58 +08:00

Karpathy preflight:

- Assumptions: the user selected the no-external-lawyer default path, but the disclosure-confirmation stage still had legacy patent-agent/attorney role acceptance and a scaffold merge path that could reintroduce reference/prior-art hashes into applicant source evidence.
- Smallest sufficient action: harden only disclosure-confirmation validation/generation, add one rejection benchmark, connect it to queue/regression, and update the narrow docs/prompts; no official filing, payment, account, or adapter execution.
- Evidence check: confirmation packets must carry exact lowercase `sha256:<64 hex>` hashes, AI legal/compliance draft-review role, `external_lawyer_involved=false`, separated prohibited reference hashes, and draft-only controls.
- Jagged-intelligence check: AI is strong at structuring confirmations, but brittle at plausible legal-role claims and prior-art/source evidence pollution; deterministic validators and mutation tests close those gaps before draft generation.
- Success criteria: positive scaffold confirmation passes with AI-only review; unsafe lawyer/agent role, external-lawyer flag, malformed hash, unknown evidence hash, and prohibited-reference hash mutations fail; full regression passes; no official-system or submission flags appear.
- Stop rule: do not upload, sign, pay, submit, claim receipt, claim application number, claim lawyer/patent-agent involvement, or let prior-art hashes support applicant technical effects.

Backup:

- `<skill-root>\backups\20260602-220400-disclosure-confirmation-ai-only-gate`

Changes recorded:

- Replaced `scripts/validate_disclosure_confirmation_packet.py` with an AI-only disclosure confirmation gate: exact SHA-256 checks, allowed AI review roles, prohibited lawyer/patent-agent role checks, `external_lawyer_involved=false`, technical-effect evidence hash binding, and prohibited-reference hash rejection.
- Updated `scripts/confirm_invention_disclosure.py` to preserve `external_lawyer_involved=false`, render AI legal/compliance draft-review language, stop on missing final AI self-filing authorization, and prevent scaffold prior-art source hashes from being merged back into confirmed applicant `source_hashes`.
- Updated `scripts/validate_scaffold_confirmation_benchmark.py` to independently enforce AI-only confirmation roles, no external lawyer involvement, draft-only status, and confirmation-report wording.
- Added `scripts/validate_disclosure_confirmation_rejection_benchmark.py`.
- Added `benchmarks/disclosure-confirmation-rejection/` with mutation cases for patent-agent role claims, attorney-name claims, external-lawyer flag mutation, malformed source/reviewed hashes, prohibited reference hashes in source/effect evidence, and unknown technical-effect hashes.
- Updated `benchmarks/scaffold-confirmation-to-disclosure/disclosure-confirmation-packet.json` and regenerated `invention-disclosure.json`, `filing-status.json`, `confirmation-report.md`, and `artifact-hashes.json`.
- Connected the new rejection benchmark in `scripts/build_case_queue.py` and `scripts/run_case_queue.py`.
- Updated `references/disclosure-confirmation.md`, `SKILL.md`, and `test-prompts.json` to document AI legal/compliance draft review, exact hash gates, prohibited-reference separation, and the new rejection benchmark.
- Generated queue evidence in `out\disclosure-confirmation-rejection-queue.json` and `out\disclosure-confirmation-rejection-runner-result.json`.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `python -X utf8 -m py_compile` on disclosure confirmation validator/generator/benchmark/queue scripts: passed.
- `python -X utf8 -m json.tool` on `test-prompts.json`, positive confirmation packet, rejection cases, and rejection artifact manifest: passed.
- `confirm_invention_disclosure.py` regenerated the scaffold-confirmation benchmark with `ok=true`, `draft_generation_allowed=true`, `filing_allowed=false`, `external_lawyer_involved=false`, `official_system_touched=false`, and `official_submission_performed=false`.
- `validate_disclosure_confirmation_packet.py` on the positive packet with expected scaffold hash: passed.
- `validate_scaffold_confirmation_benchmark.py benchmarks\scaffold-confirmation-to-disclosure --json`: passed.
- `validate_disclosure_confirmation_rejection_benchmark.py benchmarks\disclosure-confirmation-rejection --json`: passed.
- `validate_artifact_hash_manifest.py` on both scaffold-confirmation and disclosure-confirmation-rejection manifests: passed.
- `build_case_queue.py` plus `run_case_queue.py` for the new rejection benchmark: passed, with local dry-run only.
- Structured prior-art hash check: the prohibited reference hash is absent from positive packet/disclosure `source_hashes` and technical-effect evidence, and present only in `prohibited_reference_hashes`.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=49 failed=0`, `artifact_manifests.total=52 failed=0`, `source_compile.total=92 failed=0`, `json_parse.total=259 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Extra scans for real official-system touch, real official submission, external-lawyer true flags, prohibited positive disclosure roles, and residual `__pycache__`: no matches.

## 2026-06-02 21:50 +08:00

Karpathy preflight:

- Assumptions: all current source-material manifests already carry enough local evidence to recompute `source_package_hash` from material filenames, hashes, and byte counts.
- Smallest sufficient action: harden only package-level source hash recomputation and add one rejection mutation for valid-shaped-but-wrong package hashes; no broad refactor.
- Evidence check: a top IP evidence team would verify both individual source file hashes and the aggregate source package hash so material additions, removals, or substitutions cannot hide behind unchanged file rows.
- Jagged-intelligence check: AI can keep each material row plausible while drifting the aggregate package identity; deterministic recomputation closes that brittle point before drafting or filing.
- Success criteria: all positive source-material fixtures still pass, the new mismatch rejection case fails for `source_package_hash_mismatch`, full regression passes, and no official-system, submission, or external-lawyer flag appears.
- Stop rule: do not upload, sign, pay, submit, claim receipt, claim application number, or involve external lawyers.

Backup:

- `<skill-root>\backups\20260602-215500-source-package-hash-recompute`

Changes recorded:

- Updated `scripts/validate_source_material_manifest.py` to recompute `source_package_hash` from sorted `filename<TAB>hash<TAB>bytes` rows whenever local material files are available.
- Added `source_package_hash_mismatch_rejected` to `benchmarks/source-material-file-binding-rejection/rejection-cases.json`.
- Refreshed `benchmarks/source-material-file-binding-rejection/artifact-hashes.json`.
- Updated `references/case-package-protocol.md`, `SKILL.md`, and `test-prompts.json` to document aggregate source-package hash recomputation and mismatch rejection.

Verification:

- `python -X utf8 -m py_compile scripts\validate_source_material_manifest.py scripts\validate_source_material_file_binding_rejection_benchmark.py scripts\build_case_queue.py`: passed.
- `python -X utf8 -m json.tool` on `test-prompts.json`, source-material rejection cases, and source-material rejection artifact manifest: passed.
- `validate_source_material_file_binding_rejection_benchmark.py benchmarks\source-material-file-binding-rejection --json`: passed with expected prior-art-not-claim-support warnings, including `source_package_hash_mismatch_rejected`.
- `validate_artifact_hash_manifest.py benchmarks\source-material-file-binding-rejection\artifact-hashes.json --json`: passed.
- `validate_source_material_manifest.py benchmarks\incoming-disclosure-to-application\source-material-manifest.yaml --base-dir benchmarks\incoming-disclosure-to-application --json`: passed with expected prior-art-not-claim-support warning.
- `validate_case_package_benchmark.py benchmarks\case-package-intake-dry-run --json`: passed with expected source-material warnings.
- `validate_case_intake_orchestration_benchmark.py benchmarks\case-package-orchestration-dry-run --json`: passed with expected source-material warnings.
- `validate_draft_evidence_provenance_benchmark.py` on `draft-evidence-provenance-gate` and `ai-self-filing-draft-evidence-provenance`: passed with expected draft/prior-art warnings.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=48 failed=0`, `artifact_manifests.total=51 failed=0`, `source_compile.total=91 failed=0`, `json_parse.total=257 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Extra forbidden flag scan for real official-system touch, real official submission, and external-lawyer involvement: no matches.
- Extra weak-prefix scan in the source-material package-hash target files: no matches.
- Extra SHA token scan over the source-material rejection benchmark and source manifest: expected exact hashes or deliberate malformed rejection mutations only.

## 2026-06-02 21:44 +08:00

Karpathy preflight:

- Assumptions: top patent operations, filing automation, and IP evidence teams treat raw received materials as an adversarial evidence boundary; positive validation is insufficient without mutation/rejection coverage.
- Smallest sufficient action: add source-material rejection coverage and one narrowly scoped validator hardening for prior-art/reference evidence contamination; no official filing path, no lawyer path, and no broad refactor.
- Evidence check: local source files must exist and match exact hashes; claim-support links must refer to known claim-support-eligible materials; prior-art/reference materials must never become applicant-owned claim support.
- Jagged-intelligence check: AI is strong at drafting from structured materials, but brittle at provenance pollution and plausible-but-false support maps; hard rejection cases turn those brittle points into repeatable gates.
- Success criteria: source-material positive benchmark still passes, new rejection benchmark passes, full regression includes the new folder, generated evidence bundle validates, and forbidden scans remain empty.
- Stop rule: do not upload, sign, pay, submit, claim receipt, claim application number, or claim external lawyer involvement.

Backup:

- `<skill-root>\backups\20260602-214500-source-material-rejection-gate`

Changes recorded:

- Updated `scripts/validate_source_material_manifest.py` to reject prior-art/reference materials marked `usable_for_claim_support=true`.
- Added claim-support link checks so links must point to known materials and those materials must be usable for claim support.
- Added `scripts/validate_source_material_file_binding_rejection_benchmark.py` for mutation-based rejection testing of source material manifests.
- Added `benchmarks/source-material-file-binding-rejection/` with cases for missing material files, material hash mismatch, malformed source/material/chain/claim-support hashes, unknown material IDs, prior-art marked usable for support, and claim-support links to prior art.
- Added the new benchmark to `scripts/build_case_queue.py` so full regression runs it.
- Updated `references/case-package-protocol.md`, `SKILL.md`, and `test-prompts.json` to make source-material rejection coverage part of the standard intake quality gate.

Verification:

- `python -X utf8 -m py_compile scripts\validate_source_material_manifest.py scripts\validate_source_material_file_binding_rejection_benchmark.py scripts\build_case_queue.py`: passed.
- `python -X utf8 -m json.tool` on `test-prompts.json`, the new `rejection-cases.json`, and the new `artifact-hashes.json`: passed.
- `validate_source_material_file_binding_rejection_benchmark.py benchmarks\source-material-file-binding-rejection --json`: passed with expected prior-art-not-claim-support warnings.
- `validate_artifact_hash_manifest.py benchmarks\source-material-file-binding-rejection\artifact-hashes.json --json`: passed.
- `validate_source_material_manifest.py benchmarks\incoming-disclosure-to-application\source-material-manifest.yaml --base-dir benchmarks\incoming-disclosure-to-application --json`: passed with expected prior-art-not-claim-support warning.
- `validate_incoming_application_benchmark.py benchmarks\incoming-disclosure-to-application --json`: passed with expected draft/prior-art warnings.
- `validate_case_package_benchmark.py benchmarks\case-package-intake-dry-run --json`: passed with expected source-material warnings.
- `validate_case_intake_orchestration_benchmark.py benchmarks\case-package-orchestration-dry-run --json`: passed with expected source-material warnings.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=48 failed=0`, `artifact_manifests.total=51 failed=0`, `source_compile.total=91 failed=0`, `json_parse.total=257 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Extra forbidden flag scan for real official-system touch, real official submission, and external-lawyer involvement: no matches.
- Extra weak-prefix scan in the source-material rejection target files: no matches.
- Extra SHA token scan over the new rejection benchmark and source manifest: expected exact hashes or deliberate malformed rejection mutations only.

## 2026-06-02 21:34 +08:00

Karpathy preflight:

- Assumptions: the raw "received materials" layer is now a filing-quality evidence boundary; descriptive `sha256:` placeholders can make unverified source material look claim-support-ready.
- Smallest sufficient action: harden only source-material, claim-support, draft-provenance, abnormal-risk, and directly derived benchmark/lifecycle artifacts; do not broaden into real official filing.
- Evidence check: source files, manifest material hashes, chain-of-custody hashes, claim-support rows, draft evidence provenance, abnormal-risk source hashes, application materials, receipt, application-number evidence, and lifecycle trace artifacts must be exact lowercase `sha256:<64 hex>` and recomputed where local files exist.
- Jagged-intelligence check: AI is strong at structuring patent drafts and audit packets, but brittle at evidence drift and prior-art/source confusion; file-bound validation and prior-art exclusion are the guardrails.
- Success criteria: focused source/provenance/abnormal/materials/application-number/lifecycle validators pass, full regression passes, extra forbidden scans have no matches, and no real official-system, official-submission, or external-lawyer flag is introduced.
- Stop rule: do not upload, sign, pay, submit, claim a real receipt, or claim a real application number.

Backup:

- `<skill-root>\backups\20260602-211200-source-material-file-binding`
- `<skill-root>\backups\20260602-212000-downstream-lifecycle-refresh`

Changes recorded:

- Updated source-material validation to require exact lowercase SHA-256 fields and recompute referenced material files when a base directory is available.
- Updated claim-support and draft-evidence provenance validation to reject weak `sha256:` prefix placeholders; own-support, prohibited-reference, and row evidence hashes must be exact.
- Updated provenance and abnormal-risk generators to copy manifest-referenced source files into output packages and ignore non-exact hash tokens.
- Rebuilt `benchmarks/incoming-disclosure-to-application` with real local raw evidence files, exact material hashes, a stable `source_package_hash`, and refreshed draft/claim-map/artifact hashes.
- Regenerated draft-evidence provenance, abnormal-risk, AI self-filing package/materials/official-ready/adapter/receipt/application-number/lifecycle benchmark chains after upstream source hash changes.
- Fixed a discovered evidence error in `benchmarks/draft-package-generation`: a prior-art hash had been used as technical-effect support; it now points to applicant-owned drawing notes, and derived AI self-filing hashes were refreshed.
- Updated `case-lifecycle-trace-mock` stage hashes for the refreshed source manifest and draft artifact.
- Updated `references/case-package-protocol.md`, `references/draft-package-generation.md`, `SKILL.md`, and `test-prompts.json` to document exact file-bound source material hashes and prior-art exclusion from own claim support.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `validate_source_material_manifest.py benchmarks\incoming-disclosure-to-application\source-material-manifest.yaml --base-dir benchmarks\incoming-disclosure-to-application --json`: passed with expected prior-art-not-claim-support warning.
- `validate_incoming_application_benchmark.py benchmarks\incoming-disclosure-to-application --json`: passed with expected draft/prior-art warnings.
- `validate_draft_evidence_provenance_benchmark.py` on `draft-evidence-provenance-gate` and `ai-self-filing-draft-evidence-provenance`: passed with expected draft/prior-art warnings.
- `validate_abnormal_filing_risk_benchmark.py` on `abnormal-filing-risk-gate` and `ai-self-filing-abnormal-risk-gate`: passed with expected draft/prior-art warnings.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_generated_application_number_benchmark.py benchmarks\ai-self-filing-official-receipt-to-application-number --json`: passed with expected mock application-number warning.
- `validate_case_lifecycle_benchmark.py` on `ai-self-filing-lifecycle-trace`, `generated-case-lifecycle-trace`, and `case-lifecycle-trace-mock`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Extra forbidden flag scans for real official-system touch, real official submission, and external-lawyer involvement: no matches.
- Extra weak-prefix scan in hardened source/provenance scripts and docs: no matches.
- Extra affected-material SHA token scan: all `sha256:` tokens are exact lowercase 64-hex values.

## 2026-06-02 21:02 +08:00

Karpathy preflight:

- Assumptions: the application-materials bundle is the point where AI-generated claims/specification/abstract/drawings/request/XML materials become a preflight-ready artifact; malformed hash strings here can make unsupported generated material look bound.
- Smallest sufficient action: harden `validate_patent_application_materials.py` and its rejection benchmark only, without pretending old raw-material benchmark placeholders are file-bound when the referenced raw files are absent.
- Evidence check: generated material files, request metadata, document generation plan, XML readiness, filing status, copied draft-evidence provenance, copied abnormal-risk assessment, official inventory hashes, own-support hashes, and prohibited-reference hashes must use exact lowercase SHA-256 values.
- Jagged-intelligence check: AI is strong at generating application text and metadata, but brittle at evidentiary integrity; exact hash-shape rejection prevents plausible but unbound material bundles from advancing toward official-channel preflight.
- Success criteria: application-materials positive benchmark passes, malformed-hash rejection cases fail for the expected reasons, full regression passes, and no official-system, official-submission, or external-lawyer flag is introduced.
- Stop rule: do not upload, sign, pay, submit, claim receipt, or claim an application number from generated materials.

Backup:

- `<skill-root>\backups\20260602-210300-application-materials-exact-hash-gate`

Changes recorded:

- Updated `scripts/validate_patent_application_materials.py` to require exact lowercase `sha256:<64 hex>` values instead of weak `sha256:` prefix checks.
- Added exact-hash validation for `evidence_provenance.own_support_hashes`, `evidence_provenance.prohibited_reference_hashes`, and optional `xml_readiness.validation_report_hash`.
- Added rejection cases for malformed `final_package_hash`, malformed own-support hash, and malformed XML validation-report hash in `benchmarks/patent-application-materials-rejection/rejection-cases.json`.
- Refreshed `benchmarks/patent-application-materials-rejection/artifact-hashes.json` after the rejection spec changed.
- Updated `references/application-materials-generation.md`, `SKILL.md`, and `test-prompts.json` to require exact SHA-256 at the application-materials boundary.
- Explicitly left old raw-material benchmark placeholders for a separate protocol pass because their referenced raw files are not present; replacing them with synthetic 64-hex values would not be honest file binding.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `python -X utf8 -m py_compile scripts\validate_patent_application_materials.py scripts\validate_patent_application_materials_rejection_benchmark.py`: passed.
- `python -X utf8 -m json.tool test-prompts.json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_patent_application_materials_rejection_benchmark.py benchmarks\patent-application-materials-rejection --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\patent-application-materials-rejection\artifact-hashes.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Forbidden flag scan for real official-system touch, real official submission, and external-lawyer involvement: no matches.
- Residual weak-prefix scan in the application-materials target validator and docs: no matches.

## 2026-06-02 20:53 +08:00

Karpathy preflight:

- Assumptions: post-adapter official evidence, official receipt, application-number evidence, and lifecycle traces are high-risk status-upgrade boundaries; they must not accept descriptive `sha256:` placeholders.
- Smallest sufficient action: harden only the production official-evidence and application-number/lifecycle hash checks, then regenerate or refresh directly affected benchmark artifacts.
- Evidence check: receipt files, official status snapshots, official file lists, paid payment receipts, application-number evidence, lifecycle artifacts, and production evidence packets must be recomputed from local bytes when a base directory is available.
- Jagged-intelligence check: AI can produce plausible filing/status language while drifting artifact hashes; exact lowercase SHA-256 plus file-bound recomputation closes this brittle edge.
- Success criteria: focused application-number, receipt, production-evidence, adapter, and lifecycle validators pass; full regression passes; no real official-system, real official-submission, or external-lawyer flag is introduced.
- Stop rule: do not upload, sign, pay, submit, claim a real official receipt, or claim a real application number.

Backup:

- `<skill-root>\backups\20260602-205200-production-official-evidence-hash-binding`
- Backup note: `scripts\validate_application_number_benchmark.py` was added to the backup after the edit because no prior backup copy was found; the anomaly is recorded here instead of hidden. `benchmarks\case-lifecycle-trace-mock` was also added after full regression exposed its derived hash drift.

Changes recorded:

- Updated `scripts/validate_application_number_evidence.py` to require exact lowercase `sha256:<64 hex>` hashes, require `application.official_file_list_file`, and recompute receipt, official status snapshot, official file list, and paid payment receipt file hashes from disk.
- Updated `scripts/validate_production_official_evidence_gate.py` to enforce exact hash format and pass application-number evidence directory context except for explicit production-shape tests.
- Updated `scripts/prepare_application_number_acceptance.py` to validate source evidence against source files, copy official receipt/status/file-list/payment evidence into the generated output, and rewrite path/hash fields to the copied files.
- Updated `scripts/prepare_receipt_capture.py`, `scripts/validate_case_lifecycle_trace.py`, `scripts/validate_adapter_execution_benchmark.py`, and `scripts/validate_application_number_benchmark.py` to reject weak hash placeholders or pass file-bound context where available.
- Added official file-list evidence into application-number benchmark packets and regenerated official-receipt-to-application-number plus AI self-filing application-number benchmark outputs.
- Refreshed production official-evidence shape hashes, application-number acceptance mock manifest, generated lifecycle traces, and AI self-filing lifecycle traces after upstream hash changes.
- Fixed the full-regression-discovered drift in `benchmarks/case-lifecycle-trace-mock` by synchronizing stage 9's application-number evidence hash and refreshing that mock trace manifest.
- Updated `references/application-number-evidence.md`, `references/production-official-evidence-gate.md`, `references/case-lifecycle-trace.md`, `SKILL.md`, and `test-prompts.json` to document exact SHA-256 and official file-list/status snapshot file binding.
- Removed generated `scripts\__pycache__` after validation.

Verification:

- `python -X utf8 -m py_compile` on the touched validators/generators: passed.
- `validate_application_number_benchmark.py benchmarks\application-number-acceptance-mock --json`: passed with expected mock application-number warning.
- `validate_generated_application_number_benchmark.py benchmarks\official-receipt-to-application-number --json`: passed with expected mock application-number warning.
- `validate_generated_application_number_benchmark.py benchmarks\ai-self-filing-official-receipt-to-application-number --json`: passed with expected mock application-number warning.
- `validate_production_official_evidence_gate_benchmark.py benchmarks\production-official-evidence-gate --json`: passed with expected production-shape warning.
- `validate_generated_receipt_capture_benchmark.py benchmarks\submitted-pending-receipt-to-official-receipt --json`: passed.
- `validate_generated_receipt_capture_benchmark.py benchmarks\ai-self-filing-submitted-pending-receipt-to-official-receipt --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\generated-case-lifecycle-trace --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\ai-self-filing-lifecycle-trace --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\case-lifecycle-trace-mock --json`: passed after the derived stage 9 hash refresh.
- `validate_adapter_execution_benchmark.py benchmarks\adapter-execution-mock-submitted --json`: passed with expected mock/submitted-pending warnings.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt --json`: passed with expected mock/submitted-pending warnings.
- First full `run_regression_gate.py --output-dir out\regression-gate --json` found one derived hash mismatch in `case-lifecycle-trace-mock`; after fixing it, the rerun passed with `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Forbidden flag scan for real official-system touch, real official submission, and external-lawyer involvement: no matches.
- Residual weak-prefix scan in the official-evidence/application-number/lifecycle target validators: no matches.

## 2026-06-02 20:36 +08:00

Karpathy preflight:

- Assumptions: approved-adapter preflight, production adapter readiness, official session authorization, and filing adapter request/response are execution-boundary artifacts and must not accept descriptive `sha256:` placeholders.
- Smallest sufficient action: harden only the adapter preflight/contract/session/readiness validators, then regenerate directly affected benchmark chains.
- Evidence check: local file references for authorization packet, official preflight, package manifest, receipt plan, audit plan, docket plan, readiness packet, session packet, adapter request, approved preflight, and adapter execution result must be recomputed from disk.
- Jagged-intelligence check: AI workflows can keep plausible legal and filing text while drifting hashes across preflight/request/response; exact SHA-256 plus file-bound consistency checks close that brittle execution edge.
- Success criteria: focused adapter/session/readiness/receipt/application/lifecycle validators pass, full regression passes, and no official-system, official-submission, or external-lawyer flag is introduced.
- Stop rule: do not upload, sign, pay, submit, claim real receipt, or claim a real application number.

Backup:

- `<skill-root>\backups\20260602-203700-approved-adapter-preflight-contract-hash-binding`

Changes recorded:

- Updated `scripts/validate_production_adapter_readiness.py` and `scripts/validate_official_session_authorization.py` to require exact lowercase `sha256:<64 hex>` hash fields.
- Updated `scripts/validate_approved_adapter_preflight.py` to require exact hash fields and recompute local authorization, official preflight, package manifest, receipt plan, audit plan, docket plan, production readiness packet, and official session packet hashes.
- Updated `scripts/validate_filing_adapter_contract.py` to require exact hash fields, recompute approved-preflight/readiness/session/result file hashes, compare approved-adapter requests back to the referenced preflight, and compare submitted-pending responses back to the referenced execution result.
- Fixed `scripts/prepare_receipt_capture.py` so blank optional payment/receipt evidence paths are not treated as directories in `artifact-hashes.json`.
- Replaced descriptive benchmark hash placeholders in approved-adapter and case-processor dry-run artifacts with exact SHA-256 values and refreshed their artifact manifests.
- Regenerated official-ready and AI self-filing approved-adapter preflight, adapter execution, receipt capture, application-number, and lifecycle benchmark chains after the stricter hash binding changed upstream artifact hashes.
- Updated `references/production-adapter-readiness.md`, `references/official-session-authorization.md`, `references/approved-adapter-preflight.md`, `references/filing-adapter-interface.md`, `SKILL.md`, and `test-prompts.json` to document exact SHA-256 and file-bound adapter boundary checks.
- Removed generated `scripts\__pycache__`.

Verification:

- `validate_approved_adapter_benchmark.py benchmarks\approved-adapter-preflight-ready --json`: passed.
- `validate_case_processor_benchmark.py benchmarks\case-processor-dry-run --json`: passed.
- `validate_generated_approved_adapter_preflight_benchmark.py benchmarks\official-ready-to-approved-adapter-preflight --json`: passed.
- `validate_generated_approved_adapter_preflight_benchmark.py benchmarks\ai-self-filing-approved-adapter-preflight --json`: passed.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\approved-adapter-to-submitted-pending-receipt --json`: passed with expected mock/submitted-pending warnings.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt --json`: passed with expected mock/submitted-pending warnings.
- `validate_generated_receipt_capture_benchmark.py benchmarks\submitted-pending-receipt-to-official-receipt --json`: passed.
- `validate_generated_receipt_capture_benchmark.py benchmarks\ai-self-filing-submitted-pending-receipt-to-official-receipt --json`: passed.
- `validate_generated_application_number_benchmark.py benchmarks\official-receipt-to-application-number --json`: passed with expected mock application-number warning.
- `validate_generated_application_number_benchmark.py benchmarks\ai-self-filing-official-receipt-to-application-number --json`: passed with expected mock application-number warning.
- `validate_case_lifecycle_benchmark.py benchmarks\generated-case-lifecycle-trace --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\ai-self-filing-lifecycle-trace --json`: passed.
- `validate_production_adapter_readiness_benchmark.py benchmarks\production-adapter-readiness-gate --json`: passed with expected production-shape warning.
- `validate_official_session_authorization_benchmark.py benchmarks\official-session-authorization-gate --json`: passed with expected production-shape warning.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.
- Forbidden flag scan for `external_lawyer_involved=true`, `official_submission_performed=true`, and `official_system_touched=true`: no matches.
- Residual weak-prefix scan in the four adapter-boundary validators: no matches.

## 2026-06-02 20:15 +08:00

Karpathy preflight:

- Assumptions: the AI self-filing legal/compliance gate is a critical no-external-lawyer entry point and must not accept descriptive or malformed hash strings.
- Smallest sufficient action: harden `validate_ai_self_filing_authorization.py` first, then pass packet-directory context only where it is already known.
- Evidence check: same-case abnormal filing risk evidence must be a local artifact path whose hash is recomputed by the validator when possible.
- Jagged-intelligence check: AI workflows can preserve plausible legal-gate text while drifting hashes or artifact paths; exact hash format plus file binding closes that brittle point before package validation.
- Success criteria: AI self-filing authorization, package, legal-gate rejection, deficiency, cure, generator smoke tests, full regression, and regression artifact manifest all pass.
- Stop rule: do not upload, sign, pay, submit, claim real receipt, or claim a real application number.

Backup:

- `<skill-root>\backups\20260602-200900-ai-self-filing-authorization-hash-binding`

Changes recorded:

- Updated `scripts/validate_ai_self_filing_authorization.py` to require exact lowercase `sha256:<64 hex>` values for AI self-filing hash fields.
- Required `ai_compliance_review.abnormal_filing_risk_assessment.artifact_path` and added file existence plus hash recomputation when `base_dir` is supplied.
- Passed `base_dir` through AI self-filing package, ready, approved-adapter, deficiency, cure, and benchmark validators where packet directory context is authoritative.
- Added legal-gate rejection cases for invalid hash shape, abnormal-risk artifact hash mismatch, and missing abnormal-risk artifact file.
- Updated `benchmarks/ai-self-filing-legal-gate-rejection/artifact-hashes.json` for the changed rejection spec.
- Updated `references/ai-self-filing-gate.md`, `references/legal-gates.md`, `SKILL.md`, and `test-prompts.json` to document exact SHA-256 and abnormal-risk artifact path/hash binding.
- Removed generated pyc files for scripts touched in this stage.

Verification:

- `validate_ai_self_filing_authorization.py benchmarks\ai-self-filing-package-validation\ai-self-filing-authorization-packet.json --json`: passed.
- `validate_ai_self_filing_package_benchmark.py benchmarks\ai-self-filing-package-validation --json`: passed.
- `validate_ai_self_filing_legal_gate_rejection_benchmark.py benchmarks\ai-self-filing-legal-gate-rejection --json`: passed.
- `validate_ai_self_filing_deficiency_report_benchmark.py benchmarks\ai-self-filing-deficiency-report --json`: passed.
- `validate_ai_self_filing_cure_revalidation_benchmark.py benchmarks\ai-self-filing-cure-revalidation --json`: passed.
- `prepare_ai_self_filing_package.py ... --output-dir out\ai-self-filing-package-validation-smoke --json`: passed.
- `prepare_ai_self_filing_deficiency_report.py ... --rejection-case-id abnormal_risk_assessment_hash_mismatch_rejected --output-dir out\ai-self-filing-deficiency-hash-mismatch-smoke --json`: passed with `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `prepare_ai_self_filing_cure_revalidation.py ... --output-dir out\ai-self-filing-cure-revalidation-smoke --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 20:07 +08:00

Karpathy preflight:

- Assumptions: validated filing packages must not pass on descriptive hash placeholders or missing final-material files; AI self-filing still requires the legal/compliance gate, but no external lawyer or patent agent is used.
- Smallest sufficient action: bind source draft, authorization packet, and final package documents to local file hashes; then regenerate only directly affected package, materials, ready, adapter, and lifecycle benchmark artifacts.
- Evidence check: validators must recompute file hashes from the package directory; generated packages must include draft/material files; downstream traces must use current stage artifact hashes.
- Jagged-intelligence check: AI workflows often keep plausible manifest fields while file paths or copied inventories drift; directory-aware validation closes that gap before official-channel preflight.
- Success criteria: focused package/material/lifecycle validators pass, full regression passes, and regression artifact manifest validates independently.
- Stop rule: do not upload, sign, pay, submit, claim real receipt, or claim a real application number.

Backup:

- `<skill-root>\backups\20260602-194900-validated-filing-package-file-hash-binding`

Changes recorded:

- Updated `scripts/validate_filing_package_manifest.py` and `scripts/validate_submission_packet.py` to require exact lowercase `sha256:<64 hex>` values and validate referenced files against hashes when a base directory is available.
- Updated package validation call sites in `scripts/prepare_validated_filing_package.py`, `scripts/prepare_ai_self_filing_package.py`, `scripts/prepare_ready_for_authorized_filing.py`, `scripts/prepare_approved_adapter_preflight.py`, `scripts/validate_ai_self_filing_package_benchmark.py`, `scripts/validate_authorized_ready_benchmark.py`, and `scripts/validate_patent_application_materials.py`.
- Updated `scripts/prepare_validated_filing_package.py` to copy the source draft and final claims/specification/abstract/drawings/request metadata files into generated validated packages, and to write manifest document hashes from those copied files.
- Updated `scripts/prepare_ai_self_filing_package.py` to write source draft plus offline mock final material files into the package and bind manifest document hashes to those files.
- Added file-bound mock materials to `benchmarks/draft-to-filing-package-validation`, `benchmarks/draft-package-to-filing-validation`, and `benchmarks/authorized-cn-ready-for-filing`; replaced validated-package hash placeholders with exact hashes where those benchmarks are in the hardened path.
- Regenerated affected generated artifacts for draft package validation, AI self-filing package validation, AI application materials, AI/counsel official-ready, AI/counsel approved adapter preflight, AI/counsel adapter execution mock result, and AI/counsel lifecycle traces.
- Updated `benchmarks/case-lifecycle-trace-mock` stage artifact hashes for the changed `draft-to-filing-package-validation` artifacts.
- Updated `SKILL.md` and `test-prompts.json` to document exact sha256 file binding for validated package generation and validation.
- Removed generated pyc files for scripts touched in this stage.

Verification:

- `validate_draft_to_package_benchmark.py benchmarks\draft-to-filing-package-validation --json`: passed.
- `validate_validated_filing_package_benchmark.py benchmarks\draft-package-to-filing-validation --json`: passed.
- `validate_ai_self_filing_package_benchmark.py benchmarks\ai-self-filing-package-validation --json`: passed.
- `validate_authorized_ready_benchmark.py benchmarks\authorized-cn-ready-for-filing --json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\case-lifecycle-trace-mock --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 19:33 +08:00

Karpathy preflight:

- Assumptions: `submitted_pending_receipt` is a high-risk transition and must not rely on descriptive `sha256:mock...` or `sha256:...-v1` placeholders; no external lawyer is used; no official system is touched by these local generators.
- Smallest sufficient action: harden adapter execution evidence first, because it is the bridge between approved adapter preflight and receipt capture.
- Evidence check: submitted-pending status snapshot and submitted file-list evidence must be local files whose hashes are recomputed by validators/generators.
- Jagged-intelligence check: AI is brittle at preserving cross-stage hashes through generated result, response, status, production evidence gate, and lifecycle traces; add file-bound validation plus mutation tests.
- Success criteria: adapter focused validators, generated adapter validators, lifecycle validators, production official evidence gate, full regression, and regression artifact manifest all pass.
- Stop rule: do not upload, sign, pay, submit, claim real receipt, or claim a real application number.

Backup:

- `<skill-root>\backups\20260602-193300-adapter-execution-hash-binding`

Changes recorded:

- Updated `scripts/validate_adapter_execution_result.py` to require exact lowercase `sha256:<64 hex>` values and require file-bound submitted status snapshot plus submitted file-list evidence.
- Updated `scripts/prepare_adapter_execution_result.py` to validate source evidence files, copy them into generated output, recompute their hashes, and include copied evidence files in artifact manifests.
- Updated `scripts/validate_adapter_execution_benchmark.py` with negative mutations for submitted status snapshot and submitted file-list hash mismatches.
- Updated `scripts/validate_generated_adapter_execution_result_benchmark.py` to validate source evidence file paths/hashes and compare source/result file references.
- Added local mock submitted package, submitted status snapshot, and submitted file-list evidence to `adapter-execution-mock-submitted`.
- Added local submitted status snapshot and submitted file-list evidence to counsel-reviewed and AI self-filing generated adapter execution benchmarks, then regenerated both benchmark folders through `prepare_adapter_execution_result.py`.
- Synchronized adapter result/response/status/audit/docket hashes, lifecycle stage artifact hashes, and artifact manifests for affected adapter and lifecycle benchmarks.
- Updated production official evidence shape-test and mock-rejection packets to match the stricter adapter execution evidence contract and current artifact hashes.
- Updated `SKILL.md` and `test-prompts.json` to state the adapter execution file-bound SHA-256 evidence contract.
- Removed generated `.pyc` files for adapter execution, generated adapter validation, production official evidence, artifact manifest, and regression scripts.

Verification:

- `validate_adapter_execution_benchmark.py benchmarks\adapter-execution-mock-submitted --json`: passed with expected mock/follow-up warnings.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\approved-adapter-to-submitted-pending-receipt --json`: passed with expected mock/follow-up warnings.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt --json`: passed with expected mock/follow-up warnings.
- `validate_case_lifecycle_benchmark.py benchmarks\case-lifecycle-trace-mock --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\generated-case-lifecycle-trace --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\ai-self-filing-lifecycle-trace --json`: passed.
- `validate_production_official_evidence_gate_benchmark.py benchmarks\production-official-evidence-gate --json`: passed with expected production-shape warning.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 19:22 +08:00

Karpathy preflight:

- Assumptions: receipt and application-number status must be backed by real local evidence files in benchmarks, not descriptive `sha256:mock...` placeholders; no external lawyer is used; no official system is touched.
- Smallest sufficient action: make receipt-capture validation require exact SHA-256 format and recompute file hashes where file paths are present, then synchronize affected generated benchmarks and lifecycle traces.
- Evidence check: all benchmark evidence remains explicitly mock/shape-test material; production evidence still requires the production official evidence gate.
- Jagged-intelligence check: AI workflows are brittle at carrying hashes through multi-stage traces; validators must recompute hashes instead of trusting copied strings.
- Success criteria: focused receipt/application-number/lifecycle validators, artifact manifests, full regression gate, and regression artifact manifest all pass.
- Stop rule: do not upload, sign, pay, submit, mark real receipt, or mark a real application number.

Backup:

- `<skill-root>\backups\20260602-190520-receipt-capture-file-hash-binding`
- Added backup copies for `ai-self-filing-submitted-pending-receipt-to-official-receipt`, `ai-self-filing-official-receipt-to-application-number`, `ai-self-filing-lifecycle-trace`, and previous `out\regression-gate` outputs.

Changes recorded:

- Updated `scripts/validate_receipt_capture.py` to require exact lowercase `sha256:<64 hex>` values and recompute `official_receipt.receipt_hash` plus paid `fees.payment_receipt_hash` from referenced files when a base directory is provided.
- Updated `scripts/prepare_receipt_capture.py` to copy receipt/payment evidence files into the output folder, compute their hashes, validate generated receipt evidence with a base directory, and include copied files in artifact manifests.
- Propagated receipt-capture base directories through adapter execution, approved adapter preflight, ready-for-authorized-filing, application-number acceptance, production official evidence gate, and affected benchmark validators.
- Added mock receipt, official file-list, payment receipt, and status snapshot files to receipt/application-number benchmarks where evidence was previously only a placeholder string.
- Replaced stale `sha256:mock...` receipt/file-list/status/docket placeholders in receipt capture, AI self-filing receipt, application-number, and lifecycle benchmarks with real file hashes.
- Synchronized affected `artifact-hashes.json` manifests and lifecycle stage artifact hashes, keeping mock evidence clearly labeled as non-official.
- Updated `SKILL.md` and `test-prompts.json` so receipt capture explicitly requires exact SHA-256 and file-bound receipt/payment evidence.
- Removed generated `.pyc` files for receipt, application-number, lifecycle, production-official, adapter-execution, artifact-manifest, and regression scripts.

Verification:

- `validate_generated_receipt_capture_benchmark.py benchmarks\submitted-pending-receipt-to-official-receipt --json`: passed.
- `validate_receipt_capture_benchmark.py benchmarks\receipt-capture-mock --json`: passed.
- `validate_generated_application_number_benchmark.py benchmarks\official-receipt-to-application-number --json`: passed with expected mock warning.
- `validate_application_number_benchmark.py benchmarks\application-number-acceptance-mock --json`: passed with expected mock warning.
- `validate_generated_receipt_capture_benchmark.py benchmarks\ai-self-filing-submitted-pending-receipt-to-official-receipt --json`: passed.
- `validate_generated_application_number_benchmark.py benchmarks\ai-self-filing-official-receipt-to-application-number --json`: passed with expected mock warning.
- `validate_case_lifecycle_benchmark.py benchmarks\case-lifecycle-trace-mock --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\generated-case-lifecycle-trace --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\ai-self-filing-lifecycle-trace --json`: passed.
- `validate_production_official_evidence_gate_benchmark.py benchmarks\production-official-evidence-gate --json`: passed with expected production-shape warning.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 18:06 +08:00

Karpathy preflight:

- Assumptions: the user wants autonomous local edits, no repeated permission questions, mandatory backups, written change records, and Karpathy-style preflight before each modification.
- Smallest sufficient action: record the new operating rule and snapshot the current application-materials stage work before further edits.
- Evidence check: local project is not a git repository, so file-level backups are required.
- Jagged-intelligence check: AI is strong at repeatable local validation but brittle around official filing/legal boundaries; official submission, signature, payment, receipt, and application number remain hard-stop external-system gates.
- Success criteria: a backup folder exists and this worklog records what changed.
- Stop rule: stop before any real official filing, payment, signature, or destructive filesystem action.

Backup:

- `<skill-root>\backups\20260602-180624-application-materials-stage`

Changes recorded:

- Added patent application materials generation stage for AI self-filing.
- Added `scripts/prepare_patent_application_materials.py`.
- Added `scripts/validate_patent_application_materials.py`.
- Added `scripts/validate_patent_application_materials_benchmark.py`.
- Updated `scripts/build_case_queue.py` to detect `ai-self-filing-application-materials` and route it as `patent_application_materials`.
- Updated `scripts/run_case_queue.py` to run the new benchmark validator and report the next action as official-channel preflight.
- Added `references/application-materials-generation.md`.
- Updated `references/ai-self-filing-gate.md`, `references/case-queue-batch-processor.md`, and `references/case-processor-state-machine.md` to include the materials stage.
- Updated `SKILL.md` and `test-prompts.json` to include the AI self-filing application materials benchmark.
- Generated `benchmarks/ai-self-filing-application-materials/`.
- Generated local queue evidence in `out/ai-self-filing-application-materials-queue.json` and `out/ai-self-filing-application-materials-runner-result.json`.

Verification already run:

- `scripts/prepare_patent_application_materials.py` passed.
- `scripts/validate_patent_application_materials.py` passed.
- `scripts/validate_patent_application_materials_benchmark.py` passed.
- `scripts/validate_artifact_hash_manifest.py` passed for the generated materials benchmark.
- `scripts/build_case_queue.py` generated the materials queue.
- `scripts/run_case_queue.py` passed for the materials queue after rerunning in sequence.

Standing rule added by user:

- Do not ask for permission for future local modifications.
- Before modifications, create a backup.
- Write down what changed.
- Call Karpathy skills before every modification.

## 2026-06-02 18:13 +08:00

Karpathy preflight:

- Assumptions: AI self-filing must not advance from package validation to official-channel preflight unless the application materials bundle is generated and hash-bound.
- Smallest sufficient action: require `application_materials.path` and `application_materials.hash` in AI self-filing official preflight source; validate that bundle before `ready_for_authorized_filing`.
- Evidence check: regression gate failure showed lifecycle hash drift and forbidden scan caught a misleading external-lawyer true-shaped safeguard.
- Jagged-intelligence check: AI is brittle around negative boolean wording; avoid fields that syntactically look like a forbidden true official/legal state.
- Success criteria: focused validators pass and full regression gate returns `ok=true`.
- Stop rule: no official upload, signature, payment, submission, receipt, or application-number state may be created by these local generators.

Backups:

- `<skill-root>\backups\20260602-180733-ready-requires-application-materials`
- `<skill-root>\backups\20260602-181218-doc-test-application-materials-ready`
- `<skill-root>\backups\20260602-181344-regression-fixes-materials-lifecycle`

Changes recorded:

- Updated `scripts/prepare_ready_for_authorized_filing.py` so AI self-filing official preflight requires and validates `application-materials.json` by path and hash.
- Updated `scripts/validate_ready_for_authorized_filing_benchmark.py` to require `application_materials_generation=passed` and `application_materials_hash` for AI self-filing ready status.
- Updated `benchmarks/ai-self-filing-official-ready/official-preflight-source.json` with the materials bundle path and hash.
- Regenerated `benchmarks/ai-self-filing-official-ready/`.
- Renamed the materials safeguard to `external_lawyer_absent=true` to avoid any external-lawyer true-shaped pattern.
- Regenerated `benchmarks/ai-self-filing-application-materials/`.
- Regenerated `benchmarks/ai-self-filing-lifecycle-trace/` after official-ready hash changes.
- Updated `references/ready-for-authorized-filing.md`, `SKILL.md`, and `test-prompts.json` to document the materials bundle as an AI self-filing preflight prerequisite.
- Removed generated pyc files for the scripts touched in this stage.

Verification:

- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_ready_for_authorized_filing_benchmark.py benchmarks\ai-self-filing-official-ready --json`: passed.
- `validate_case_lifecycle_benchmark.py benchmarks\ai-self-filing-lifecycle-trace --json`: passed.
- Forbidden scan for placeholders, secrets, and external-lawyer true-shaped fields: no matches.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=45 failed=0`, `artifact_manifests.total=48 failed=0`, `source_compile.total=88 failed=0`, `json_parse.total=251 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 18:23 +08:00

Karpathy preflight:

- Assumptions: the AI self-filing official-ready gate is only robust if invalid or missing application-materials evidence is explicitly rejected.
- Smallest sufficient action: add one rejection benchmark that mutates `official-preflight-source.json` materials binding fields and expects `prepare_ready_for_authorized_filing.py` to stop.
- Evidence check: the positive materials and ready benchmarks already pass; the missing evidence is a negative benchmark proving the path cannot be bypassed.
- Jagged-intelligence check: AI-generated workflows tend to over-trust happy paths; rejection cases must include missing path, missing hash, hash mismatch, missing file, and wrong artifact type.
- Success criteria: the rejection benchmark passes standalone, routes through the case queue, and is included in full regression.
- Stop rule: no official upload, signature, payment, submission, receipt, or application-number state may be created by rejection tests.

Backup:

- `<skill-root>\backups\20260602-181932-application-materials-ready-rejection`

Changes recorded:

- Added `scripts/validate_ai_self_filing_application_materials_binding_rejection_benchmark.py`.
- Added `benchmarks/ai-self-filing-application-materials-binding-rejection/rejection-cases.json`.
- Added `benchmarks/ai-self-filing-application-materials-binding-rejection/artifact-hashes.json`.
- Updated `scripts/build_case_queue.py` to recognize the new rejection benchmark and route it as `ai_self_filing_application_materials_binding_rejection`.
- Updated `scripts/run_case_queue.py` to run and report the new rejection benchmark.
- Updated `SKILL.md` and `test-prompts.json` with the new rejection benchmark instructions.
- Generated queue evidence in `out\ai-self-filing-application-materials-binding-rejection-queue.json` and `out\ai-self-filing-application-materials-binding-rejection-runner-result.json`.

Verification:

- `validate_ai_self_filing_application_materials_binding_rejection_benchmark.py benchmarks\ai-self-filing-application-materials-binding-rejection --json`: passed.
- `build_case_queue.py benchmarks\ai-self-filing-application-materials-binding-rejection ... --json`: passed.
- `run_case_queue.py out\ai-self-filing-application-materials-binding-rejection-queue.json ... --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\ai-self-filing-application-materials-binding-rejection\artifact-hashes.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=46 failed=0`, `artifact_manifests.total=49 failed=0`, `source_compile.total=89 failed=0`, `json_parse.total=253 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 18:31 +08:00

Karpathy preflight:

- Assumptions: the application materials bundle must be rejected for internal defects before official-channel preflight, even when the upstream package binding exists.
- Smallest sufficient action: add one focused rejection benchmark that mutates `application-materials.json` and expects `validate_patent_application_materials.py` to stop.
- Evidence check: the positive materials benchmark and official-ready binding rejection benchmark already pass; the missing evidence is internal malformed-material rejection.
- Jagged-intelligence check: AI-generated application packages are brittle around metadata completeness, generated document coverage, XML readiness, reference/prior-art provenance, source-package hash binding, and safeguard booleans.
- Success criteria: standalone rejection validator passes, queue builder and runner route it with the correct expected outcome, artifact manifests pass, full regression remains green.
- Stop rule: no official upload, signature, payment, submission, receipt, or application-number state may be created by these local rejection tests.

Backups:

- `<skill-root>\backups\20260602-182559-application-materials-integrity-rejection`
- `<skill-root>\backups\20260602-182559-application-materials-integrity-rejection-connect`

Changes recorded:

- Added `scripts/validate_patent_application_materials_rejection_benchmark.py`.
- Added `benchmarks/patent-application-materials-rejection/rejection-cases.json`.
- Added `benchmarks/patent-application-materials-rejection/artifact-hashes.json`.
- Updated `scripts/build_case_queue.py` to recognize the materials rejection benchmark and route it as `patent_application_materials_rejection`.
- Updated `scripts/run_case_queue.py` to run and report the new rejection benchmark as `patent_application_materials_rejection_passed`.
- Updated `SKILL.md` and `test-prompts.json` with the malformed application-materials rejection instructions.
- Generated queue evidence in `out\patent-application-materials-rejection-queue.json` and `out\patent-application-materials-rejection-runner-result.json`.
- Removed generated pyc files for the scripts touched in this stage.

Verification:

- `validate_patent_application_materials_rejection_benchmark.py benchmarks\patent-application-materials-rejection --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\patent-application-materials-rejection\artifact-hashes.json --json`: passed.
- `build_case_queue.py benchmarks\patent-application-materials-rejection ... --json`: passed with `expected_outcome=patent_application_materials_rejection`.
- `run_case_queue.py out\patent-application-materials-rejection-queue.json ... --json`: passed with `decision=patent_application_materials_rejection_passed`, `official_system_touched=false`, and `official_submission_performed=false`.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 18:58 +08:00

Karpathy preflight:

- Assumptions: `adapter-execution-result.json` and `filing-adapter-response.json` are the evidence boundary for advancing to `submitted_pending_receipt`, so their referenced files must be hash-recomputed, not only shape-checked.
- Smallest sufficient action: add optional base-directory file hash checks to adapter execution result and response validators, then pass base directories from processors and benchmark validators.
- Evidence check: generated adapter-execution benchmarks already had correct file hashes; older static mock/lifecycle benchmarks exposed stale placeholder hashes and were corrected.
- Jagged-intelligence check: AI workflows can copy submitted-pending evidence while referenced request, preflight, receipt-plan, audit, or docket files drift; recomputing those hashes closes the post-adapter evidence gap.
- Success criteria: approved-adapter execution, AI self-filing execution, receipt capture, production official evidence gate, lifecycle trace, artifact manifests, and full regression all pass.
- Stop rule: this stage must not execute an adapter, touch an official system, submit, sign, pay, capture a live receipt, or create an application number.

Backup:

- `<skill-root>\backups\20260602-185220-adapter-execution-file-hash-binding`

Changes recorded:

- Updated `scripts/validate_adapter_execution_result.py` so it recomputes `adapter_request_hash`, `approved_adapter_preflight_hash`, `receipt_capture_plan_hash`, `audit_log_entry_hash`, and `docket_entry_hash` when referenced files are available.
- Updated `scripts/validate_filing_adapter_contract.py` so submitted-pending adapter responses recompute `adapter_execution_result_hash`.
- Updated `scripts/prepare_adapter_execution_result.py`, `scripts/prepare_receipt_capture.py`, `scripts/validate_adapter_execution_benchmark.py`, `scripts/validate_case_processor_benchmark.py`, and `scripts/validate_production_official_evidence_gate.py` to pass base directories into the stronger validators.
- Kept production official evidence shape tests compatible by skipping adjacent file recomputation only for explicit `production_shape_test` / `not_real_official_evidence` shape-test artifacts under `allow_production_shape_test`.
- Added negative mutation checks in `scripts/validate_adapter_execution_benchmark.py` for adapter request, approved preflight, receipt plan, audit, docket, and adapter execution result response hash mismatches.
- Corrected stale placeholder hashes in `benchmarks/adapter-execution-mock-submitted/adapter-execution-result.json` and `benchmarks/adapter-execution-mock-submitted/filing-adapter-response.json`.
- Updated `benchmarks/adapter-execution-mock-submitted/artifact-hashes.json`.
- Updated `benchmarks/case-lifecycle-trace-mock/case-lifecycle-trace.json` and its `artifact-hashes.json` after the adapter execution artifact hash changed.
- Updated `references/adapter-execution-result.md`, `references/filing-adapter-interface.md`, `SKILL.md`, and `test-prompts.json` to document execution-result and response file-hash recomputation.
- Removed generated pyc files for adapter execution, receipt, case-processor, and production-official scripts touched in this stage.

Verification:

- `validate_generated_adapter_execution_result_benchmark.py benchmarks\approved-adapter-to-submitted-pending-receipt --json`: passed.
- `validate_generated_adapter_execution_result_benchmark.py benchmarks\ai-self-filing-adapter-to-submitted-pending-receipt --json`: passed.
- `validate_adapter_execution_benchmark.py benchmarks\adapter-execution-mock-submitted --json`: passed.
- `validate_generated_receipt_capture_benchmark.py benchmarks\submitted-pending-receipt-to-official-receipt --json`: passed.
- `validate_production_official_evidence_gate_benchmark.py benchmarks\production-official-evidence-gate --json`: passed with the expected shape-test warning.
- `validate_case_lifecycle_benchmark.py benchmarks\case-lifecycle-trace-mock --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\adapter-execution-mock-submitted\artifact-hashes.json --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\case-lifecycle-trace-mock\artifact-hashes.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 18:46 +08:00

Karpathy preflight:

- Assumptions: the filing adapter request is the real execution input, so its referenced preflight/readiness/session hashes must be recomputed from files, not merely checked for `sha256:` shape.
- Smallest sufficient action: extend `validate_filing_adapter_contract.py` with optional base-directory hash checks for approved-adapter requests and pass base directories from affected generators/benchmarks.
- Evidence check: existing generated approved-adapter benchmarks had valid hashes; one older static approved-adapter benchmark exposed a stale preflight hash and was corrected.
- Jagged-intelligence check: AI workflows can copy approved-preflight strings into adapter requests while the referenced file drifts; recomputing the file hash at the request boundary closes that execution-path gap.
- Success criteria: adapter request validation passes for positive benchmarks, mutated request hashes fail inside `validate_approved_adapter_benchmark.py`, full regression remains green, and no official system is touched.
- Stop rule: no adapter execution, official upload, signature, payment, submission, receipt, or application-number state may be created.

Backup:

- `<skill-root>\backups\20260602-184420-adapter-request-preflight-hash-binding`

Changes recorded:

- Updated `scripts/validate_filing_adapter_contract.py` so approved-adapter request validation recomputes `approved_adapter_preflight_hash`, `adapter_production_readiness_hash`, and `official_session_authorization_hash` when file paths are available.
- Updated `scripts/prepare_approved_adapter_preflight.py`, `scripts/prepare_adapter_execution_result.py`, `scripts/validate_case_processor_benchmark.py`, and `scripts/validate_approved_adapter_benchmark.py` to pass base directories into adapter request validation.
- Added negative mutation checks in `scripts/validate_approved_adapter_benchmark.py` for approved-preflight, production-readiness, and official-session hash mismatches.
- Corrected `benchmarks/approved-adapter-preflight-ready/filing-adapter-request.json` from stale `sha256:approved-adapter-preflight-v1` to the actual approved-preflight file hash.
- Updated `benchmarks/approved-adapter-preflight-ready/artifact-hashes.json` for the changed adapter request.
- Updated `references/filing-adapter-interface.md`, `SKILL.md`, and `test-prompts.json` to document adapter-request file-hash recomputation.
- Removed generated pyc files for adapter and case-processor scripts touched in this stage.

Verification:

- `validate_filing_adapter_contract.py request benchmarks\official-ready-to-approved-adapter-preflight\filing-adapter-request.json --json`: passed.
- `validate_approved_adapter_benchmark.py benchmarks\approved-adapter-preflight-ready --json`: passed.
- `validate_generated_approved_adapter_preflight_benchmark.py benchmarks\official-ready-to-approved-adapter-preflight --json`: passed.
- `validate_generated_approved_adapter_preflight_benchmark.py benchmarks\ai-self-filing-approved-adapter-preflight --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\approved-adapter-preflight-ready\artifact-hashes.json --json`: passed.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 18:41 +08:00

Karpathy preflight:

- Assumptions: `official_material_inventory` must be a source-bound copy of the validated filing package manifest, not an independently editable list inside `application-materials.json`.
- Smallest sufficient action: have `validate_patent_application_materials.py` read `source_package.package_dir/filing-package-manifest.yaml`, verify its hash, validate the manifest, and compare canonical official document entries against `official_material_inventory`.
- Evidence check: the positive materials benchmark already has the correct manifest-derived inventory; rejection coverage must prove filename/hash/source-manifest tampering fails.
- Jagged-intelligence check: AI workflows can preserve a correct source manifest hash while drifting a copied inventory field; canonical comparison closes that gap before official-channel preflight.
- Success criteria: positive materials benchmark, malformed-materials rejection benchmark, queue evidence, manifest checks, and full regression all pass.
- Stop rule: no official upload, signature, payment, submission, receipt, or application-number state may be created.

Backup:

- `<skill-root>\backups\20260602-183720-official-inventory-source-binding`

Changes recorded:

- Updated `scripts/validate_patent_application_materials.py` to validate the source filing package manifest, verify `source_package.filing_package_manifest_hash`, require official inventory fields, detect duplicate official document types, and compare canonical official inventory entries against the source manifest.
- Updated `scripts/validate_patent_application_materials_rejection_benchmark.py` so rejection cases can mutate document-list entries by type.
- Added official inventory missing-filename, official inventory source-manifest mismatch, and source manifest hash mismatch cases to `benchmarks/patent-application-materials-rejection/rejection-cases.json`.
- Updated `benchmarks/patent-application-materials-rejection/artifact-hashes.json` for the changed rejection spec.
- Updated `SKILL.md` and `test-prompts.json` so application-materials generation and rejection checks explicitly cover source-manifest-bound official inventory.
- Regenerated queue evidence in `out\patent-application-materials-rejection-queue.json` and `out\patent-application-materials-rejection-runner-result.json`.
- Removed generated pyc files for scripts touched in this stage.

Verification:

- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_patent_application_materials_rejection_benchmark.py benchmarks\patent-application-materials-rejection --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\patent-application-materials-rejection\artifact-hashes.json --json`: passed.
- `build_case_queue.py benchmarks\patent-application-materials-rejection ... --json`: passed with `expected_outcome=patent_application_materials_rejection`.
- `run_case_queue.py out\patent-application-materials-rejection-queue.json ... --json`: passed with `decision=patent_application_materials_rejection_passed`, `official_system_touched=false`, and `official_submission_performed=false`.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.

## 2026-06-02 18:36 +08:00

Karpathy preflight:

- Assumptions: `document-generation-plan.json` is part of the generated application-materials evidence and must not be optional or unbound.
- Smallest sufficient action: require `document_generation_plan` in `application-materials.json`, validate its path/hash, and add two rejection cases for missing and hash-mismatched plans.
- Evidence check: the positive `ai-self-filing-application-materials` benchmark already includes the plan, so this should harden validation without changing generation output.
- Jagged-intelligence check: AI systems can generate plausible final documents while losing the plan that explains source binding; the plan must be hash-bound like request metadata and XML readiness.
- Success criteria: positive materials benchmark still passes, malformed-materials rejection benchmark passes with the new cases, queue evidence passes, and full regression remains green.
- Stop rule: no official upload, signature, payment, submission, receipt, or application-number state may be created.

Backup:

- `<skill-root>\backups\20260602-183220-document-generation-plan-binding`

Changes recorded:

- Updated `scripts/validate_patent_application_materials.py` to require and hash-validate `document_generation_plan`.
- Added missing-plan and hash-mismatch cases to `benchmarks/patent-application-materials-rejection/rejection-cases.json`.
- Updated `benchmarks/patent-application-materials-rejection/artifact-hashes.json` for the changed rejection spec.
- Updated `SKILL.md` and `test-prompts.json` so application-materials generation and rejection checks explicitly cover the document generation plan.
- Regenerated queue evidence in `out\patent-application-materials-rejection-queue.json` and `out\patent-application-materials-rejection-runner-result.json`.

Verification:

- `validate_patent_application_materials_rejection_benchmark.py benchmarks\patent-application-materials-rejection --json`: passed.
- `validate_patent_application_materials_benchmark.py benchmarks\ai-self-filing-application-materials --json`: passed.
- `validate_artifact_hash_manifest.py benchmarks\patent-application-materials-rejection\artifact-hashes.json --json`: passed.
- `build_case_queue.py benchmarks\patent-application-materials-rejection ... --json`: passed with `expected_outcome=patent_application_materials_rejection`.
- `run_case_queue.py out\patent-application-materials-rejection-queue.json ... --json`: passed with `decision=patent_application_materials_rejection_passed`, `official_system_touched=false`, and `official_submission_performed=false`.
- `run_regression_gate.py --output-dir out\regression-gate --json`: `ok=true`, `folder_validators.total=47 failed=0`, `artifact_manifests.total=50 failed=0`, `source_compile.total=90 failed=0`, `json_parse.total=255 failed=0`, `forbidden_scans.total=2 failed=0`, `official_system_touched=false`, `official_submission_performed=false`, `external_lawyer_involved=false`.
- `validate_artifact_hash_manifest.py out\regression-gate\artifact-hashes.json --json`: passed.


