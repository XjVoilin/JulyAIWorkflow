# Stage: MDD

Use [../../assets/templates/MDD_INDEX.md](../../assets/templates/MDD_INDEX.md), [../../assets/templates/MDD_MODULE.md](../../assets/templates/MDD_MODULE.md), [../../assets/templates/PROGRESS.md](../../assets/templates/PROGRESS.md), and [../../assets/templates/RESOURCE_MANIFEST.md](../../assets/templates/RESOURCE_MANIFEST.md).

## Outcome

Translate an approved GDD into a technical contract that can be implemented in dependency-safe vertical waves.

## Work

1. Inspect the target project's installed July packages, composition root, Luban generator, current directory conventions, and similar code.
2. Identify cohesive modules from product behavior and real change axes. For each responsibility, decide whether it is a JulyArch `Store`, `System`, `Procedure`, `View`, or an ordinary class based on state ownership, lifecycle, orchestration, and scene binding. Do not force a role onto simple classes, and do not avoid a fitting role for substantial game business.
3. Give every module one interface: responsibility, inputs, outputs, invariants, error modes, dependencies, files, and acceptance evidence.
4. Keep interfaces smaller than implementations. Avoid one interface per class and avoid adapters without a second real implementation or test stand-in.
5. Define dependency order and arrange tracer-bullet waves. Each early wave should produce an observable slice rather than only horizontal infrastructure.
6. Define Luban source tables and generation evidence where configuration is required. Read [../luban-workflow.md](../luban-workflow.md).
7. Produce `索引.md`, each module document, `进度.md`, and `资源清单.md`.
8. Review interface producer/consumer alignment, dependency direction, ownership, and testability before completing the Stage.

MDD documents must be self-contained for implementation. They may cite the GDD version but must not replace behavior with “see GDD section X.”
