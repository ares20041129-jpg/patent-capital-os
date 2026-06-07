# Lifecycle Rejection Gate Benchmark

This benchmark proves that Patent Capital OS rejects forged or inconsistent lifecycle traces.

## Expected Rejections

- Session-reference mismatch must fail.
- Artifact hash mismatch must fail.
- Receipt-before-submission must fail.
- Submitted package hash mismatch must fail.

## Boundary

The benchmark mutates an already validated lifecycle trace in memory. It does not log in, upload, sign, pay, submit, capture a real receipt, or create a real application number.
