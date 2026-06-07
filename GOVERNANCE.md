# Governance

Patent Capital OS is currently governed by a primary maintainer.

## Decision Model

The primary maintainer, [@ares20041129-jpg](https://github.com/ares20041129-jpg), has final decision authority for:

- roadmap priorities
- release timing
- maintainer appointments
- legal/compliance boundary changes
- security-sensitive changes
- benchmark contract changes

Community input is welcome through issues, discussions, and pull requests.

## Project Values

- truth over demo value
- evidence-bound workflow outputs
- explicit legal/compliance boundaries
- no fake official filing claims
- no fabricated adoption claims
- maintainable scripts and reproducible validation

## High-Risk Changes

The following changes require maintainer review before merge:

- changes to `scripts/validate_*`
- changes to `scripts/orchestrate_*`
- changes to official filing status transitions
- changes to AI self-filing legal/compliance gates
- changes to hash-binding rules
- changes to path-safety checks
- changes that affect `official_system_touched`, `official_submission_performed`, or `external_lawyer_involved`

## Release Policy

Releases should include:

- a short summary of user-visible changes
- verification commands and results
- known limitations
- migration notes if workflow contracts changed

## Adoption Claims

Public adoption should only be claimed when there is public evidence such as:

- an adopter entry in `ADOPTERS.md`
- a public issue or discussion from a user
- a public dependent repository
- a public citation or integration note
- GitHub stars, forks, or traffic data

Do not state that many people rely on the project until the evidence exists.
