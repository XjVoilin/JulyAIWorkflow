---
name: july-game-pipeline
description: 仅在用户显式调用本 Skill 时，从当前 July Unity 项目中对应项目名的 DesignDoc 策划案开始，依次推进 GDD、审查、MDD、实现与验收。项目目录、策划案或 July/Luban 环境不存在时，报告失败并停止。
---

# July 游戏研发流程

本 Skill 只有一个入口：用户显式引用 `$july-game-pipeline`，并表达制作、继续、推进或完善某个项目的意图。不要根据普通对话自动进入流程，也不要要求用户提供完整目录。

## 执行前提

从用户表达中取得项目名 `<项目名>`，并使用当前 Codex 工作区作为 Unity 项目根目录。执行前必须同时满足：

1. 用户的意图能够确定一个项目名；措辞不要求固定格式。无法确定时，只询问项目名。
2. 查看当前工作区 `DesignDoc/` 的直接子目录。优先使用与项目名完全一致的目录；没有完全一致项时，可以选择唯一且明显最接近的语义或文字匹配。没有合理候选或多个候选同样接近时，列出候选并询问用户。
3. 选中的项目目录中已有 `策划案.md`。不要扫描 `DesignDoc/` 之外的目录，也不要自动创建项目目录或策划案。
4. 当前工作区是已经创建好的 Unity 项目，使用 July Framework 和 Luban，并包含 `Assets/`、`Packages/manifest.json`、`ProjectSettings/ProjectVersion.txt` 与 `Tools/Luban/DataTables/`。

任一前提不满足时，明确告知用户“执行失败”及缺失项，然后停止。将匹配后的真实目录名传给 `flow.py --product`；不要把用户的近似说法直接作为目录名。不要创建 Unity 项目、项目目录或策划案作为补救。

## 开始流程

1. 读取 [产物约定](references/artifact-contract.md) 和 [July 项目约定](references/july-project-profile.md)。
2. 若 `DesignDoc/<项目名>/` 中存在 `.july-ai-workflow.json`，执行 `status`；否则执行 `init`。
3. 根据状态只处理用户指定的阶段；未指定阶段时处理“下一阶段”。
4. 开始阶段前执行 `start`，产物通过检查后执行 `complete`。
5. 每次状态变更都会自动刷新该项目目录中的 `工作流状态.md`。JSON 是机器状态源，Markdown 是给人查看的自动生成视图，两者都不要手工修改。

## 阶段

| 阶段 | 主要产物 | 执行前读取 |
|---|---|---|
| `gdd` | `GDD.md` | [GDD](references/stages/gdd.md) |
| `gdd_review` | `QA_GDD.md` | [GDD 审查](references/stages/gdd-review.md) |
| `mdd` | MDD 索引、模块、进度和资源清单 | [MDD](references/stages/mdd.md)、[Luban 流程](references/luban-workflow.md) |
| `implementation` | 代码、配置及验证证据 | [实现](references/stages/implementation.md) |
| `validation` | `QA/验收报告.md` | [验收](references/stages/validation.md) |

上游设计发生变化时，读取 [变更同步](references/stages/change-sync.md)，先修改事实所属文档，再用 `reopen` 重开最早受影响阶段。

## 状态命令

使用 Python 3 执行：

```text
python scripts/flow.py init --product <项目名>
python scripts/flow.py status --product <项目名>
python scripts/flow.py start --product <项目名> --stage <阶段>
python scripts/flow.py complete --product <项目名> --stage <阶段> --evidence <Unity项目相对路径> [--evidence <Unity项目相对路径> ...]
python scripts/flow.py reopen --product <项目名> --stage <阶段> --reason <原因>
python scripts/flow.py validate --product <项目名>
```

命令失败时修复错误原因，不要编辑状态文件绕过阶段门禁。

## 核心约束

- `策划案.md` 定义产品目标、范围、约束和待确认事项；GDD 定义玩家可观察行为；MDD 定义技术实现契约。
- GDD 不写代码、类名或文件路径；实现不得擅自增加 MDD 未定义的功能。
- 使用具体 July 接口前，先检查目标项目实际安装的包和现有组合方式。
- 游戏业务按实际责任选择 JulyArch 的 `Store`、`System`、`Procedure`、`View`；简单类不强套角色，符合角色语义的业务也不得刻意绕开框架。
- Luban 的源表和 schema 是输入；生成的 JSON/C# 是输出，不直接编辑。
- 阶段只有在产物真实存在且证据通过时才能完成。

按需复制 `assets/templates/` 中的模板，删除无关可选章节和模板说明；只有明确未决问题可以保留 `[待确认]`。
