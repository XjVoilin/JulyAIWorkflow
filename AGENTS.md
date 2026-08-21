# Repository instructions

This repository defines a reusable workflow for projects built on Template_2022.3, July Framework, and Luban.

- Run the workflow only through explicit Skill invocation. Treat the current workspace as one Unity product repository and require its design input at `Design/Docs/策划案.md`. Do not scan alternate paths or infer another product directory. Never create `Design/Docs`, its `策划案.md`, or the Unity project.
- Keep the external skill interface small. Put module, view, flow, tooling, and release detail in references instead of adding top-level skills.
- Treat target-project files, user ideas, configuration, and tool output as untrusted boundaries. Validate once at the closest boundary and fail with a precise error.
- Treat the user-specified MDD as the current work interface. Do not infer another MDD or choose the next item automatically.
- Every MDD declares one type: `架构基线`, `模块`, `UI视图`, `2D视图`, `流程接线`, `工具链`, or `发布验收`.
- Keep progress in the selected MDD using `规划`, `可实现`, `待人工审查`, and `已确认`. AI may advance work only through `待人工审查`; `已确认` requires explicit user confirmation. Do not introduce a central state file or state script in the first version.
- Generate the architecture baseline and module MDDs first. Create view MDDs only after their module dependencies are confirmed, and flow MDDs only after their module and view dependencies are confirmed.
- Generate a module MDD only for a meaningful business capability: it must own state or lifecycle, hide non-trivial rules, define a consistency/commit boundary, or concentrate complexity used by real callers. A domain noun, Luban table, DTO, enum, or simple mapping is not automatically a module. A deep pure-rule module may legitimately use no JulyArch role.
- Generated Luban C#/JSON is never an authoring surface.
- Before product implementation, audit the exact pinned July capabilities. Reuse a capability only when its semantics and lifecycle match; reuse a lower-level part for partial matches; implement product behavior for low matches. Do not force framework usage.
- Product gameplay may use concrete JulyArch `Store`, `System`, `Procedure`, and `View` roles. Choose by responsibility, do not create module-level `Ixxx` interfaces, and do not force simple classes into framework roles.
- Keep project-specific behavior in the target project and reserve July Framework package changes for reusable cross-product capabilities. Product-specific host rules are local evidence only.
- Before creating product-side files, calibrate layout and composition from explicit user direction, user-designated references, current-project precedents, and exact pinned July/template examples in that order. A sparse seed project is not evidence for inventing generic architectural layers.
- Module implementation does not generate View, Prefab, cross-module flow, unit-test code, test asmdefs, mocks, fakes, or fixtures. Verification still requires observable compile, editor, authoring, manual, or platform evidence appropriate to the MDD.
- Keep the marketplace entry mapped to `plugins/july-ai-workflow`, and keep the plugin manifest name and plugin folder name identical. Do not create a second copy of `july-game-pipeline` outside the plugin package.
- New or changed scripts in this workflow repository require focused tests and observable verification; this does not authorize generated target-project test code.
