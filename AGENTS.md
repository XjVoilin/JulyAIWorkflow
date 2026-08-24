# Repository instructions

This repository defines an explicit-invocation workflow for existing Unity products built with July Framework and Luban.

- Keep the external skill interface limited to two actions: complete the current-version product design, or implement one user-specified MDD.
- Treat the current Codex workspace as the only target product. Require `Design/Docs/策划案.md`; never search for another product, create a Unity project, or create the planning input.
- The design contract is `策划案.md → GDD.md → MDD/索引.md + all Modules and Views MDDs`. Finish and discuss the complete design before creating product code or Luban workbooks.
- Use only the user's requirements, product documents, the current stable host, and the exact pinned July/Luban sources as design evidence. Do not search outside the current product.
- In regeneration work, old gameplay code is not design evidence. Inspect only stable host composition, package pins, framework entrypoints, and authoring conventions that remain in scope.
- Define modules by stable product capability, not by technical layer or player-flow step. Define Views by player-visible screen or visual feature.
- Every business fact has one authoritative owner. Derived values are calculated from authoritative facts and are not duplicated in config, runtime state, or document contracts.
- Before adding a product type, prove that removing it would lose behavior, invariants, runtime ownership, lifecycle, or a meaningful error contract. Generated Luban types are used directly for static authored facts when their semantics match.
- Select JulyArch roles by responsibility. Store owns controlled runtime business state. System is a stable runtime capability managed or located through `ArchContext`. Procedure owns one bounded operation. Ordinary C# types own algorithms or value semantics. View owns presentation and Unity interaction.
- Module dependencies must be acyclic. Resolve cycles by correcting ownership and responsibility, not by adding events, interfaces, Common/Core containers, or coordination layers.
- Do not design persistence ownership, save/load timing, repositories, server entities, migrations, or placeholders. Persistence is intentionally deferred to the product owner.
- Do not generate target-project unit tests, PlayMode tests, test asmdefs, mocks, fakes, or fixtures. Validate with compilation, Unity Console, Luban full generation, Prefab/Inspector checks, repeatable editor/manual flows, and platform checks when relevant.
- Each MDD contains an exact product-file whitelist. Implementation may only create or modify those files plus generated Luban outputs and already-declared registration/configuration files.
- If implementation needs to change a role, fact owner, dependency, public interface, file, configuration schema, or View contract, stop and discuss the design change before editing product files.
- Implement exactly one MDD explicitly named by the user. Do not choose or continue to another MDD automatically.
- Preserve explicit-only invocation in `agents/openai.yaml`.
- Keep the marketplace entry mapped to `plugins/july-ai-workflow`, and keep the manifest name and plugin folder name identical.
- Do not modify an installed plugin cache as part of source maintenance unless the user separately requests installation or refresh.

Use boundary validation, internal trust, and fail-fast behavior. Add validation or recovery only for a concrete untrusted boundary or business-permitted failure, and validate each contract once at its owner.
