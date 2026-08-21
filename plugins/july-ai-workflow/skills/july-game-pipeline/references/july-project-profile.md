# Standalone July Project Profile

Use this profile for products created from `Template_2022.3`. Verify the target project rather than relying on remembered package interfaces.

## Required markers

- Unity project directories: `Assets/`, `Packages/`, `ProjectSettings/`.
- `ProjectSettings/ProjectVersion.txt` identifies the target's actual Editor baseline. Read it from the target; do not assume a fixed patch version from a seed inspected elsewhere.
- `Packages/manifest.json` contains `com.july.arch` and `com.code-philosophy.luban` plus the product's selected dependency closure.
- `Tools/Luban/DataTables/` contains Luban authoring inputs.

If a marker is missing, stop and report that the target is not a valid standalone July project. Do not create guessed replacement infrastructure.

## Ownership

July Framework packages own reusable capability implementations and their package-level tests. The target project owns:

- package selection and immutable version pins;
- provider and platform adapter selection;
- launch composition and business registration;
- project configuration and Luban schemas/data;
- scenes, assets, gameplay, product verification, and build policy.

Target-project gameplay may and should use JulyArch roles when their semantics fit:

- `Store`: owns domain state and controlled state changes.
- `System`: owns a long-running capability with initialization and shutdown lifecycle.
- `Procedure`: coordinates one bounded operation or use-case flow.
- `View`: represents scene/UI presentation and interaction bound to Unity objects.

Do not force a simple class into a JulyArch role when it needs none of those semantics. Conversely, do not avoid JulyArch for stateful, lifecycle-managed, orchestrating, or scene-bound business responsibilities that match a role.

Keep project-specific behavior in the target project even when it uses JulyArch. Move code into `JulyFramework` only when it is a reusable capability with a stable cross-product contract and package-level tests. Do not duplicate an installed July capability inside product code.

## Default product source layout

For an unmodified `Template_2022.3` host that already declares `Assets/Game/Scripts/Runtime/` as its product runtime root, keep product code directly under that root:

```text
Assets/Game/Scripts/Runtime/
├── Modules/<业务模块>/
└── Views/
```

Do not add a project-name directory, product-name umbrella, `Application`, `Domain`, or `Models` layer beneath `Runtime`. Do not add a broad `Content` module. A different layout is allowed only when higher-priority project evidence establishes it; record that evidence in the selected MDD.

This host default does not authorize speculative files. Module implementation creates only its selected module subtree. View directories are created later by the View stage.

## Framework capability gap

Before adding a product-side substitute, inspect the exact pin and decide ownership from the real consumer and stable contract. A remembered API or another product's helper does not prove a gap. If a reusable July responsibility appears absent or ownership is ambiguous, report the missing capability and stop the current work item. The first version does not maintain a separate framework-gap state machine.

## Selecting packages

Start from the seed manifest. Add optional July packages only when the GDD/MDD requires their capability. Git-based UPM consumption must list the selected package and its July dependency closure explicitly and pin immutable package tags. Never replace pins with an unqualified branch.

Inspect the actual package README, public types, and adjacent template usage before writing a concrete call in MDD. Names from another product's host layer are not evidence of a standalone template interface.

## Verification levels

The current workflow version does not generate target-project unit tests, PlayMode tests, test asmdefs, mocks, fakes, or fixtures.

- Product modules: Unity compilation, Console review, configuration generation, existing debug/editor entrypoints, and repeatable manual evidence.
- Scene, lifecycle, UI, and platform composition: Unity compilation, Prefab/Inspector validation, editor paths, and target-platform evidence.
- Package changes: only after separate user authorization; follow the package repository's own test requirements.
- Release: use the target project's July build pipeline and explicit platform/environment settings.
