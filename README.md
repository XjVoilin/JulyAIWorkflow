# July AI Workflow

面向 `Template_2022.3 + July Framework + Luban` 的可复用 AI 产品流水线。Unity 项目和策划案由使用者提前准备；插件被显式引用后，根据对话中的项目名，从当前工作区的 `DesignDoc/<项目名>/策划案.md` 开始推进研发流程。

## 当前能力

- 仅在显式引用 `$july-game-pipeline` 并指定设计目录后运行。
- 根据状态选择下一阶段，也允许显式执行某一合法阶段。
- 用固定产物契约生成 GDD、GDD 审查、MDD 和验收报告。
- 以证据推进阶段；缺少前置产物或验证结果时快速失败。
- 上游需求变化时重开受影响阶段，保留变更历史。
- 每次状态变更后自动刷新 `DesignDoc/<项目名>/工作流状态.md`。
- 将 July 项目职责、Luban 源文件/生成物规则和模板工程约束集中维护。

## 仓库结构

```text
.agents/plugins/marketplace.json                 # GitHub Marketplace 入口
plugins/july-ai-workflow/
├── .codex-plugin/plugin.json                    # 插件清单
└── skills/july-game-pipeline/
    ├── SKILL.md                                 # 唯一外部技能入口
    ├── references/                              # 按阶段渐进加载的规则
    ├── assets/templates/                        # 写入目标项目的产物模板
    └── scripts/                                 # 状态初始化、流转与验证
docs/                                            # 架构与决策说明
```

## 使用

### 从 GitHub Marketplace 安装

将本仓库作为 Marketplace 来源添加到 Codex：

```powershell
codex plugin marketplace add <GitHub用户或组织>/<仓库名>
```

也可以使用完整的 GitHub 仓库地址：

```powershell
codex plugin marketplace add https://github.com/<GitHub用户或组织>/<仓库名>.git
```

重新打开 Codex，在 Plugins Directory 中选择 `July AI Workflow` Marketplace，然后安装 `july-ai-workflow`。插件安装一次后，可在这台机器上的不同目标项目中使用，不需要把本仓库克隆进每个项目。

先创建好 Unity 项目，并准备 `DesignDoc/<项目名>/策划案.md`。打开目标项目后显式引用 Skill，例如：

```text
使用 $july-game-pipeline 继续 MyGame 的制作
```

措辞不要求固定格式。Codex 会优先匹配 `DesignDoc/` 下的同名目录，也可以选择唯一且明显最接近的目录；没有合理候选或多个候选同样接近时会询问用户。没有显式引用 Skill、最终目录不存在或缺少 `策划案.md` 时，流程不会执行。

更新 Marketplace 来源：

```powershell
codex plugin marketplace upgrade july-ai-workflow
```

刷新后，在 Plugins Directory 中更新或重新安装插件，并重新打开 Codex。

### 命令行入口

开发或诊断工作流时，也可以直接调用仓库中的确定性命令。

在已有 July 项目根目录初始化 `MyGame`：

```powershell
python plugins/july-ai-workflow/skills/july-game-pipeline/scripts/flow.py init `
  --product MyGame
```

`--project-root` 默认是当前目录。技能会读取 `DesignDoc/MyGame/.july-ai-workflow.json`，并自动生成同目录的 `工作流状态.md`。JSON 负责机器状态，Markdown 用于人工查看。

插件不创建 Unity 项目或策划案，不自动发布远程仓库，也不修改 `Template_2022.3` 或 `JulyFramework`。

## 设计依据

- [架构](docs/architecture.md)
- [状态真相源决策](docs/adr/0001-machine-readable-workflow-state.md)
