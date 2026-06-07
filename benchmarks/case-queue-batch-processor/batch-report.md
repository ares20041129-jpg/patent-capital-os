# Case Queue Batch Processor Benchmark

Queue ID: QUEUE-BATCH-001  
Execution mode: dry_run  
Official system touched: no  
Official submission performed: no
External professional involved: no
Legal gate metadata: present

## Purpose

This benchmark proves that multiple AI self-filing patent cases can be processed as a queue without weakening per-case gates. The batch processor reports each case independently, preserves `legal_gate_mode`, keeps `external_lawyer_involved=false`, and does not submit, sign, pay, or claim receipt in dry-run mode.

`runner-result.json` captures the output shape produced by `scripts/run_case_queue.py` for the same queue.

## Per-Case Results

| Case | Input status | Output status | Legal gate mode | Outcome | Next action |
| --- | --- | --- | --- | --- | --- |
| INCOMING-DISCLOSURE-APP-001 | draft_only | draft_only | ai_self_filing_no_external_lawyer | deficiency | Obtain AI self-filing legal/compliance authorization and package validation |
| CASE-INTAKE-ORCH-001 | package_valid_official_preflight_pending | package_valid_official_preflight_pending | ai_self_filing_no_external_lawyer | passed | Run AI self-filing official-channel preflight |
| CASE-INTAKE-ORCH-001-legal_advice_claim_rejected | legal_gate_failed | legal_gate_failed | ai_self_filing_no_external_lawyer | deficiency | Cure legal/compliance deficiencies before filing |

## Boundary

Dry-run batch processing must not advance any case to `submitted_pending_receipt`, `official_receipt_received`, or `accepted_or_application_number_received`.
