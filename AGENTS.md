# Repository instructions

This repository defines a reusable workflow for projects built on Template_2022.3, July Framework, and Luban.

- Run the workflow only through explicit Skill invocation. Infer the product name from the request and inspect the direct child directories of `DesignDoc/`. Prefer an exact match, but allow one clearly closest semantic or textual match. Ask when no candidate is plausible or multiple candidates are similarly plausible. Never create the directory, its `策划案.md`, or the Unity project.
- Keep the external skill interface small. Put stage-specific detail in references instead of adding more top-level skills without a demonstrated independent use case.
- Treat target-project files, user ideas, configuration, and tool output as untrusted boundaries. Validate once at the closest boundary and fail with a precise error.
- Treat the user-specified MDD as the current work interface. Do not infer another MDD or choose the next feature automatically.
- Keep workflow progress in the selected MDD using only `规划`, `可实现`, and `已完成`. Do not introduce a central state file or state script in the first version.
- Generated Luban C#/JSON is never an authoring surface.
- Product gameplay may use JulyArch `Store`, `System`, `Procedure`, and `View` roles. Choose by responsibility; do not force simple classes into roles or forbid fitting business code from using them. Keep project-specific behavior in the target project and reserve JulyFramework package changes for reusable cross-product capabilities.
- Product-specific host rules are local evidence only. Do not promote them to universal July rules.
- Keep the marketplace entry mapped to `plugins/july-ai-workflow`, and keep the plugin manifest name and plugin folder name identical. Do not create a second copy of `july-game-pipeline` outside the plugin package.
- New or changed scripts require focused tests and observable verification.
