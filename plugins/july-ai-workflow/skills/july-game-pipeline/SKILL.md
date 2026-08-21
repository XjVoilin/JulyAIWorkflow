---
name: july-game-pipeline
description: 仅在用户显式调用本 Skill 时，从当前 July/Luban Unity 项目的策划案生成 GDD、项目能力模块设计、View 设计，或按用户指定范围实现模块、View 与玩家功能联通。
---

# July 游戏研发流程

本 Skill 只在用户显式引用 `$july-game-pipeline` 时运行。它按“全部模块 → 全部 View → 玩家功能联通”推进，并在每份产物完成后等待人工确认。不要自动选择下一项，也不要把 AI 完成等同于用户确认。

## 定位项目

以当前 Codex 工作区作为唯一 Unity 项目根目录，并固定使用 `Design/Docs`：

1. 必须存在 `Design/Docs/策划案.md`。
2. 不扫描其他目录或工作区外路径寻找替代产品输入。
3. 用户指定 MDD 时，验证它位于当前工作区 `Design/Docs/MDD/` 或其子目录。
4. 缺少设计目录、策划案、工程标记或指定 MDD 时，报告精确路径并停止，不自动创建。

读取 [July 项目约定](references/july-project-profile.md) 校验当前工程。

## 选择动作

### 生成或更新 GDD 与模块设计

用户要求根据策划案生成或更新设计时：

1. 读取 [产物契约](references/artifact-contract.md)、[模块工作流](references/module-workflow.md) 和 [项目结构与框架能力校准](references/project-structure-calibration.md)。
2. 生成或更新 `Design/Docs/GDD.md`。GDD 只描述产品事实、玩家行为和完整项目流程，不写类名或技术目录。
3. 在划分模块前，实际检查用户指定参考项目、当前项目结构和固定版本 July 的代表性角色；整理参考路径、采用的模块粒度/角色形态和明确不照搬的内容。
4. 遍历 GDD 中全部主要流程，只用于发现项目能力并检查覆盖；结合前述工程证据确定模块边界，不在此时设计 View、事件图或模块串联。
5. 生成或更新 `Design/Docs/MDD/骨架.md`，记录项目能力清单、模块划分、能力覆盖、角色候选、校准证据和阶段门禁。
6. 为全部识别出的项目能力生成 `Design/Docs/MDD/Modules/M<N>_<模块>.md`。模块代表稳定、可独立命名和维护的项目能力，不要求统一拥有 Store、System 或复杂规则。
7. 首次设计不创建产品代码、View MDD、玩家功能联通 MDD、Prefab、配置表或测试代码。
8. 工具链或发布验收确属 GDD 范围时，可生成对应 MDD。

已有文档时保留仍成立的产品事实，但用当前项目能力划分替换旧的功能切片、技术分层或推测性模块。

### 生成 View 设计

仅在用户明确要求进入 View 阶段时：

1. 读取 [View 工作流](references/view-workflow.md)。
2. 确认 `MDD/Modules/` 下全部模块 MDD 都是 `已确认`，且每份 MDD 都记录了实际角色产物、必要的注册/配置改动和验证证据；仅确认设计文字不算完成模块阶段。
3. 根据 GDD、参考图、Prefab、场景和参考项目整理完整 View 清单，并更新 `骨架.md`。
4. 区分 `UI视图` 与 `2D视图`，为本次要求的范围生成 View MDD；不实现代码。

模块未全部确认时停止并列出未确认项，不提前生成 View。

### 生成玩家功能联通 MDD

仅在用户明确要求联通玩家功能时：

1. 读取 [玩家功能联通工作流](references/integration-workflow.md)。
2. 确认全部模块已经实现并确认，且 `骨架.md` 完整 View 清单中的所有 View 都已经实现并确认。
3. 以玩家本次要完成的行为为范围，确定发起该行为的项目能力和自然承载编排的 System、Procedure、Store 或普通类型。
4. 生成 `Design/Docs/MDD/Integrations/I<N>_<玩家功能>.md`，类型为 `玩家功能联通`，记录模块调用、ViewData 映射、刷新、导航和验证；不创建与该文档同名的运行时层或统一协调框架。

联通发现模块职责或角色缺失时，先退回对应模块 MDD 调整，不用适配层掩盖。

### 按指定 MDD 执行

仅在用户手动指定一份 MDD 时执行。先读取策划案、GDD、骨架、指定 MDD 和当前工程，再根据顶部 `类型` 路由：

- `架构基线`：只审查或更新文档。
- `模块`：读取 [模块工作流](references/module-workflow.md)。
- `UI视图` 或 `2D视图`：读取 [View 工作流](references/view-workflow.md)。
- `玩家功能联通`：读取 [玩家功能联通工作流](references/integration-workflow.md)。
- `工具链`：按范围读取 [Luban 工作流](references/luban-workflow.md)。
- `发布验收`：检查构建、平台和发布证据。

所有会修改产品文件的执行都遵循：

1. 检查 GDD 是否足以支持当前范围。
2. 读取 [项目结构校准](references/project-structure-calibration.md)，核对用户指定参考项目、当前工程和固定 July 包。
3. 涉及配置表时先读取 [Luban 工作流](references/luban-workflow.md)。
4. 满足产物契约后，将指定 MDD 更新为 `状态：可实现`。
5. 只修改指定 MDD 当前能够成立的范围；生成代码时读取 [代码质量规则](references/code-quality.md)。
6. 不生成目标项目单元测试、测试 asmdef、Mock、Fake 或 Fixture。
7. 记录实际差异、待后续实现或联通事项，以及与风险相称的验证证据。模块 MDD 只有在计划角色代码已存在、当前范围行为已实现且验证证据已写回后，才能进入 `待人工审查`。
8. 完成后更新为 `状态：待人工审查`，等待用户确认。

只有用户明确确认当前 MDD 后，才能改为 `状态：已确认`。验证失败时保留当前状态并继续修复当前范围，不报告伪造成功。

## 没有指定 MDD 时

已有设计而用户只说“继续制作”时，列出可执行文件、类型和状态，请用户选择；不要自动决定下一项。

## 工作流边界

- 不创建中央状态文件或自动续跑脚本。
- 不自动创建 Unity 项目、设计目录或策划案。
- 不把项目流程直接变成模块、状态图或统一运行时协调层。
- 不在模块阶段提前生成 View、表现数据或具体串联方式。
- 不为未指定的 MDD 实现代码。
- 不让 AI 代替用户确认。
