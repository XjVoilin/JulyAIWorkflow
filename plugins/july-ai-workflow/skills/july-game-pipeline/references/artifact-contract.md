# 产物约定

## Location and naming

当前 Unity 项目中的 `DesignDoc/<项目名>/` 是该项目所有设计产物和流程状态的根目录。项目名来自显式调用 Skill 的对话，目录必须在流程开始前存在并包含 `策划案.md`。

```text
DesignDoc/<项目名>/
├── 策划案.md
├── GDD.md
├── QA_GDD.md
├── 工作流状态.md
├── .july-ai-workflow.json
├── MDD/
│   ├── 索引.md
│   ├── 进度.md
│   ├── 资源清单.md
│   └── M<N>_<module>.md
├── ConfigDraft/
└── QA/
    └── 验收报告.md
```

Create only directories and artifacts required by the selected design. `ConfigDraft/` is used only when the MDD defines Luban source changes; `QA/` is created when implementation validation begins.

## Truth ownership

- `策划案.md` owns goals, audience, constraints, confirmed product choices, and open questions.
- GDD owns all player-facing behavior. It must not defer behavior to MDD.
- GDD review owns issue severity and the pass/block decision.
- MDD owns implementation structure, interfaces, dependencies, files, and technical acceptance.
- Luban source workbooks/schema own configurable values and data shape.
- Code and tests own actual behavior.
- `.july-ai-workflow.json` owns Stage state and transition history.
- `工作流状态.md` is generated from that JSON after every state mutation for human inspection; never edit it manually.

Do not maintain the same fact in two truth sources. Downstream artifacts may summarize an upstream fact only when they name its version and explain why the local copy is necessary.

## Metadata

Every plan, GDD, review, MDD index, and validation report begins with:

```text
> 版本：v1.0 | 日期：YYYY-MM-DD | 状态：draft/reviewed/approved
> 上游：<artifact and version, or none>
```

Increment a document version when its owned truth changes. Formatting-only edits do not require a version change.

## Unresolved information

Use `[待确认]` only for a concrete product decision and state its impact. A stage cannot complete when an unresolved item changes the core loop, win/loss rules, persistence ownership, online/offline model, monetization, or required platform capability. Non-blocking polish choices may remain if the downstream default is explicitly approved.

## Evidence

Evidence passed to `flow.py complete` must be:

- relative to the target project root;
- inside that project;
- already present on disk;
- sufficient to demonstrate the selected Stage outcome.

One placeholder file is not valid evidence for a multi-file MDD stage. Pass the index plus all module/progress/resource documents that define the implementation contract.
