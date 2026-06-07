# Production Architecture

Use this reference when turning Patent Capital OS from a drafting assistant into an authorized filing workflow.

## Core Boundary

Separate the drafting system from the filing system.

- Drafting system: intake, prior-art analysis, claim architecture, support mapping, red-team review, and AI self-filing authorization-ready drafts by default; reviewed-package drafts only for an explicit reviewed route.
- Legal approval system: selected legal gate mode, AI self-filing legal/compliance authorization or attorney/patent-agent review, applicant authorization, inventor confirmation, ownership confirmation, secrecy review, fee authorization, and immutable package hashes.
- Filing system: official-channel login, package upload, schema validation, signature, fee handling, receipt capture, and docket creation.

The filing system may run only when the legal approval system has passed and the exact package hash is authorized.

For production intake before official execution, use an inbox control plane: each received case folder is processed into a local pre-submission-to-handoff package, then the generated case outputs are validated by a dry-run queue. The inbox control plane may prepare handoff evidence and a final handoff index, but it must not execute an adapter, touch an official account, submit, pay, capture a receipt, or claim an application number.

The local skill loop is closed only after the inbox handoff index and skill completion audit validate. The closure means the skill can intake materials, generate application materials, preserve the AI legal/compliance gate, prepare read-only handoff evidence, and prove the official boundary locally. It does not mean a case has been filed.

## Team Model

| Role | Responsibility | Cannot approve |
| --- | --- | --- |
| Intake operator | Completeness check, deadlines, jurisdiction, source files | Legal sufficiency |
| Patent strategist | Portfolio value, claim scope direction, filing family plan | Inventorship or ownership |
| Prior-art analyst | Search plan, closest references, limitation matrix | Patentability guarantee |
| Claim architect | Independent/dependent claims, fallback ladder, support map | Legal authorization |
| Technical SME | Technical correctness, embodiment completeness, data support | Filing authority |
| AI legal/compliance gate | Self-filing eligibility, no mandatory-agent condition, authorization scope, abnormal filing risk, no legal-advice or lawyer-review claim | Technical facts not in evidence |
| Patent attorney / patent agent | Optional reviewed-route legal review, claim scope, filing approval | Fabricated or unsupported facts |
| Legal ops | Authorization evidence, assignment, self-filing or agency eligibility, signature, fee authority | Technical novelty |
| Filing operator | Official forms, XML/package, channel execution, receipts | Legal gate override |
| Docketing operator | Deadlines, fees, office actions, family tracking | Filing without receipt evidence |
| Red team | Novelty, obviousness, clarity, enablement, design-around attacks | Final filing approval |

## State Machine

1. Intake received.
2. Materials normalized.
3. Legal gate pending.
4. Drafting and prior-art work.
5. Claim support map complete.
6. Red-team complete.
7. Selected legal gate evidence pending.
8. AI self-filing legal/compliance authorization or reviewed-route approval tied to exact package hash.
9. Applicant authorized filing and fees.
10. Filing package generated.
11. Official-channel preflight complete.
12. Submitted pending receipt.
13. Official receipt captured.
14. Docket created.
15. Portfolio updated.

Any failed hard gate moves the case to blocked with a deficiency report.

## Hard Gates

- Selected legal gate is tied to the final package hash: AI self-filing legal/compliance authorization for the no-external-lawyer route, or counsel/patent-agent approval for an explicit reviewed route.
- Applicant authorization covers the exact filing action and fee action.
- Inventor list and order are confirmed.
- Ownership or assignment basis is documented.
- Secrecy and foreign-filing status is resolved.
- XML/forms/attachments pass validation.
- Official-channel credentials and signature authority are lawful and current.
- Human-only official-system steps are not bypassed.
- Receipt capture and docketing are required after submission.

## Audit Requirements

Each material action should record:

- Actor or automation identity.
- Timestamp.
- Input artifact hashes.
- Output artifact hashes.
- Approval basis.
- Stop/proceed decision.
- External system touched, if any.
- Receipt or error evidence.

## Production Principle

The system can be fast only after it is precise. If a case lacks authorization, the correct output is a deficiency report, not a draft submission.
