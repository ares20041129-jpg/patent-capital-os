# GitHub Publishing Checklist

Use this checklist when preparing Patent Capital OS for a GitHub repository.

## Repository Readiness

- [ ] `README.md` accurately describes the current repository boundary
- [ ] `CONTRIBUTING.md` and `SECURITY.md` are present
- [ ] `LICENSE` and `NOTICE` are present
- [ ] `MAINTAINERS.md` names the public primary/core maintainer
- [ ] `GOVERNANCE.md` explains the maintainer model
- [ ] `ADOPTERS.md` avoids unsupported usage claims
- [ ] `MARKETING.md` explains the developer and GPT-builder launch plan
- [ ] `.gitignore` excludes `out/`, `backups/`, and local zip exports
- [ ] `requirements.txt` matches the actual runtime dependency surface
- [ ] no secrets, credentials, or applicant-private materials are present
- [ ] no generated artifact falsely claims real official submission

## Content Review

- [ ] `SKILL.md` still matches the implemented workflow
- [ ] `references/production-intake-runbook.md` still matches the recommended commands
- [ ] `WORKLOG.md` includes the latest material changes and verification notes
- [ ] `test-prompts.json` still reflects the supported benchmark prompts

## Validation

- [ ] narrow validators for changed workflows have passed
- [ ] `python -X utf8 scripts/run_regression_gate.py --output-dir out/regression-gate --json` passed
- [ ] `python -X utf8 scripts/validate_artifact_hash_manifest.py out/regression-gate/artifact-hashes.json --json` passed

## GitHub Setup

- [ ] choose repository visibility deliberately
- [ ] make the repository public when ready
- [ ] keep the maintainer GitHub profile public
- [ ] link the project from the maintainer profile
- [ ] decide whether benchmark artifacts should remain committed as contract evidence
- [ ] add maintainers and review rules
- [ ] enable issues only after confirming the security reporting path
- [ ] enable GitHub Actions and confirm CI passes
- [ ] add repository topics such as `patent`, `ip`, `ai-workflows`, `codex-skill`, `legaltech`, `workflow-automation`

## Recommended First Commit Shape

- repository docs
- license and governance files
- `SKILL.md`
- `scripts/`
- `references/`
- `assets/`
- `schemas/`
- `benchmarks/`
- `test-prompts.json`

Do not include local `out/`, local `backups/`, or export zip files.
