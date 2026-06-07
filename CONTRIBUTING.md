# Contributing

Thanks for working on Patent Capital OS.

## Contribution Standard

This repository is not a casual text-generation project. Changes must preserve:

- legal/compliance gate requirements
- exact hash-binding behavior
- no-official-action local defaults
- benchmark and regression validity

## Before You Change Anything

1. Read `SKILL.md`.
2. Read `references/karpathy-preflight.md`.
3. Read the specific reference file for the workflow you are touching.
4. Review `WORKLOG.md` for recent invariants and prior verification evidence.

## Non-Negotiable Boundaries

Do not merge changes that:

- remove or weaken the legal/compliance gate
- claim official submission without evidence
- set default official-action flags to true
- treat reference patents as applicant-owned claim support
- silently bypass file hash checks, path checks, or lifecycle validation

## Development Workflow

1. Make the smallest sufficient change.
2. Update or add benchmark evidence only when the contract truly changes.
3. Run the narrowest validator that proves the change.
4. Run the regression gate before calling the repository green.
5. Record the change and verification result in `WORKLOG.md`.

## Minimum Validation

For any meaningful change, run:

```bash
python -X utf8 scripts/run_regression_gate.py --output-dir out/regression-gate --json
python -X utf8 scripts/validate_artifact_hash_manifest.py out/regression-gate/artifact-hashes.json --json
```

For workflow-specific changes, also run the matching benchmark validator from `scripts/`.

## Pull Request Guidance

A good pull request should include:

- what changed
- why it changed
- what invariant was preserved
- what validators were run
- whether any benchmark artifact changed

## License

No repository-wide open-source license has been assigned yet. Do not add third-party material or redistribution assumptions without explicit approval.
