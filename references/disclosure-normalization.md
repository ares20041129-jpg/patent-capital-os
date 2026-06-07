# Disclosure Normalization

Use this reference after raw materials have been packaged and before any AI self-filing authorization-ready draft generation.

## Purpose

Disclosure normalization converts a standard case package into a structured invention disclosure scaffold. The scaffold is a working intake artifact only. It is not an inventor-confirmed disclosure, not an AI self-filing authorization-ready draft input, and not filing-readiness evidence.

## Required Inputs

- `case-package-manifest.json` from a validated case package.
- Copied source material files and hashes.
- `01-normalized/source-material-manifest.json` when available.

## Required Outputs

- `invention-disclosure-scaffold.json`
- `normalization-report.md`
- `artifact-hashes.json`

Run:

```bash
python -X utf8 scripts/normalize_invention_disclosure.py case-package --output-dir disclosure-normalization-scaffold --json
python -X utf8 scripts/validate_invention_disclosure_scaffold.py disclosure-normalization-scaffold/invention-disclosure-scaffold.json --json
python -X utf8 scripts/validate_disclosure_normalization_benchmark.py benchmarks/disclosure-normalization-scaffold --json
```

## Non-Negotiable Boundaries

- Keep `disclosure_status=scaffold_pending_confirmation`.
- Keep `legal_gate_mode=ai_self_filing_no_external_lawyer`.
- Keep `external_lawyer_involved=false`.
- Keep `inventor_confirmation_pending=true`.
- Keep `legal_gate_pending=true`.
- Keep `no_copying_confirmation_pending=true`.
- Keep `filing_allowed=false`.
- Keep `draft_generation_allowed=false`.
- Do not infer inventors, ownership, applicant authority, AI legal/compliance confirmation, no-copying confirmation, secrecy status, or technical effects beyond source evidence.
- Do not default to attorney, lawyer, counsel, patent-agent, or patent agent review wording in the scaffold or normalization report.

## Advancement Rule

Only advance from scaffold to confirmed invention disclosure after inventor contribution, applicant/ownership basis, no-copying confirmation, technical-effect evidence, and AI legal/compliance draft confirmation are explicitly supplied and validated. After confirmation, use `scripts/validate_invention_disclosure.py` before generating any AI self-filing authorization-ready patent draft.
