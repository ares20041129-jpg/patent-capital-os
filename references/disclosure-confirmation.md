# Disclosure Confirmation

Use this reference when an invention disclosure scaffold has received structured inventor, applicant, evidence, no-copying, secrecy, and AI legal/compliance draft-review confirmations.

## Purpose

Disclosure confirmation promotes `invention-disclosure-scaffold.json` to `invention-disclosure.json` for draft-only patent generation. This is a drafting gate, not a filing gate.

## Required Inputs

- `invention-disclosure-scaffold.json`
- `disclosure-confirmation-packet.json`

The confirmation packet must include:

- inventor names and contribution confirmation;
- applicant identity and ownership basis;
- actual R&D basis;
- technical effects with evidence references;
- no-copying and no-synonym-substitution confirmation;
- real technical contribution summary;
- secrecy or foreign-filing status;
- AI legal/compliance review limited to `draft_generation_only`;
- `controls.external_lawyer_involved=false`;
- no claim that an external lawyer, patent agent, attorney, or in-house counsel reviewed or approved this confirmation stage;
- exact lowercase `sha256:<64 hex>` values for the scaffold hash, reviewed scaffold hash, and source/evidence hashes;
- prohibited reference/prior-art hashes separated from applicant source hashes;
- controls proving `draft_generation_allowed=true` and `filing_allowed=false`.

## Command

```bash
python -X utf8 scripts/confirm_invention_disclosure.py invention-disclosure-scaffold.json disclosure-confirmation-packet.json --output-dir scaffold-confirmation-to-disclosure --json
```

## Outputs

- `invention-disclosure.json`
- `filing-status.json`
- `confirmation-report.md`
- `artifact-hashes.json`

## Required Invariants

- `invention-disclosure.json` must pass `scripts/validate_invention_disclosure.py`.
- `filing-status.json` must remain `status=draft_only`.
- `legal_gate` for filing must remain `failed`.
- `decision=do_not_file`.
- `draft_generation_allowed=true`.
- `filing_allowed=false`.
- `official_system_touched=false`.
- `official_submission_performed=false`.
- `external_lawyer_involved=false`.
- Final AI self-filing legal/compliance authorization, applicant filing authorization, agency/signature authority, fee authority, official-channel preflight, and package hash match remain required before any filing action.

## Validator

Run:

```bash
python -X utf8 scripts/validate_disclosure_confirmation_packet.py disclosure-confirmation-packet.json --json
python -X utf8 scripts/validate_scaffold_confirmation_benchmark.py benchmarks/scaffold-confirmation-to-disclosure --json
python -X utf8 scripts/validate_disclosure_confirmation_rejection_benchmark.py benchmarks/disclosure-confirmation-rejection --json
```

Passing these validators means the disclosure can enter draft-only generation. It does not mean the case can be filed, submitted, receipted, or docketed as an application.
