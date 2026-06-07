# Security Policy

Patent Capital OS operates in a legal/compliance-sensitive domain. Treat all changes as potentially high impact.

## Scope of Security Here

Security in this repository includes:

- unsafe path handling
- silent output tampering
- hash-binding bypass
- privilege or authority confusion
- forged filing-state escalation
- accidental official-system automation
- false claims of lawyer review, receipt, or application number

## Supported Boundary

The repository's default supported boundary is local, read-only, pre-submission workflow generation and validation.

Safe default expectations:

- `official_system_touched=false`
- `official_submission_performed=false`
- `external_lawyer_involved=false` on the AI-only route

## Reporting a Problem

Do not open a public issue for:

- real credentials
- official-account data
- sensitive applicant materials
- exploitable path or hash bypasses
- anything that could enable unauthorized filing actions

Instead, report privately through the maintainer-approved channel for the repository.

## High-Risk Change Areas

Pay extra attention to:

- `scripts/validate_*`
- `scripts/prepare_*`
- `scripts/orchestrate_*`
- `references/filing-execution-boundary.md`
- `references/legal-gates.md`
- `references/production-architecture.md`

## Release Hygiene

Before publishing a release or pushing public changes:

1. Confirm no local credentials or applicant-sensitive files are present.
2. Confirm `out/` and `backups/` are not staged.
3. Run the regression gate.
4. Recheck that no generated artifact claims real official submission without evidence.
