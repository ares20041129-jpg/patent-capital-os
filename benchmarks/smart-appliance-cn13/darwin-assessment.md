# Darwin Assessment - Smart Appliance CN13 Benchmark

Date: 2026-06-01

Scope: assess the current Patent Capital OS benchmark against the target of an audit-ready patent application workflow. This is not legal advice and does not authorize filing.

## Karpathy Preflight

- Assumptions: the benchmark is based on the cited patent publication records and summaries, not a complete counsel-reviewed invention disclosure packet.
- Smallest sufficient action: score the benchmark, identify production gaps, and preserve the current do-not-file decision.
- Evidence available: `report.md`, `submission-packet-status.json`, the Patent Capital OS skill files, and the validation script outputs.
- Missing facts: applicant identity, inventor confirmations, assignment chain, counsel approval, official CNIPA-ready XML/forms, fee authorization, and filing-channel credentials.
- AI-strong work: clustering prior art themes, drafting claim architecture, detecting missing authorization, and producing an audit trail.
- AI-brittle work: legal inventorship, patentability opinion, claim scope risk, prosecution strategy, and official filing interactions.
- Guardrail: no filing, fee payment, signature, or official-channel action may occur without an authorized legal packet.
- Success criterion: assessment file created, legal gate preserved, next mutations are concrete.
- Stop rule: stop before any external submission or payment action.
- Decision: proceed with assessment only.

## Score

Overall score: 82 / 100

| Area | Score | Rationale |
| --- | ---: | --- |
| Legal gate integrity | 19 / 20 | The benchmark correctly fails filing readiness and records `do_not_file`. |
| Claim architecture | 16 / 20 | The core invention is concrete and claims are structured, but support mapping is not yet complete. |
| Prior-art matrix | 14 / 20 | The 13 references are mapped by theme, but the work is still abstract-level instead of full-claim-level. |
| Filing readiness realism | 11 / 15 | Missing legal, authorization, XML/form, fee, and official-channel evidence is explicitly surfaced. |
| Automation readiness | 9 / 15 | A validation script exists, but schema coverage and artifact generation are not production-grade yet. |
| Auditability | 7 / 10 | The report and status JSON are traceable; source capture and hash evidence need expansion. |
| Red-team controls | 6 / 10 | Risks are identified, but no independent adversarial reviewer artifact exists yet. |

## Pass / Fail Decision

Pass as a draft benchmark and skill evaluation artifact.

Fail as an auto-filing workflow.

Reason: the system is correctly designed to block filing when the legal authorization packet is absent. That is the desired behavior for the current evidence state.

## Key Findings

1. The legal gate is working.
   The strongest feature is that the workflow refuses to convert a draft benchmark into a filing action. This matches the user's requirement that the legal step must not be removed.

2. The benchmark needs full-reference ingestion before it can support claim-level novelty analysis.
   Current prior-art work is useful for strategy, but production patent work needs claims, specification embodiments, drawings, prosecution status where available, and family data.

3. Claim support mapping is the next missing core artifact.
   Each claim element should trace to invention disclosure evidence, experimental data, diagrams, and prior-art differentiation. Without that map, drafting quality cannot be reliably audited.

4. Authorization needs machine-verifiable evidence.
   The workflow should require structured proof for applicant authorization, inventor confirmation, ownership or assignment chain, counsel review, secrecy review, official channel, and fee authorization.

5. The current automation is a gatekeeper, not yet an end-to-end production operator.
   It can validate packets and generate draft reports. It should not file until official-channel integration, credential handling, human authorization, and audit logging are implemented.

## Darwin Mutations To Apply Next

1. Add a claim-support-map template.
   Required fields: claim id, limitation text, disclosure source, prior-art delta, technical effect, fallback position, evidence hash, reviewer, and approval status.

2. Add a production authorization schema.
   Required fields: applicant, inventors, assignments, attorney or patent-agent reviewer, review timestamp, scope of authorization, secrecy review result, fee authorization, filing jurisdiction, and official filing channel.

3. Add a full-reference ingestion route.
   The route should capture publication metadata, abstract, claims, description, drawings, citations, legal status, family members, and source URLs.

4. Add an independent red-team artifact.
   The red team should attack novelty, obviousness, unity, enablement, clarity, inventorship, ownership, and submission-readiness.

5. Add official-channel separation.
   Filing automation should be isolated from drafting automation and require a signed, immutable authorization packet before it can run.

## Next Production Cut

Create these files next:

- `assets/templates/claim-support-map.md`
- `assets/templates/legal-authorization-packet.yaml`
- `references/production-architecture.md`
- `scripts/validate_benchmark_gate.py`

The benchmark should remain `do_not_file` until all legal and official-channel requirements are present.
