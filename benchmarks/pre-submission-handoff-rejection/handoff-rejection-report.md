# Handoff Rejection Gate

This benchmark proves malformed pre-submission handoff packages are rejected before any adapter execution or official filing action.

- Lifecycle hash mismatch must fail.
- Official action flag mutation must fail.
- Missing evidence role must fail.
- Copied evidence tamper must fail.
- Reference-delta boundary mutation must fail.

The rejection cases are local validation only. They do not log in, upload, sign, pay, execute an adapter, submit, capture a receipt, or claim an application number.
