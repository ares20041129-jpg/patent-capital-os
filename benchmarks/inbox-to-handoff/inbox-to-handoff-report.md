# Inbox To Handoff Report

Inbox ID: INBOX-HANDOFF-001
Pipeline status: pass
Route: AI self-filing, no external lawyer or patent agent in default path
Official system touched: no
Official submission performed: no
Adapter execution performed: no
Automatic submission performed: no
External lawyer involved: no

## Summary

- Total: 2
- Passed: 2
- Blocked: 0

## Cases

| Case | Status | Decision | Reference delta | Output |
| --- | --- | --- | --- | --- |
| CASE-INBOX-HANDOFF-REF-001 | pass | handoff_ready_no_auto_submit | yes | D:\.agents\skills\patent-capital-os\benchmarks\inbox-to-handoff\processed-cases\001-CASE-INBOX-HANDOFF-REF-001 |
| CASE-INBOX-HANDOFF-001 | pass | handoff_ready_no_auto_submit | no | D:\.agents\skills\patent-capital-os\benchmarks\inbox-to-handoff\processed-cases\002-CASE-INBOX-HANDOFF-001 |

## Boundary

This inbox orchestration processes received raw material folders into local read-only handoff packages. It does not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.

## Generated Artifacts

- case-queue.json: sha256:3a0bfff486f14022df57c88c3d55468335599b65dae656c09a75c160daf8279d
- batch-processor-result.json: sha256:50c0bd7c4f40b52c6e93f9553f329d862f41336457e04c0df8891ad9025fb6e1
- processed-cases/001-CASE-INBOX-HANDOFF-REF-001/artifact-hashes.json: sha256:a609970a29e592f969060daaa1639e6e7fda5fbae1cf8a3096dc3fa0865c7306
- processed-cases/002-CASE-INBOX-HANDOFF-001/artifact-hashes.json: sha256:16a3b5ee9b554b160979a239d8b76b4f687d8dacf302a248a8454e61651bb2df
- inbox-to-handoff-result.json: sha256:533eaf42e5545429af2cd3e135f230477a302aa160c628444c2ae0c3b87759de
