# Authorized CN Ready-For-Filing Benchmark

Case ID: AUTHORIZED-CN-READY-001  
Status: ready_for_authorized_filing  
Official submission performed: no  
Date: 2026-06-01

## Purpose

This benchmark proves the positive path up to the handoff boundary: a packet with counsel review, applicant authorization, inventor confirmation, ownership evidence, secrecy status, final XML hash, fee authorization, official channel authority, and receipt-capture plan can become `ready_for_authorized_filing`.

It does not prove official filing. No official system action, payment, signature, receipt, or application number exists.

## Gates

| Gate | Result | Evidence |
| --- | --- | --- |
| Counsel/patent-agent review | pass | `submission-packet.json` reviewer and reviewed hash |
| Applicant authorization | pass | allowed actions include submit, file, and pay official fees |
| Inventor confirmation | pass | contribution_confirmed true |
| Ownership | pass | assignment evidence reference |
| Secrecy review | pass | CN completed, no foreign/PCT planned, not_required |
| XML/package | pass | final_xml hash present and preflight says validation passed |
| Fee authority | pass | auto_pay_authorized true |
| Official channel | pass | CNIPA system, account owner, signature authority, automation_allowed |
| Receipt capture | pass | destination and owner present |

## Boundary

The correct next state after this benchmark is still not `submitted_pending_receipt`. It remains `ready_for_authorized_filing` until a lawful official-channel filing action occurs and the system captures official status evidence.
