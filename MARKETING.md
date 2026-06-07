# GitHub Launch Kit

This is the GitHub-facing marketing kit for Patent Capital OS. It is written for the repository itself: README positioning, repo description, topics, release language, issue/discussion conversion, adopter evidence, and maintainer credibility.

The goal is to make a developer, GPT builder, or agent engineer understand the project in 30 seconds, trust the boundary claims in 3 minutes, and run or star the repository in 10 minutes.

For the deeper strategic reasoning behind this kit, see `docs/github-marketing-strategy.md`.

## Repository Positioning

Patent Capital OS is an open-source Codex skill for evidence-bound patent workflow automation.

It turns patent invention materials into local, hash-bound pre-submission handoff packages through intake, draft generation, reference-patent delta analysis, AI legal/compliance gates, quality review, batch indexing, and completion audit.

It deliberately stops before real official filing.

## GitHub One-Liner

Use this as the repository description:

```text
Evidence-bound Codex skill for patent intake, AI legal/compliance gates, application-material generation, quality review, and read-only pre-submission handoff.
```

Shorter variant:

```text
Open-source patent workflow skill with legal/compliance gates, hash-bound artifacts, validators, and no fake official filing.
```

## GitHub Topics

Recommended topics:

```text
ai-agents
ai-workflows
codex-skill
gpt-skills
ip
legal-compliance
legaltech
open-source
patent
patent-automation
patent-workflow
workflow-automation
```

Keep topics specific. Avoid vague tags that attract the wrong audience.

## README First Screen

The top of the README should answer four questions immediately:

- What is it?
- Who is it for?
- What can it run locally?
- What does it refuse to claim?

Recommended first-screen copy:

```markdown
# Patent Capital OS

Patent Capital OS is an open-source Codex skill for evidence-bound patent workflow automation.

It helps developers and GPT builders turn invention materials into local, hash-bound pre-submission handoff packages with intake, patent draft generation, reference-patent delta analysis, AI legal/compliance gates, quality review, batch indexing, and completion audit.

It does not perform real official patent filing by default. The local closed loop stops at `approved_for_adapter_execution` / `handoff_ready_no_auto_submit`.
```

## Why Developers Should Care

This project should be marketed on GitHub as an engineering artifact, not as a legal shortcut.

Developer-facing value:

- A real example of a serious Codex skill with scripts, templates, references, schemas, benchmarks, and CI.
- A reusable pattern for agent workflows that need hard stop conditions and audit evidence.
- A patent-domain workflow that shows how AI systems can generate useful artifacts without faking legal authority.
- A validation-heavy architecture with hash-bound artifacts and rejection benchmarks.
- A public maintainer model that does not exaggerate adoption.

## What Makes It Different

Use these as GitHub bullets:

- Not a prompt pack: it is a workflow skill with executable local scripts.
- Not an AI lawyer: it keeps AI legal/compliance review separate from legal advice.
- Not an auto-filing bot: it does not log in, upload, sign, pay, submit, capture receipts, or claim application numbers.
- Not a demo-only folder: it includes validators, benchmark fixtures, runbooks, and regression gates.
- Not a black box: it records work in `WORKLOG.md` and keeps source artifacts hash-bound.

## GitHub Conversion Path

The repository should move visitors through this path:

1. Read the README first screen.
2. See the explicit no-official-submission boundary.
3. Run a smoke command or inspect benchmark fixtures.
4. Star the repo if the architecture is useful.
5. Open an issue for a workflow gap, docs request, or integration idea.
6. Submit an adopter report only after real usage exists.

Primary GitHub calls to action:

- "Run the local smoke workflow."
- "Open an issue for a patent workflow gap."
- "Use `ADOPTERS.md` only for real public usage evidence."
- "Star the repo if the skill architecture is useful."

## README Sections To Keep Sharp

Keep these sections short and strong:

- Project Status
- Core Capabilities
- Explicit Boundary
- Quick Start
- Verification Status
- Maintainer Evidence

Avoid turning the README into a sales page. GitHub users want proof, commands, files, and clear constraints.

## Release Copy

Use this template for GitHub releases:

```markdown
## Patent Capital OS vX.Y.Z

This release improves the local patent skill workflow from invention-material intake to read-only pre-submission handoff.

### Highlights

- [Capability]
- [Validator or benchmark]
- [Documentation or runbook]

### Boundary

This release does not perform official login, upload, signature, fee payment, submission, receipt capture, or application-number issuance.

### Verification

- `python -m json.tool test-prompts.json`
- `python -m py_compile ...`
- `[focused validator command]`
- `[CI or regression result]`
```

## Issue Strategy

Use issues as public evidence of active maintenance.

Recommended labels:

- `good first issue`
- `documentation`
- `benchmark`
- `validator`
- `workflow`
- `legal-boundary`
- `patent-domain`
- `help wanted`

Recommended first public issues:

- Add a compact architecture diagram to the README.
- Add a minimal sample inbox fixture for new users.
- Document the difference between draft generation, handoff readiness, and official submission.
- Add a validator map showing which scripts guard which workflow boundaries.
- Add a contributor guide section for creating rejection benchmarks.

## Discussion Prompts

Use GitHub Discussions to attract the right people:

- "What makes a patent workflow skill trustworthy enough for local use?"
- "Where should AI patent drafting stop before legal or official authority is required?"
- "What benchmark fixtures would make this skill easier to evaluate?"
- "Which agent workflow patterns from this repo are reusable outside patent operations?"

## Adopter Evidence

Do not claim broad usage before it exists.

Good adopter evidence:

- public issue from a real user
- public discussion with workflow feedback
- public fork that integrates the skill
- public demo using the repository
- public entry in `ADOPTERS.md`

Bad adopter evidence:

- private praise without permission
- assumed users from traffic
- fake testimonials
- unverified "many people rely on this" claims

## GitHub Profile Copy

Use this for Cyrus Sheng's profile:

```markdown
I am the primary maintainer of Patent Capital OS, an open-source Codex skill for evidence-bound patent workflow automation.

The project focuses on local patent intake, draft generation, AI legal/compliance gates, application-material preparation, quality review, hash-bound handoff packages, and regression-tested stop boundaries before official filing.
```

## Pinned Repository Note

When pinning the repo on the GitHub profile, use this mental model:

```text
Patent Capital OS = serious AI workflow infrastructure for patent operations, not a legal shortcut.
```

## Star Pitch

Use this line when asking technical audiences to star the repo:

```text
Star it if you want a concrete example of how to build AI agent workflows with legal/compliance gates, hash-bound artifacts, rejection benchmarks, and honest stop conditions.
```

## Pull Request Pitch

Use this line when inviting contributors:

```text
Contributions are welcome around validators, benchmark fixtures, documentation, sample workflows, and safer patent-domain automation boundaries.
```

## GitHub SEO Keywords

Use these terms naturally in README, release notes, and issue titles:

- patent workflow automation
- patent application materials
- Codex skill
- GPT skill
- AI agent workflow
- legal compliance gate
- AI legal compliance
- patent drafting workflow
- prior art delta
- claim support map
- hash-bound artifacts
- pre-submission handoff
- regression-tested AI workflow

## What Not To Say

Do not use these claims on GitHub:

- "AI lawyer"
- "automatic patent filing"
- "guaranteed patent approval"
- "officially submitted"
- "lawyer-reviewed" unless there is real evidence
- "many companies use this" unless public evidence exists
- "bypass patent agents"
- "bypass CNIPA controls"

## Maintainer Rhythm For GitHub

Weekly:

- Triage new issues and label them.
- Add one small documentation or benchmark improvement.
- Publish a short maintainer note when there is meaningful progress.
- Keep `ADOPTERS.md` honest.
- Keep `ROADMAP.md` current.

Monthly:

- Cut a small release if changes are meaningful.
- Review README first screen and repo topics.
- Open or close roadmap issues based on actual feedback.
- Record public evidence in `docs/maintainer-application-evidence.md`.

## Success Criteria

The GitHub marketing is working when:

- A developer can explain the project accurately after reading the README.
- A GPT builder understands the skill architecture and stop boundaries.
- Issues and discussions ask about real workflow integrations rather than fake filing.
- Stars, forks, and adopter reports grow from public technical trust.
- Cyrus Sheng is visibly the active primary maintainer without overstating adoption.
