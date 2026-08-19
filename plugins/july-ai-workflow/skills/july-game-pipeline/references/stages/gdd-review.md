# Stage: GDD Review

Use [../../assets/templates/GDD_REVIEW.md](../../assets/templates/GDD_REVIEW.md).

## Outcome

Decide whether the GDD is sufficiently consistent, complete, feasible, and testable to become technical input.

## Review dimensions

- `策划案.md` coverage and scope consistency.
- Core-loop completeness and state-transition consistency.
- Win/loss/exit/retry behavior.
- Interaction rules, ambiguity, and edge cases.
- Progression, generation, persistence, and data ownership.
- UI flow, localization, feedback, and accessibility expectations.
- Platform feasibility against the verified Project Profile.
- Configurability candidates appropriate for Luban.
- Acceptance scenarios that can distinguish correct from incorrect behavior.

Classify issues as blocker, major, or minor. Each issue names evidence, impact, and required correction. A review with any unresolved blocker does not pass and the Stage does not complete.

Fix GDD-owned problems in the GDD, increment its version, and rerun the review. Do not “resolve” a GDD ambiguity by deciding it later in MDD.
