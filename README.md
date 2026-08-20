# July AI Workflow

面向已经创建的 July Framework + Luban Unity项目，通过 Codex插件把策划案转换为 GDD和功能 MDD，再按用户手动指定的 MDD实现游戏功能。

第一版只有两个动作：

```text
生成设计：策划案 -> GDD -> 骨架MDD和各功能规划MDD
实现功能：指定MDD -> 校准为可实现 -> 编码 -> 验证 -> 记录完成
```

第一版不维护中央状态，也不会自动决定下一个功能。

## 使用前提

- 已创建 Unity项目并使用 July Framework与 Luban。
- 当前项目存在 `Design/Docs/策划案.md`。
- 用户在 Codex中显式引用 `$july-game-pipeline`。

首次生成设计：

```text
$july-game-pipeline 根据策划案生成 GDD和全部功能MDD
```

手动选择骨架或功能实现：

```text
$july-game-pipeline 按 Design/Docs/MDD/骨架.md 实现
$july-game-pipeline 按 Design/Docs/MDD/F003_商品出售.md 实现
```

插件不会创建 Unity项目、设计目录或策划案。项目、输入或指定 MDD无法定位时会报告失败并停止。

## 目标项目产物

```text
Design/Docs/
├── 策划案.md
├── GDD.md
└── MDD/
    ├── 骨架.md
    ├── F001_<功能>.md
    └── ...
```

每份 MDD使用 `规划`、`可实现`、`已完成`三个状态，并在同一文件中记录技术方案、实际修改和验证结果。

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

详细设计见 [docs/architecture.md](docs/architecture.md)。当前结构刻意保持精简，不包含状态脚本和产物模板。

## 安装

将本 GitHub仓库添加为 Codex Marketplace来源，并在插件目录安装 `july-ai-workflow`。安装或更新后新建 Codex任务，确保加载最新 Skill。
