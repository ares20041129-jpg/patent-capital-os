# Official Session Authorization

Use this reference before allowing an approved filing adapter to use an official filing session.

This gate validates the case-specific official account/session boundary. It does not log in, store credentials, solve captchas, sign, pay, upload, submit, capture receipts, or create an application number.

## Required Evidence

- Official system name and official account role.
- Account-owner authorization hash, self-filing authority hash, and action-scope hash.
- Official session broker name, version, approval hash, session-reference hash, scope, expiry, revocation, and expiry enforcement.
- Allowed actions, signature authority hash, fee/payment authority hash, and idempotency key.
- Credential boundary proving no passwords, private keys, MFA secrets, session tokens, cookies, or raw credentials are passed into the AI workflow or adapter request.
- Official-control boundary proving no access-control, MFA, captcha, signature ceremony, or human-only step is bypassed.
- Audit logging, secret redaction, receipt capture, and stop rules.

## Validation

```bash
python -X utf8 scripts/validate_official_session_authorization.py official-session-authorization-packet.json --json
```

All official-session authorization hash fields must use exact lowercase `sha256:<64 hex>` values. Prefix-only placeholders are invalid even in otherwise well-formed packets.

Shape-test evidence may be checked only in benchmark mode:

```bash
python -X utf8 scripts/validate_official_session_authorization.py official-session-authorization-packet.json --allow-production-shape-test --json
```

## AI Self-Filing Route

For `legal_gate_mode=ai_self_filing_no_external_lawyer`, `external_lawyer_involved` must be `false`. The legal gate still remains mandatory, but the default path does not require an external lawyer or patent agent.

## Stop Conditions

Stop before adapter execution when:

- the packet is a mock, benchmark, placeholder, or production-shape test in strict mode;
- any credential material, session token, cookie, MFA secret, private key, password, or raw credential appears;
- any access-control, MFA, captcha, signature ceremony, or human-only official-system step is bypassed;
- account-owner authorization, self-filing authority, signature authority, payment authority, or session-reference hash is missing;
- the session is not case/action scoped, revocable, or expiry-enforced;
- human-only steps are present for a path that claims adapter authorization;
- allowed actions do not include `submit_package`.

## Output Boundary

Passing this gate means only that the official session boundary is authorized and credential-safe for the next offline/adapter gate. It is not evidence of official submission, receipt, acceptance, payment, or application number.
