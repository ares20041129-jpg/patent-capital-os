# Karpathy Preflight

Use this reference before every material action in Patent Capital OS. This adapts Karpathy-style engineering discipline to patent filing operations.

## Purpose

Prevent common agent failures:

- acting on hidden assumptions;
- overbuilding instead of doing the smallest useful action;
- treating AI confidence as evidence;
- confusing draft, preview, upload, filing, receipt, and acceptance;
- skipping legal or fee authority checks;
- making broad edits or broad filings without a verifiable success condition.

## Required Preflight Card

Produce this before action:

```markdown
## Karpathy Preflight

- Action:
- Smallest sufficient step:
- Assumptions:
- Evidence available:
- Missing/uncertain facts:
- AI-strong parts:
- AI-brittle parts:
- Human/legal/official guardrail:
- Success criterion:
- Stop rule:
- Proceed / Stop:
```

## Rules

1. Think before acting.
   - If multiple interpretations exist, name them.
   - If the action depends on a missing fact, stop.

2. Simplicity first.
   - Do only the smallest step needed.
   - Do not add extra workflow, templates, filing actions, or code just because they seem useful.

3. Surgical changes.
   - Touch only files and fields needed for the current action.
   - Do not refactor unrelated skill content, templates, scripts, or metadata.

4. Goal-driven execution.
   - Define proof of success before acting.
   - Verification can be a validation result, official receipt, created file, docket entry, or documented stop decision.

5. Jagged-intelligence handling.
   - AI is strong at structuring, comparison, drafting, and checklist generation.
   - AI is brittle at legal authorization, self-filing eligibility, official filing status, identity, signatures, payment authority, edge-case XML conversion, and hidden prior art.
   - Put brittle points behind AI self-filing legal/compliance gates or explicit reviewed-route gates, official validation, and audit evidence.

6. Iron Man suit rule.
   - The system augments authorized applicants and filing operators, plus legal professionals only when that route is explicitly used.
   - Do not remove human/legal authority from actions that require it.

7. March of nines rule.
   - Demo readiness is not filing readiness.
   - For filing and payment, require version hashes, validation logs, authority evidence, official-channel path, receipt capture, and rollback/escalation plan.

## Fee And Payment Preflight

Before any fee or payment action, verify:

- fee amount and fee type;
- payer;
- fee reduction status;
- payment account;
- automatic payment authorization;
- deadline;
- receipt capture path.

If any item is missing, do not pay.

## Filing Preflight

Before any filing action, verify:

- selected legal gate mode tied to final package hash: validated AI self-filing legal/compliance authorization for the no-external-lawyer route, or counsel/patent-agent review for an explicit reviewed-package route;
- self-filing eligibility and no mandatory-agent condition when the AI self-filing route is used;
- applicant authorization includes filing/submission;
- inventor and ownership confirmations;
- secrecy review status if relevant;
- official filing channel;
- signature authority;
- XML/package validation;
- receipt capture path.

If official system demands a human-only step, stop at ready-to-submit handoff.

## Script Or File-Edit Preflight

Before script execution or file edit, verify:

- target file/path;
- expected change;
- backup or version-control state;
- command success criteria;
- non-destructive behavior.

Never use destructive git or filesystem operations as a shortcut.

## Stop Conditions

Stop when:

- the action is broader than necessary;
- required legal, payment, or official-channel evidence is absent;
- success cannot be verified;
- package hash differs from the reviewed or AI-authorized legal-gate hash;
- the user asks to bypass official controls;
- the action would fabricate or hide a legal or technical fact.
