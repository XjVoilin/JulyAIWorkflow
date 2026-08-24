---
name: july-game-pipeline
description: 仅在用户显式调用时，为当前 July/Luban Unity 项目完成当前版本的完整 GDD、模块与 View 设计，或严格按用户指定的单份 MDD 实施。
---

# July 游戏研发流程

本 Skill 只在用户显式引用 `$july-game-pipeline` 时运行。当前 Codex 工作区是唯一目标项目；不搜索或依赖其他产品。

## 定位项目

先读取 [项目约定](references/project-profile.md)，验证当前工作区、`Design/Docs/策划案.md`、Unity 工程标记及固定 July/Luban 依赖。缺少必需输入时报告精确路径并停止，不自动创建策划案或 Unity 工程。

## 选择动作

只接受以下两种动作。用户意图不明确时，说明这两个动作并请用户指定；不要推断下一项工作。

### 完成当前版本的完整项目设计

1. 读取 [完整设计流程](references/design-workflow.md)、[索引模板](references/index-template.md)、[模块 MDD 模板](references/module-mdd-template.md) 和 [View MDD 模板](references/view-mdd-template.md)。涉及配置时同时读取 [Luban 工作流](references/luban-workflow.md)。
2. 读取策划案、已有 GDD/MDD、当前稳定宿主和当前项目固定版本 July/Luban 源码。重新生成场景中，旧业务代码不作为设计依据。
3. 先与用户讨论所有会改变产品范围、事实所有权、模块边界、玩家流程、View 清单或技术合同的未决问题。只有用户明确推迟的非结构性内容可以保留未决。
4. 在足够确定后，一次完成当前版本全部设计：`GDD.md`、`MDD/索引.md`、全部 `MDD/Modules/*.md` 和全部 `MDD/Views/*.md`。
5. 此动作不创建产品代码、Prefab、场景修改、Luban 工作簿或生成产物。

### 实施用户指定的单份 MDD

1. 用户必须明确指定 `Design/Docs/MDD/Modules/` 或 `Design/Docs/MDD/Views/` 下的一份 MDD。未指定时列出这两个动作，不自行选择文件。
2. 读取策划案、GDD、索引、指定 MDD、[实施流程](references/implementation-workflow.md) 和 [代码质量规则](references/code-quality.md)。模块涉及 Luban 时再读取 [Luban 工作流](references/luban-workflow.md)。
3. 核验事实所有权、依赖、角色、接口、伪代码、配置合同、注册位置、文件白名单和验收路径都足以实施。
4. 若实现需要新增或改变设计外的事实、角色、依赖、接口、文件、配置字段或 View 行为，停止实现，与用户讨论并先更新设计文档。
5. 只实施该 MDD；完成后执行与风险相称的验证，不自动继续其他 MDD。

## 强制设计原则

- 完整设计先于任何产品实现，View 与模块在同一次完整设计中完成。
- GDD 只写产品事实；技术设计从索引开始。
- 每个业务事实只有一个权威来源；派生值不重复配置或存储。
- 模块按稳定产品能力划分，依赖图必须无环。
- Store、System、Procedure、普通类型、Luban 生成类型和 View 按真实责任选择，不设置角色配额。
- 新产品类型必须通过必要性审查；不要创建生成类型的镜像、别名、查询转发器或静态 Definition 包装。
- 玩家完整流程和跨模块调用写在发起能力的模块 MDD 中，不创建单独联通文档或全局协调层。
- 每份 MDD 必须包含精确产品文件白名单，实施不得越界。
- 不设计存档/读档时机与持久化架构，不生成目标项目测试代码。
- 采用边界验证、内部信任、违约快速失败；不添加无真实故障依据的兜底。
