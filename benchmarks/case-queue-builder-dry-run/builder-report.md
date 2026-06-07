# Case Queue Builder Benchmark

Queue ID: BUILDER-QUEUE-001  
Builder mode: dry_run  
Official system touched: no  
Official submission allowed: no
External professional involved: no
Legal gate metadata: present

## Purpose

This benchmark proves that received AI self-filing case folders can be converted into a structured case queue before any filing action. The builder reads existing case records or filing status files, infers each case status, preserves `legal_gate_mode`, records `external_lawyer_involved=false`, selects local validators, and writes `generated-case-queue.json`.

## Generated Queue

| Case | Source record | Current status | Legal gate mode | Expected outcome | Validator |
| --- | --- | --- | --- | --- | --- |
| INCOMING-DISCLOSURE-APP-001 | filing-status.json | draft_only | ai_self_filing_no_external_lawyer | deficiency | validate_incoming_application_benchmark |
| CASE-INTAKE-ORCH-001 | filing-package-manifest.yaml | package_valid_official_preflight_pending | ai_self_filing_no_external_lawyer | ai_self_filing_package_validation | validate_ai_self_filing_package_benchmark |
| CASE-INTAKE-ORCH-001-legal_advice_claim_rejected | filing-status.json | legal_gate_failed | ai_self_filing_no_external_lawyer | deficiency | validate_ai_self_filing_deficiency_report_benchmark |

## Boundary

The builder only creates a queue. It does not validate official credentials, submit, sign, pay, claim filing receipt, or advance any case status.
