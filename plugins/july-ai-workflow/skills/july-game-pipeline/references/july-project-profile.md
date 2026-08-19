# Standalone July Project Profile

Use this profile for products created from `Template_2022.3`. Verify the target project rather than relying on remembered package interfaces.

## Required markers

- Unity project directories: `Assets/`, `Packages/`, `ProjectSettings/`.
- `ProjectSettings/ProjectVersion.txt` identifies the Editor baseline. The inspected seed currently uses `2022.3.62f2`.
- `Packages/manifest.json` contains `com.july.arch` and `com.code-philosophy.luban` plus the product's selected dependency closure.
- `Tools/Luban/DataTables/` contains Luban authoring inputs.

If a marker is missing, stop and report that the target is not a valid standalone July project. Do not create guessed replacement infrastructure.

## Ownership

July Framework packages own reusable capability implementations and their package-level tests. The target project owns:

- package selection and immutable version pins;
- provider and platform adapter selection;
- launch composition and business registration;
- project configuration and Luban schemas/data;
- scenes, assets, gameplay, product tests, and build policy.

Target-project gameplay may and should use JulyArch roles when their semantics fit:

- `Store`: owns domain state and controlled state changes.
- `System`: owns a long-running capability with initialization and shutdown lifecycle.
- `Procedure`: coordinates one bounded operation or use-case flow.
- `View`: represents scene/UI presentation and interaction bound to Unity objects.

Do not force a simple class into a JulyArch role when it needs none of those semantics. Conversely, do not avoid JulyArch for stateful, lifecycle-managed, orchestrating, or scene-bound business responsibilities that match a role.

Keep project-specific behavior in the target project even when it uses JulyArch. Move code into `JulyFramework` only when it is a reusable capability with a stable cross-product contract and package-level tests. Do not duplicate an installed July capability inside product code.

## Selecting packages

Start from the seed manifest. Add optional July packages only when the GDD/MDD requires their capability. Git-based UPM consumption must list the selected package and its July dependency closure explicitly and pin immutable package tags. Never replace pins with an unqualified branch.

Inspect the actual package README, public types, and adjacent template usage before writing a concrete call in MDD. Names from another product's host layer are not evidence of a standalone template interface.

## Verification levels

- Product logic: focused EditMode tests where possible.
- Scene, lifecycle, UI, and platform composition: Unity compilation plus focused PlayMode/integration evidence.
- Package changes: package tests in JulyFramework and seed-template integration validation.
- Release: use the target project's July build pipeline and explicit platform/environment settings.
