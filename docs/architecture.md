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
       └── 索引: facts, action contracts, symbol providers, full dependency graph, topological order
            ├── Modules MDDs: capability implementation contracts
            └── Views MDDs: presentation implementation contracts
```

The GDD contains product language only. Technical names begin in the index and are fully specified in the corresponding MDDs.

## Design derivation

For every complete player flow, the workflow identifies player-visible facts and actions first. It then determines each fact's single authority and every action's owning capability. Only after ownership is stable does it select JulyArch roles, configuration schemas, types, interfaces, and files.

New product types pass a necessity review. A type is justified only when it owns behavior, an invariant, runtime state, lifecycle, or a meaningful error contract. Static authored facts use Luban's generated types directly. Derived values remain calculations rather than duplicated authored or stored fields.

Each atomic player action receives one canonical action contract. Each cross-MDD product symbol receives one providing MDD. These contracts are shared by Module and View documents instead of being independently restated.

All Module and View MDDs form one implementation dependency graph containing compile, Luban authoring, registration, Prefab, and runtime-contract edges. The graph is topologically ordered before numbering. Every MDD must compile and complete its own acceptance using only the stable host, its own whitelist, and earlier MDD outputs. A cycle indicates incorrect ownership, action boundaries, navigation, or MDD boundaries and is fixed in design; events, interfaces, string routing, placeholders, or Common/Core containers are not used to conceal it.

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

The index records an exact topological implementation order, and Module/View items may interleave. It is not a batch command; each implementation request still names exactly one MDD.

## Design artifact compiler

Complete-design generation uses a compiler-like boundary:

```text
discussion (no writes)
  → workspace-bound staging directory in OS temp
  → ephemeral JSON contract
  → staged GDD + index
  → staged MDD batches (at most two)
  → partial validation after every batch
  → full validation
  → transactional publication of the complete Docs directory
  → full validation of the published design
```

The staging directory carries an ephemeral binding to the resolved workspace path, planning-document digest, and Unity project version. This is transaction provenance, not workflow status, and is never published. It prevents a valid stage from one product or an obsolete planning input from being published elsewhere.

The JSON contract is the mechanical authority for artifact identities, action contracts, product-symbol providers, dependency evidence, topological order, and exact file whitelists. The temporary standalone JSON is never published. Its complete value is embedded in `索引.md`; each MDD embeds its exact Artifact object. Human-readable tables and prose are generated from the same source and remain the design review surface. Validation also requires Markdown headings, substantive non-contract sections, and literal body references to contract IDs, signatures, product symbols, dependencies, and file paths, reducing drift between reviewable prose and machine data.

`scripts/design_artifacts.py` uses only the Python standard library. It validates both partial staging batches and complete sets. Publishing rejects links or directory junctions under the existing Docs tree, preserves `策划案.md` and unrelated Docs content, prepares a same-volume candidate directory, swaps the entire Docs directory, validates the result, and restores the old directory on an ordinary failure. Formal project files are never generated one at a time. A separate plugin-side `unittest` suite exercises the compiler boundary and rollback behavior; it does not authorize or generate target-product test code.

This makes structural completeness, graph ordering, uniqueness, and artifact-set consistency deterministic. Product semantics still require discussion and human review; the script cannot prove that a rule is fun or that a module boundary expresses the intended product.

## Deliberate exclusions

- Reusing a persistence provider for product Stores, save/load calls or timing, save failure, cross-launch recovery, server/local storage choice, migrations, repositories, and placeholders.
- Target-project test assemblies, unit or PlayMode tests, mocks, fakes, and fixtures.
- A project-wide Application/coordinator layer.
- Product-specific examples or external product paths in the plugin source.
- Treating old gameplay code as design evidence during regeneration.

## Implementation gate

Every implementation request first runs full artifact validation against formal `Design/Docs`. Every MDD provides an exact file whitelist and closure proof. Implementation then verifies its prerequisites, action contracts, symbol providers, current project host, and exact package APIs. It changes only whitelisted product files and declared generated/configuration/registration outputs. A missing or invalid complete design, forward reference, signature conflict, or required change to ownership, roles, interfaces, dependencies, files, schema, or View behavior is a complete-design defect and pauses implementation until the design is discussed and regenerated.

Validation is proportional to the artifact: Unity compilation and Console review, Luban full generation, registration checks, Prefab/Inspector inspection, representative WindowData/GM display, repeatable editor/manual flow, and target-platform checks when applicable.
