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
- Platform feasibility against the verified Project Profile. Inventory required platform/framework capabilities separately from installed packages. Project markers or a package name prove environment identity, not that a required contract exists. A successful-path method does not prove required failure semantics: explicitly hand off missing/corrupt data, cancellation, partial write, restore and initialization outcomes for MDD contract verification. When exact interface evidence belongs to MDD, mark it `risk: requires MDD framework audit` instead of claiming support.
- Configurability candidates appropriate for Luban.
- Acceptance scenarios that can distinguish correct from incorrect behavior.

Classify issues as blocker, major, or minor. Each issue names evidence, impact, and required correction. A review with any unresolved blocker does not pass and the Stage does not complete.

Fix GDD-owned problems in the GDD, increment its version, and rerun the review. Do not “resolve” a GDD ambiguity by deciding it later in MDD.

A GDD may pass with a clearly recorded technical risk when its player behavior is coherent and MDD is the correct owner of the contract decision. A suspected reusable July capability gap must be carried into the MDD framework adequacy audit; it cannot disappear behind a generic `July/平台可行性：pass` statement.
