# Patent Capital OS

Patent Capital OS is a production-style Codex skill for patent intake, draft generation, AI legal/compliance gating, application-material preparation, quality review, and read-only pre-submission handoff.

It is designed for Chinese patent workflow prototyping and enterprise IP operations. The current repository closes the local skill loop from received materials to `approved_for_adapter_execution` / `handoff_ready_no_auto_submit` and intentionally stops before real official submission.

## Project Status

Patent Capital OS is an early public open-source project maintained by Cyrus Sheng ([@ares20041129-jpg](https://github.com/ares20041129-jpg)). It has a complete local workflow loop, benchmark evidence, and regression gates. Public adoption is tracked honestly in `ADOPTERS.md`; the project does not claim broad ecosystem reliance until public evidence exists.

## What This Repository Contains

- `SKILL.md`: the primary skill contract and workflow router
- `scripts/`: generators, orchestrators, validators, queue runners, and regression gates
- `references/`: operational doctrine, workflow references, legal/compliance boundaries, and runbooks
- `assets/templates/`: canonical packet and report templates
- `schemas/`: structured packet schemas
- `benchmarks/`: positive and rejection benchmark fixtures
- `agents/`: UI-facing metadata for the skill
- `WORKLOG.md`: change log with preflight and verification evidence
- `MAINTAINERS.md`: primary/core maintainer record
- `GOVERNANCE.md`: project decision and review model
- `ADOPTERS.md`: public adoption evidence tracker
- `ROADMAP.md`: public roadmap
- `MARKETING.md`: developer and GPT-builder launch strategy

## Core Capabilities

- Raw invention-material intake and case packaging
- Invention-disclosure normalization and confirmation
- Reference-patent delta generation for cited patent sets
- Draft package generation and claim-support mapping
- Evidence provenance and abnormal filing risk assessment
- AI self-filing legal/compliance gate with `external_lawyer_involved=false`
- Application-material generation and independent quality review
- Pre-submission pipeline orchestration
- Read-only handoff package generation
- Batch inbox processing, handoff indexing, and completion audit
- Queue validation and full regression validation

## Explicit Boundary

This repository does **not** perform real official filing by default.

The closed-loop local outputs must keep:

- `official_system_touched=false`
- `official_submission_performed=false`
- `external_lawyer_involved=false` on the default AI-only route

The repository does not claim:

- official login
- upload
- electronic signature
- fee payment
- official submission
- receipt capture
- application-number issuance

## Quick Start

### Requirements

- Python 3.10+
- `PyYAML`

Install:

```bash
python -m pip install -r requirements.txt
```

### 1. Run a batch inbox to handoff

```bash
python -X utf8 scripts/orchestrate_inbox_to_handoff.py inbox --output-dir out/inbox-to-handoff --inbox-id INBOX-001 --confirmation-packet-template assets/templates/disclosure-confirmation-packet.json --ai-self-filing-source-template assets/templates/ai-self-filing-source.json --json
```

### 2. Build the final handoff index

```bash
python -X utf8 scripts/prepare_inbox_handoff_index.py out/inbox-to-handoff --output-dir out/inbox-handoff-index --index-id INBOX-HANDOFF-INDEX-001 --json
python -X utf8 scripts/validate_inbox_handoff_index_benchmark.py out/inbox-handoff-index --json
```

### 3. Build the local completion audit

```bash
python -X utf8 scripts/prepare_skill_completion_audit.py --skill-root . --output-dir out/skill-completion-audit --json
python -X utf8 scripts/validate_skill_completion_audit_benchmark.py out/skill-completion-audit --json
```

### 4. Run the regression gate

```bash
python -X utf8 scripts/run_regression_gate.py --output-dir out/regression-gate --json
python -X utf8 scripts/validate_artifact_hash_manifest.py out/regression-gate/artifact-hashes.json --json
```

## Recommended Reading Order

1. `SKILL.md`
2. `references/production-intake-runbook.md`
3. `references/workflow-orchestration.md`
4. `references/production-architecture.md`
5. `MAINTAINERS.md`
6. `GOVERNANCE.md`
7. `WORKLOG.md`

## Repository Layout

```text
patent-capital-os/
  agents/
  assets/
  benchmarks/
  references/
  schemas/
  scripts/
  SKILL.md
  WORKLOG.md
  test-prompts.json
```

## GitHub Publishing Notes

- `benchmarks/` is part of the repository contract and should stay versioned.
- `out/` and `backups/` are local working artifacts and are ignored by `.gitignore`.
- The project is licensed under Apache-2.0.
- Review `SECURITY.md` before enabling issues, PRs, or public contribution.
- Keep `ADOPTERS.md` truthful. Do not claim heavy usage until public evidence exists.

## Maintainer Evidence

For applications or reviews that ask whether the maintainer is active in open source, see:

- `MAINTAINERS.md`
- `GOVERNANCE.md`
- `WORKLOG.md`
- `MARKETING.md`
- `docs/maintainer-application-evidence.md`

## Verification Status

The local skill loop has already passed full regression and closes at the read-only handoff boundary, not at official submission.

See:

- `references/production-intake-runbook.md`
- `references/regression-gate.md`
- `WORKLOG.md`
