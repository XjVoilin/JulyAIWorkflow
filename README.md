# July AI Workflow

面向已经创建的 July Framework + Luban Unity 项目，通过 Codex 插件先从整个项目的玩家流程中发现稳定项目能力，再按“全部模块 → 全部 View → 玩家功能联通”的顺序渐进设计和实现。

第一版不维护中央状态，不自动决定下一项，也不把 AI 的完成结论当作用户确认。

## 使用前提

- 已创建 Unity 项目并使用 July Framework 与 Luban；
- 当前项目存在 `Design/Docs/策划案.md`；
- 用户在 Codex 中显式引用 `$july-game-pipeline`。

首次生成设计（玩家流程此时只用于发现模块和检查覆盖，不生成 View 或流程架构）：

```text
$july-game-pipeline 根据策划案生成 GDD、架构基线和模块 MDD
```

手动选择模块实现：

```text
$july-game-pipeline 按 Design/Docs/MDD/Modules/M003_商品.md 实现
```

所有模块角色代码与验证证据经人工确认后，再明确要求生成和实现完整 UI/2D View 清单；清单中的所有 View 经人工确认后，按具体玩家功能逐项联通。联通逻辑放进发起该能力的 System、Procedure、Store 操作或普通类型，不要求额外建立全局协调/Application 层。插件不会创建 Unity 项目、设计目录或策划案。

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
    ├── Integrations/
    ├── Tooling/
    └── Release/
```

目录按需创建。模块按稳定、可独立命名和维护的项目能力划分，不按玩家流程切片，也不要求统一拥有状态、生命周期、深规则或某种 JulyArch 角色。一个模块可以只含 Store、只含 System、只含 Procedure、混合多个角色，或只含普通 C# 类型；角色由实际职责决定。首次不提前创建空 View 或玩家功能文档。

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
