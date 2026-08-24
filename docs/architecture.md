# July AI Workflow architecture

## Purpose

The workflow prevents product code generation from outrunning product and technical design. It first establishes one reviewable, complete current-version design, then treats a single user-selected MDD as the only implementation authority.

## External interface

The skill exposes two actions only:

1. **Complete project design** — discuss structural decisions and create or update the GDD, index, every module MDD, and every View MDD for the declared current-version scope.
2. **Implement specified MDD** — implement exactly one user-named module or View MDD and validate the observable result.

There is no workflow phase metadata, automatic continuation, or MDD category outside Modules and Views.

## Design hierarchy

```text
策划案
  └── GDD: product facts and complete player experience
       └── 索引: fact ownership, modules, dependencies, Views, implementation waves
            ├── Modules MDDs: capability implementation contracts
            └── Views MDDs: presentation implementation contracts
```

The GDD contains product language only. Technical names begin in the index and are fully specified in the corresponding MDDs.

## Design derivation

For every complete player flow, the workflow identifies player-visible facts and actions first. It then determines each fact's single authority and every action's owning capability. Only after ownership is stable does it select JulyArch roles, configuration schemas, types, interfaces, and files.

New product types pass a necessity review. A type is justified only when it owns behavior, an invariant, runtime state, lifecycle, or a meaningful error contract. Static authored facts use Luban's generated types directly. Derived values remain calculations rather than duplicated authored or stored fields.

Modules form a directed acyclic dependency graph. A cycle indicates incorrect ownership or responsibility and is fixed in design; events, interfaces, or Common/Core containers are not used to conceal it.

## JulyArch role model

- **Store** owns controlled runtime business state and publishes empty change notifications after consistent mutation.
- **System** is a stable runtime capability managed or located through `ArchContext`; simplicity and current consumer count do not disqualify it.
- **Procedure** performs one bounded operation, especially multistep, asynchronous, cancellable, or commit-oriented work.
- **ordinary type** owns algorithms or value semantics that need no JulyArch lifecycle.
- **View** owns Unity presentation and interaction.

No role quota exists. A configuration-only module is valid when it owns stable authored business facts and needs no handwritten runtime wrapper.

## Window contract

Every Window has a WindowData object. The Window keeps the same Data instance for its open lifetime.

```text
Open Window
  → WindowData constructor reads required Store/System facts
  → Window renders from Data

Empty business event
  → Window calls a targeted Data refresh method
  → Data reads current Store/System facts
  → Window redraws only the affected region

Button
  → business command: call owning System public method
  → pure presentation navigation: call UISystem directly
```

WindowData is mutable to support GM/editor display checks. It implements only the query interfaces it actually needs. It has no `RefreshAll`; partial refresh methods are named by presentation responsibility. Business events carry no data. Windows do not assemble display facts from Store/System, mutate Stores, or run Procedures directly.

## Product artifact tree

```text
Design/Docs/
├── 策划案.md
├── GDD.md
└── MDD/
    ├── 索引.md
    ├── Modules/M001_<能力>.md
    └── Views/V001_<视觉功能>.md
```

The index recommends implementation waves, but a wave is not a batch command. Each implementation request names exactly one MDD.

## Deliberate exclusions

- Persistence provider, server/local storage choice, save/load timing, migrations, repositories, and placeholders.
- Target-project test assemblies, unit or PlayMode tests, mocks, fakes, and fixtures.
- A project-wide Application/coordinator layer.
- Product-specific examples or external product paths in the plugin source.
- Treating old gameplay code as design evidence during regeneration.

## Implementation gate

Every MDD provides an exact file whitelist. Implementation first verifies the current project host and exact package APIs. It then changes only whitelisted product files and declared generated/configuration/registration outputs. A required change to ownership, roles, interfaces, dependencies, files, schema, or View behavior pauses implementation until the design is discussed and updated.

Validation is proportional to the artifact: Unity compilation and Console review, Luban full generation, registration checks, Prefab/Inspector inspection, representative WindowData/GM display, repeatable editor/manual flow, and target-platform checks when applicable.
