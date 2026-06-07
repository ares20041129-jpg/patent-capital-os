# Application Number Evidence

Use this reference after `official_receipt_received` when a workflow claims that an application number or acceptance status has been received.

## Purpose

Application-number evidence is the final filing-status gate in Patent Capital OS. It confirms that the official system has issued an application number or acceptance status and that the case can be docketed and added to the portfolio as a pending application.

## Required Evidence

- Official receipt ID, file, and hash.
- Application number from the official system.
- Filing date.
- Official status text, official status snapshot file, and exact status snapshot hash.
- Official file-list file and exact file-list hash.
- Official session authorization hash and official session-reference hash preserved from adapter execution, receipt capture, and receipt status.
- Final package hash, counsel-reviewed or AI-reviewed package hash, and submitted package hash.
- Fee/payment status and payment receipt hash when paid.
- Docket entry with next deadlines.
- Portfolio family ID, tags, and maintenance owner.
- When the receipt evidence carries `reference_patent_delta_hash`, the application-number evidence, filing status, and report must preserve the same application-materials hash, reference-patent delta hash, positive delta row and claim-element counts, and `reference_delta_boundary_preserved=true`.
- Reference-patent delta evidence remains boundary and claim-strategy evidence only. It is not applicant claim support, legal advice, filing authorization, official submission evidence, receipt evidence, or application-number evidence.

## Stop Conditions

Stop and do not mark `accepted_or_application_number_received` when:

- Application number is missing or only user-supplied without official evidence.
- Official receipt hash is missing.
- Official status snapshot file or hash is missing or mismatched.
- Official file-list file or hash is missing or mismatched.
- Official session authorization hash or official session-reference hash is missing or differs from receipt capture/status evidence.
- Reference-delta metadata is missing or mismatched after it appeared in receipt capture/status evidence.
- Submitted package hash differs from final or reviewed package hash.
- Fee status is invalid or a paid fee lacks payment receipt hash.
- Docket or portfolio update is missing.

## Validator

Run:

```bash
python -X utf8 scripts/validate_application_number_evidence.py application-number-evidence.json --json
```

Then run `scripts/validate_filing_status_transition.py` on the status file. Mock benchmark data must be explicitly marked as mock.

The validator requires exact lowercase `sha256:<64 hex>` values. When local receipt, official status snapshot, official file-list, or paid payment receipt file paths are present, it recomputes file hashes and rejects mismatches.

## Evidence Processor

When `official_receipt_received` evidence exists and an independently supplied official status/application-number source is available, use:

```bash
python -X utf8 scripts/prepare_application_number_acceptance.py official-receipt-dir application-number-source.json --output-dir application-number-dir --json
```

This script must not log in, scrape, upload, sign, pay, submit, or touch an official system. It only converts already-supplied evidence into:

- `application-number-evidence.json`
- `filing-status.json`
- `docket-entry.yaml`
- `portfolio-update.json`
- `application-number-report.md`
- `artifact-hashes.json`

For benchmark data, `benchmark_mock=true` is mandatory and the report must state that the application number and acceptance notice are not real.
