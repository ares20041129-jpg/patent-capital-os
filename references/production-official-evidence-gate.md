# Production Official Evidence Gate

Use this reference before treating any post-adapter submission, receipt, or application-number artifact as real official evidence.

## Purpose

This gate separates production official evidence from benchmark, generated, simulated, or shape-test evidence. It does not log in, upload, sign, pay, submit, scrape, or capture official evidence. It only validates an independently supplied evidence packet after an authorized official action has already happened.

## Strict Production Rule

Run:

```bash
python -X utf8 scripts/validate_production_official_evidence_gate.py production-official-evidence-packet.json --json
```

The strict gate accepts only `evidence_mode=production_official_evidence`. It rejects:

- `benchmark_mock=true`
- `production_shape_test=true`
- `not_real_official_evidence=true`
- strings or markers that identify mock, benchmark, placeholder, or shape-test evidence
- any raw credential, private key, session token, cookie, MFA secret, or captcha bypass
- package hash mismatch between final, reviewed, and submitted artifacts
- missing official status snapshot, file-list, receipt, application-number, docket, or portfolio evidence
- generated artifacts that claim the local generator touched the official system

## AI Self-Filing Requirement

For `legal_gate_mode=ai_self_filing_no_external_lawyer`, the packet must keep:

- `external_lawyer_involved=false`
- applicant self-filing authorization already validated
- no mandatory-agent condition
- no agency-bypass request
- no foreign/HMT applicant condition for this route

The legal step remains mandatory; it is the AI self-filing legal/compliance gate, not lawyer review.

## Evidence Required

The packet must bind these artifacts by path and sha256:

- `adapter-execution-result.json`
- `receipt-capture.yaml`
- `application-number-evidence.json`

The validator checks that:

- the adapter result passes `validate_adapter_execution_result.py`
- the adapter result is bound to the same production adapter readiness hash named in the evidence packet
- the adapter result is bound to the same official session authorization hash named in the evidence packet
- the adapter result is bound to the same official session reference hash named in the evidence packet source
- the receipt capture is bound to the same official session authorization hash and source session-reference hash
- the application-number evidence is bound to the same official session authorization hash and source session-reference hash
- the application-number evidence binds receipt, official status snapshot, and official file-list files to exact `sha256:<64 hex>` hashes
- adapter execution, receipt capture, and application-number evidence all preserve the same official session authorization and session-reference hashes
- when `reference_patent_delta_hash` is present, the packet, adapter execution, receipt capture, and application-number evidence all preserve the same `application_materials_hash`, `reference_patent_delta_hash`, positive reference-delta row and claim-element counts, and `reference_delta_boundary_preserved=true`
- receipt capture passes `validate_receipt_capture.py`
- application-number evidence passes `validate_application_number_evidence.py`
- case ID and official system match across artifacts
- receipt hash matches between receipt and application evidence
- final, reviewed, and submitted package hashes remain identical
- generator action fields remain false while official evidence claim fields may be true

## Benchmark Shape Test

Use `--allow-production-shape-test` only inside benchmark validation. A production-shape test proves the schema and validator behavior; it is explicitly not real official evidence and must fail the strict production gate.

## Stop Conditions

Stop and do not mark production evidence verified when:

- any artifact is mock, benchmark, shape-test, or placeholder evidence
- any official evidence hash is missing or mismatched
- any application-number receipt, status snapshot, or official file-list file is missing or hash-mismatched
- the adapter execution result is not bound to a production adapter readiness hash
- the adapter execution result is not bound to an official session authorization hash
- the adapter execution result is not bound to the source official session reference hash
- receipt capture or application-number evidence is not bound to the same official session authorization and session-reference hashes
- reference-delta metadata is present in any post-adapter artifact but missing, mismatched, non-positive, or not boundary-preserved in the packet or any other post-adapter artifact
- legal gate mode and external-lawyer fields conflict
- credential material or bypass instructions appear anywhere
- the official evidence does not independently prove submission, receipt, and application number in order
