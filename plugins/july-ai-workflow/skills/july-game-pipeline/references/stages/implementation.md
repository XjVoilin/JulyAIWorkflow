# Stage: Implementation

## Outcome

Implement the approved MDD in dependency-safe waves and collect observable evidence for every module.

## Work

1. Select the next pending module whose dependencies are complete. Work on one bounded module or one explicitly coordinated wave.
2. Read the complete module MDD, its producer interfaces, and relevant target-project code.
3. Implement only the specified behavior. Use the MDD-selected JulyArch `Store`, `System`, `Procedure`, and `View` roles where applicable, and use installed July modules at their verified interfaces. Do not build parallel lifecycle, events, persistence, resource, UI, or configuration mechanisms.
4. Apply [代码生成质量规则](../code-quality.md). Treat required collaborators and established internal invariants as non-null. Add a null check, default value, retry, fallback, or silent branch only for an evidenced boundary and its specified recovery behavior; otherwise fail fast so contract violations remain visible.
5. If implementation reveals that a required reusable capability or an existing July package contract is missing, stop before adding a product workaround. Apply [框架能力缺口 Gate](../framework-gap-gate.md), record the proposal, and block this Stage. Resume only after the package release and target-pin integration evidence satisfy the Gate.
6. Author Luban source inputs, run the project's generator, and verify outputs when the MDD requires configuration.
7. Verify through the module interface: focused tests, Unity compilation, and the module's acceptance evidence.
8. Update the MDD progress artifact with actual evidence and blockers.
9. Run the wave gate after every wave: interface alignment, dependency direction, compilation/tests, defensive-logic review, lifecycle/resource cleanup, and GDD coverage for that slice.

Do not mark the overall `implementation` Stage complete until every MDD module and wave gate is complete. If an MDD interface is wrong, stop and reopen `mdd`; do not quietly diverge in code.
