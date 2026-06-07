# Receipt Capture Mock Benchmark

Case ID: RECEIPT-CAPTURE-MOCK-001  
Status: official_receipt_received  
Date: 2026-06-01  
Benchmark mock: yes

## Purpose

This benchmark proves that the receipt-capture validator requires official receipt fields, file hashes, filing date, fee status, docket entry, and application number when a workflow claims `official_receipt_received`.

## Boundary

This is not a real CNIPA receipt, not a real filing, and not a real application number. The mock values exist only to test status and evidence validation.

## Evidence Required In Production

- Official receipt file and hash.
- Official file list hash.
- Filing timestamp.
- Fee/payment receipt when paid.
- Docket entry and next deadlines.
- Application number only if issued by the official system.
