# Validated Filing Package

Use this reference when a draft package and a real submission authorization packet should be checked before official-channel preflight.

## Purpose

Validated filing package generation bridges draft-only artifacts to `package_valid_official_preflight_pending`. It requires a separate `submission-authorization-packet.json`; the system must not invent attorney review, applicant authorization, agency authority, signature authority, fee authority, secrecy review, or final package hashes.

## Command

```bash
python -X utf8 scripts/prepare_validated_filing_package.py draft-package-dir submission-authorization-packet.json --output-dir draft-package-to-filing-validation --json
```

## Outputs

- `submission-authorization-packet.json`
- `filing-package-manifest.yaml`
- `filing-status.json`
- `package-validation-report.md`
- `artifact-hashes.json`

## Required Invariants

- Submission authorization packet passes `scripts/validate_submission_packet.py`.
- Filing package manifest passes `scripts/validate_filing_package_manifest.py`.
- `status=package_valid_official_preflight_pending`.
- `legal_gate=passed`.
- `package_validation=passed`.
- `official_channel_preflight=pending`.
- `decision=do_not_file_until_official_preflight`.
- `official_system_touched=false`.
- `official_submission_performed=false`.
- No receipt hash or application number may appear.

## Validator

Run:

```bash
python -X utf8 scripts/validate_validated_filing_package_benchmark.py benchmarks/draft-package-to-filing-validation --json
```

Passing this validator means package validation is complete and the next gate is official-channel preflight. It does not mean the case is submitted, receipted, accepted, paid, signed, or assigned an application number.
