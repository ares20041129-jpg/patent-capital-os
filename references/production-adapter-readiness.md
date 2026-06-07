# Production Adapter Readiness

Use this reference before a filing adapter is allowed to become a production execution option for AI self-filing or counsel-reviewed filing.

## Purpose

Production adapter readiness validates the adapter itself, not a specific patent case. It proves that an adapter has a reviewed release, credential-safe execution model, official-control boundary, dry-run evidence, audit logging, rollback controls, and duplicate-submission protection.

This gate does not submit, sign, pay, upload, log in, or touch an official system. It only validates readiness evidence supplied for the adapter.

## Strict Readiness Rule

Run:

```bash
python -X utf8 scripts/validate_production_adapter_readiness.py production-adapter-readiness-packet.json --json
```

The strict gate accepts only `evidence_mode=production_adapter_readiness`. It rejects benchmark, mock, placeholder, and production-shape-test evidence.

All readiness hash fields must use exact lowercase `sha256:<64 hex>` values. A descriptive value such as `sha256:adapter-dry-run-v1` is not readiness evidence.

An approved-adapter preflight must bind this packet by path and hash under `adapter.production_readiness`. A case cannot advance to `approved_for_adapter_execution` from shape-test readiness, missing readiness, or a readiness packet whose adapter name, version, registry hash, official system, or AI self-filing legal mode does not match the approved adapter.

## Required Evidence

- Adapter registry entry hash.
- Immutable release artifact hash.
- Source review hash.
- Passed security review, threat model, dependency scan, and sandbox dry-run hash.
- Account-owner authorization and filing-operations/compliance approvals.
- Credential policy proving no raw credentials, private keys, session tokens, cookies, MFA secrets, or captcha bypass are passed to the adapter.
- Official-control policy proving the adapter does not bypass access controls, MFA, captcha, or signature ceremony requirements.
- Execution controls for package-hash immutability, human-only handoff, receipt capture, audit logging, docket updates, and stop-on-bypass.
- Rollback and duplicate-submission protection.

## AI Self-Filing Requirement

For `legal_gate_mode=ai_self_filing_no_external_lawyer`, the readiness packet must preserve `external_lawyer_involved=false`. The adapter readiness gate never supplies legal authority by itself; the case still needs a validated AI self-filing legal/compliance gate and applicant authorization.

## Benchmark Shape Test

Use `--allow-production-shape-test` only inside benchmark validation. A production-shape packet proves the schema and validator behavior. It is not real adapter approval and must fail strict production readiness.

## Stop Conditions

Stop and do not allow approved-adapter execution when:

- credential material or bypass instructions appear anywhere;
- security review, threat model, dependency scan, or dry run is missing or failed;
- official controls are bypassed or human-only steps are not converted to handoff;
- duplicate-submission protection is absent;
- receipt capture, audit logging, or docket update is optional or missing;
- the packet is mock, benchmark, placeholder, or shape-test evidence.
