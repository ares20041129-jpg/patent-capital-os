# Inbox Rejection Gate

This benchmark proves unsafe inbox-to-handoff inputs are blocked before patent material generation, handoff reliance, adapter execution, or any official action.

## Required Failures

- Path traversal must fail for `raw_input_dir`.
- Path traversal must fail for `reference_delta_source`.
- Missing raw input must fail.
- Empty inbox must fail.
- Existing output must fail before stale outputs are reused.

## Boundary

No official action is allowed. The rejection gate must not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.
