# July AI Workflow

面向已经创建的 July Framework + Luban Unity 项目，通过 Codex 插件把策划案转换为 GDD、架构基线和模块 MDD，再按“模块 → View → 流程接线”的顺序渐进实现。

第一版不维护中央状态，不自动决定下一项，也不把 AI 的完成结论当作用户确认。

## 使用前提

- 已创建 Unity 项目并使用 July Framework 与 Luban；
- 当前项目存在 `Design/Docs/策划案.md`；
- 用户在 Codex 中显式引用 `$july-game-pipeline`。

首次生成设计：

```text
$july-game-pipeline 根据策划案生成 GDD、架构基线和模块 MDD
```

手动选择模块实现：

```text
$july-game-pipeline 按 Design/Docs/MDD/Modules/M003_商品.md 实现
```

模块经人工确认后，再明确要求生成 UI/2D View MDD；View 经人工确认后，再生成相邻起点到终点的流程接线 MDD。插件不会创建 Unity 项目、设计目录或策划案。

## 目标项目产物

```text
Design/Docs/
├── 策划案.md
├── GDD.md
└── MDD/
    ├── 骨架.md
    ├── Modules/
    ├── Views/
    │   ├── UI/
    │   └── 2D/
    ├── Flows/
    ├── Tooling/
    └── Release/
```

目录按需创建。首次只创建骨架、模块和 GDD 明确需要的工具链/发布 MDD，不提前创建空 View 或流程文档。

每份 MDD 声明类型，并使用：

```text
规划 → 可实现 → 待人工审查 → 已确认
```

AI 最多推进到 `待人工审查`；`已确认` 只能由用户明确确认。

## 仓库结构

```text
.agents/plugins/marketplace.json
plugins/july-ai-workflow/
├── .codex-plugin/plugin.json
└── skills/july-game-pipeline/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
docs/architecture.md
```

详细设计见 [docs/architecture.md](docs/architecture.md)。

## 安装

将本 GitHub 仓库添加为 Codex Marketplace 来源，并安装 `july-ai-workflow`。更新仓库并重新安装插件后，新建 Codex 任务以加载最新 Skill。
