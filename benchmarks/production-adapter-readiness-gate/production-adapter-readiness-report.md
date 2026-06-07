# Production Adapter Readiness Benchmark

This benchmark proves the strict adapter readiness gate before any approved adapter can be used for real filing.

## Expected Results

- The production-shape adapter packet passes only with the benchmark-only shape-test flag.
- The same shape test is not real adapter approval and must fail strict adapter readiness.
- Strict production packet passes only when it uses `evidence_mode=production_adapter_readiness` and contains no mock, benchmark, placeholder, shape-test, credential, or bypass markers.
- An unsafe adapter must fail when it includes credential material or bypasses official controls.
- AI self-filing preserves no external lawyer involvement.

## Boundary

This benchmark does not log in, upload, sign, pay, submit, capture a receipt, or create an application number.
