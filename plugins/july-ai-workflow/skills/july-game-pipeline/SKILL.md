---
name: july-game-pipeline
description: 仅在用户显式调用时，为当前 July/Luban Unity 项目完成当前版本的完整 GDD、模块与 View 设计，或严格按用户指定的单份 MDD 实施。
---

# July 游戏研发流程

本 Skill 只在用户显式引用 `$july-game-pipeline` 时运行。当前 Codex 工作区是唯一目标产品，不搜索或依赖其他项目。

## 定位项目

先读取 [项目约定](references/project-profile.md)，验证当前工作区、`Design/Docs/策划案.md`、Unity 工程标记及固定 July/Luban 依赖。缺少必需输入时报告精确路径并停止，不创建替代项目或策划案。

## 选择动作

只接受两种动作。用户未明确选择时说明这两种动作，不推断下一项工作。

### 完成当前版本的完整项目设计

1. 先只读取 [完整设计流程](references/design-workflow.md)，再读取策划案、已有 GDD/MDD、稳定宿主及当前固定版本 July/Luban 源码。重新生成时，旧业务代码不是设计证据。
2. 与用户讨论所有会改变范围、事实所有权、模块边界、玩家流程、View 清单、动作合同、配置 schema 或实施闭包的未决问题。讨论期间不写项目设计文件。
3. 用户确认全部结构性决定后，才读取 [结构化设计合同](references/design-contract.md)、[设计闭包门禁](references/design-closure-audit.md)、[索引模板](references/index-template.md)、[模块 MDD 模板](references/module-mdd-template.md) 和 [View MDD 模板](references/view-mdd-template.md)。涉及配置时再读取 [Luban 工作流](references/luban-workflow.md)。
4. 运行 `scripts/design_artifacts.py create-stage --workspace <当前工作区>`，只在返回的系统临时目录中工作。所有 staging 验证都必须同时传入同一 `--workspace`。
5. 先创建 `.july-design-contract.json`，再从同一合同生成 GDD 与索引；索引必须嵌入完全相同的 `july-design-contract` JSON。运行一次 `partial --surface staging` 验证。
6. 按全局实施顺序生成 MDD，每批最多两份；每份嵌入与索引完全一致的 `july-mdd-contract` JSON。每批后运行 `partial --surface staging` 验证。不要把批次当作用户操作，也不要在批次之间发布。
7. 全部 MDD 完成后运行 `full --surface staging` 验证。只有退出码为 0 才运行 `publish`；发布脚本会保留 `策划案.md` 和其他非 GDD/MDD 文档，并以整套设计替换旧 GDD/MDD。
8. 发布后再次对正式 `Design/Docs` 运行 `full --surface published` 验证，再清理本轮暂存目录。若生成中断、验证失败或发布失败，正式项目不得被部分更新，也不得报告设计完成。
9. 此动作不创建产品代码、Prefab、场景修改、Luban 工作簿或生成产物。

所有脚本命令、合同字段和清理边界以 [结构化设计合同](references/design-contract.md) 为准。不得绕过脚本直接把暂存文件逐个复制进项目。

### 实施用户指定的单份 MDD

1. 用户必须明确指定 `Design/Docs/MDD/Modules/` 或 `Design/Docs/MDD/Views/` 下的一份 MDD；不自行选择。
2. 在读取设计并修改产品前，先对正式 `Design/Docs` 运行 `scripts/design_artifacts.py validate --source <当前工作区>/Design/Docs --mode full --surface published`。失败表示整套设计无效；不得实施“还能做的部分”。
3. 读取策划案、GDD、索引、指定 MDD、[实施流程](references/implementation-workflow.md) 和 [代码质量规则](references/code-quality.md)。涉及配置时再读取 [Luban 工作流](references/luban-workflow.md)。
4. 核验指定 MDD 的前置产物已经实施，动作、符号提供者、文件白名单和当前稳定宿主与设计一致。
5. 若实现需要改变设计外的事实、角色、依赖、接口、文件、配置字段或 View 行为，停止实现，与用户讨论并先更新整套设计。
6. 只实施这一份 MDD，按风险执行验证，不自动继续其他 MDD。

## 强制产品设计原则

- GDD 只写产品事实，技术设计从索引开始；Module 与 View 必须覆盖同一当前版本。
- 每个业务事实只有一个权威来源；派生值不重复配置或存储。
- 模块按稳定业务能力划分，不能用 Editor 工具、验证、生成或发布职责伪装成业务模块。
- Store、System、Procedure、普通类型、Luban 生成类型与 View 按真实责任选择；不设置角色配额，不创建静态 Definition 包装或生成类型镜像。
- 每个原子玩家动作只有一个动作 ID、所有者、规范签名和导航所有者；每个跨 MDD 产品符号只有一个提供者。
- 全部 Module/View、Luban、注册和运行时合同进入同一无环实施图；每份 MDD 只依赖稳定宿主、自有或更早产物。Prefab 只在 View 正文保留资源名、预期路径、布局与人工接线要求，不进入结构化合同、实施图或文件白名单。
- 每份 MDD 必须包含精确产品文件白名单；实施不得越界。
- 单份 View MDD 实施不创建或修改 Prefab，不执行节点绑定、图片挂载或 Inspector 可视化验收；Prefab 未由人工交付时不打开窗口、不建立空界面或伪成功兜底。
- 不设计持久化，不生成目标项目测试代码，不维护流程状态，不自动实施下一份 MDD。
- 采用边界验证、内部信任、违约快速失败，不添加无真实故障依据的兜底。
