# GitHub Marketing Strategy

This document is the strategic thinking layer behind the Patent Capital OS GitHub launch. `MARKETING.md` is the execution kit; this file explains the reasoning, audience architecture, trust model, narrative system, growth loops, metrics, and guardrails.

## Executive Thesis

Patent Capital OS should not be marketed as "AI writes patents" or "AI files patents." That attracts the wrong users, creates legal-risk confusion, and weakens trust with serious developers.

The strongest GitHub positioning is:

```text
Patent Capital OS is an evidence-bound open-source Codex skill that shows how serious AI workflows can operate in a legally sensitive domain without faking authority, legal review, or official filing.
```

The project wins attention by being unusually disciplined:

- it has a real patent-domain workflow;
- it has executable local scripts, validators, templates, schemas, and benchmarks;
- it has explicit legal/compliance gates;
- it proves local outputs stop before official filing;
- it is transparent about maintainer status and adoption evidence.

The core marketing idea is not hype. It is engineering trust.

## Strategic Source Base

This strategy follows current GitHub and open-source credibility mechanics:

- GitHub says a README should explain what the project does, why it is useful, how users get started, where to get help, and who maintains it: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- GitHub topics help people find projects by purpose, subject area, community, and important qualities: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- GitHub Discussions are designed for open-ended community conversation, Q&A, announcements, and decisions around a project: https://docs.github.com/en/discussions
- OpenSSF Best Practices Badge frames public open-source trust as visible best-practice evidence, not private claims: https://openssf.org/projects/best-practices-badge/

## Strategic Constraints

These constraints are part of the marketing strategy, not merely compliance notes:

- Do not claim legal advice.
- Do not claim lawyer or patent-agent review unless real evidence exists.
- Do not claim official submission, receipt, acceptance, or application number from local outputs.
- Do not claim broad adoption until public evidence exists.
- Do not position the project as a way to bypass patent agents, legal review, CNIPA controls, account authority, signatures, fees, captchas, or official systems.
- Do not turn the README into a sales page; GitHub users want proof, commands, files, and constraints.

The trust boundary is the differentiator. Many AI projects market what they can generate. Patent Capital OS should market what it can generate and what it refuses to fake.

## Audience Architecture

### Tier 1: GPT And Agent Builders

Job to be done:

- Learn how to structure a serious skill with tools, templates, validators, references, and stop conditions.

Why they care:

- The project is a concrete pattern for agent workflows in high-stakes domains.

Message:

```text
Study this if you are building GPT/agent workflows that need evidence, validation, and hard stop conditions.
```

Best GitHub proof:

- `SKILL.md`
- `scripts/`
- `benchmarks/`
- `test-prompts.json`
- `WORKLOG.md`

### Tier 2: Python Workflow Developers

Job to be done:

- Inspect or reuse a workflow automation pattern with validation gates.

Why they care:

- The repository is scriptable, local, and testable.

Message:

```text
This is a local workflow engine for patent operations, with validators and regression fixtures you can inspect.
```

Best GitHub proof:

- Quick Start commands
- validator scripts
- benchmark fixtures
- CI status

### Tier 3: Legaltech And IP Operations Builders

Job to be done:

- Understand where AI can help patent operations without pretending to replace legal authority.

Why they care:

- The project speaks in real patent workflow objects: disclosures, claim support, legal gates, handoff packages, docket/audit concepts.

Message:

```text
This is not an AI lawyer. It is an auditable local pre-submission workflow for patent operations.
```

Best GitHub proof:

- explicit boundary section
- legal/compliance gate references
- handoff package workflow
- completion audit

### Tier 4: Open-Source Reviewers And Maintainer Programs

Job to be done:

- Decide whether the maintainer is credible, active, and transparent.

Why they care:

- Applications for maintainer status or ecosystem programs need public evidence.

Message:

```text
Cyrus Sheng is the active primary maintainer of a public open-source project with governance, issues, roadmap, releases, and CI.
```

Best GitHub proof:

- `MAINTAINERS.md`
- `GOVERNANCE.md`
- `ROADMAP.md`
- open issues
- commit history
- release history
- CI

## Category Design

Do not create a category called "AI patent filing." It is risky and inaccurate.

Use this category:

```text
evidence-bound patent workflow automation
```

Adjacent categories:

- AI agent workflow infrastructure
- legal/compliance-aware automation
- patent operations tooling
- GPT skill architecture
- local pre-submission handoff automation

Category enemy:

```text
unverifiable AI legal automation that blurs draft, review, and official submission
```

Category promise:

```text
AI can produce useful patent-operation artifacts when every stage is source-bound, validator-backed, and honest about authority boundaries.
```

## Narrative Architecture

Use a three-layer narrative.

### Layer 1: Plain English

```text
Patent Capital OS turns invention materials into local, hash-bound patent handoff packages.
```

### Layer 2: Developer Trust

```text
It uses scripts, schemas, templates, validators, benchmarks, and CI to make the workflow inspectable and reproducible.
```

### Layer 3: Boundary Credibility

```text
It deliberately stops before real official filing and records that no official system was touched.
```

This narrative should appear in README, release notes, issues, profile copy, and discussion prompts.

## GitHub Surface Strategy

### README

Purpose:

- convert an unknown visitor into an informed technical reader.

First-screen requirements:

- clear one-sentence positioning;
- target audience;
- concrete local output;
- explicit stop boundary;
- link to Quick Start.

Do not hide the boundary below the fold. It is part of the value proposition.

### Repository Description

Purpose:

- make GitHub search and profile cards self-explanatory.

Current description:

```text
Evidence-bound Codex skill for patent intake, AI legal/compliance gates, application-material generation, quality review, and read-only pre-submission handoff.
```

### Topics

Purpose:

- classify the repository for discovery and contribution.

Strategic topic groups:

- agent/GPT: `ai-agents`, `ai-workflows`, `codex-skill`, `gpt-skills`
- patent/IP: `patent`, `patent-automation`, `patent-workflow`, `ip`
- trust/legaltech: `legal-compliance`, `legaltech`
- OSS/workflow: `open-source`, `workflow-automation`

### Issues

Purpose:

- prove active maintenance and create contribution handles.

Issue strategy:

- every issue should be real work;
- labels should make the repo navigable;
- good first issues should reduce onboarding risk;
- legal-boundary issues should preserve trust.

### Discussions

Purpose:

- separate open-ended questions from scoped implementation work.

Discussion categories should eventually support:

- Q&A
- Ideas
- Announcements
- Use cases
- Benchmark requests

### Releases

Purpose:

- create a public rhythm of meaningful progress.

Every release should include:

- capabilities changed;
- validators or benchmarks changed;
- boundary statement;
- verification commands;
- known limitations.

## Trust Flywheel

The GitHub growth engine is a trust flywheel:

1. Clear positioning brings the right technical audience.
2. Explicit boundaries prevent low-quality or risky expectations.
3. Runnable commands create proof.
4. Validators and benchmarks create confidence.
5. Issues and discussions create public interaction.
6. Public fixes and releases create maintainer evidence.
7. Adoption entries and citations create credibility.
8. Better credibility attracts better contributors and users.

The flywheel breaks if the project exaggerates legal authority, adoption, or official filing capability.

## Content System

Use three content types inside GitHub.

### Proof Content

Purpose:

- show that the project works and has boundaries.

Examples:

- regression result notes;
- benchmark summaries;
- validator maps;
- handoff package examples;
- architecture diagram.

### Teaching Content

Purpose:

- help GPT/agent builders learn from the architecture.

Examples:

- "How the legal/compliance gate works"
- "Why reference patents are boundary evidence, not applicant support"
- "How rejection benchmarks prevent unsafe workflow drift"
- "How to design a skill that stops before official action"

### Participation Content

Purpose:

- turn observers into contributors.

Examples:

- good first issues;
- discussion prompts;
- benchmark fixture requests;
- docs improvement tasks;
- adopter report template.

## 90-Day GitHub Plan

### Days 0-7: Trust Foundation

- Keep README first screen sharp.
- Keep topics and description aligned.
- Open starter issues.
- Add architecture diagram.
- Add minimal sample fixture issue or PR.
- Make the boundary section impossible to miss.

### Days 8-30: Developer Comprehension

- Publish validator map.
- Add sample run outputs.
- Improve Quick Start to reduce first-run friction.
- Add discussion prompts.
- Turn repeated questions into docs.
- Cut a small release with release notes.

### Days 31-60: Proof Of Activity

- Close starter issues through small PRs.
- Add more rejection benchmarks.
- Add maintainer notes.
- Add one real demo fixture.
- Track stars, forks, issues, discussions, and cloners without overstating them.

### Days 61-90: Credibility Expansion

- Apply for or prepare OpenSSF Best Practices Badge criteria if the project fits.
- Publish a public article or discussion explaining the evidence-bound pattern.
- Invite careful feedback from agent builders and legaltech builders.
- Add adopter entries only when public usage is real.
- Package a clearer release if the workflow surface improves.

## Metrics

### Leading Indicators

- README visits
- profile visits
- stars
- forks
- issue views
- discussion views
- unique cloners
- first-time contributor comments

### Quality Indicators

- issues asking about real workflow integration;
- contributors referencing actual files;
- discussions about validators, handoff, or boundaries;
- external links that describe the project accurately.

### Trust Indicators

- no false adopter claims;
- no unresolved confusion around official submission;
- no issues asking how to bypass official controls;
- CI stays green;
- release notes include boundaries and verification.

### Maintainer-Credibility Indicators

- steady commits;
- issues triaged;
- PRs reviewed;
- roadmap updated;
- worklog maintained;
- releases created when changes are meaningful.

## Experiment Backlog

Run small experiments and keep what creates technical trust:

- README A/B copy through commit history and traffic observation.
- Add architecture diagram and compare issue quality.
- Add sample fixture and track clones/stars after release.
- Pin a discussion asking for benchmark requests.
- Add a validator map and watch whether questions become more specific.
- Create a release focused only on "trust infrastructure" and measure response.

Do not run paid ads until the README, demo fixture, and contribution path are strong enough to convert cold technical traffic.

## Risk Register

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Users think it files patents | Creates legal and trust risk | Put boundary in README, release notes, issues, and docs |
| Users think AI gate is legal advice | Misstates authority | Use "AI legal/compliance gate" and explicit no-legal-advice language |
| Project looks inactive | Weakens maintainer credibility | Maintain issues, releases, roadmap, and worklog |
| Too much marketing, not enough proof | Developers disengage | Lead with commands, validators, benchmarks, and files |
| Fake adoption temptation | Destroys trust | Use `ADOPTERS.md` only for public evidence |
| Domain looks too narrow | Limits audience | Explain reusable agent workflow patterns |
| Domain looks too risky | Scares contributors | Emphasize local, no-official-submission boundary |

## Claim Matrix

| Claim | Allowed? | Evidence Required |
| --- | --- | --- |
| Open-source Codex skill | Yes | Public repository and `SKILL.md` |
| Patent workflow automation | Yes | scripts, references, templates, benchmarks |
| AI legal/compliance gate | Yes | gate docs and validators |
| Legal advice | No | Never claim |
| Lawyer-reviewed | Only with real evidence | reviewer record and version hash |
| Official submission | No for local loop | official receipt/evidence would be required |
| Application number received | No for local loop | official application-number evidence required |
| Broadly used | Not yet | public adopters, forks, citations, integrations |
| Active primary maintainer | Yes | commits, issues, releases, maintainer docs |

## Maintainer Operating Model

Weekly:

- triage issues;
- answer or organize discussions;
- improve one docs or benchmark item;
- keep roadmap honest;
- avoid unsupported adoption claims.

Monthly:

- review GitHub traffic and issue quality;
- cut a release if meaningful changes shipped;
- update maintainer evidence;
- check README first-screen clarity;
- review OpenSSF/security readiness.

Quarterly:

- review category positioning;
- evaluate whether adoption evidence supports stronger claims;
- decide whether to expand beyond GitHub into external channels;
- retire or rewrite messaging that attracts wrong users.

## Strategic Checklist

The strategy is working when all of these are true:

- The README explains the project, usefulness, quick start, help path, and maintainer, matching GitHub README guidance.
- Topics classify the repository by purpose, domain, and community.
- Discussions are available for open-ended community conversation.
- Issues are scoped and labeled for real contribution.
- The project never markets local workflow outputs as official filing.
- The maintainer can point to public evidence of activity.
- Developers can reuse the skill architecture even if they do not work in patent operations.
- Legaltech/IP readers can trust the boundary language.
- Adoption claims remain evidence-bound.
