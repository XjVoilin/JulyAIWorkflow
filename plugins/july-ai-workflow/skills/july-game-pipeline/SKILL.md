---
name: july-game-pipeline
description: 仅在用户显式调用后，将游戏策划案生成 GDD、将 GDD 生成全部 MDD，或严格实施一份指定 MDD。适用于使用 JulyFramework 与 Luban 的 Unity 项目；不生成图片、Prefab 或测试。
---

# July 游戏研发流程

只执行用户当前明确要求的一个动作：

1. 策划案生成、更新或重新生成 GDD；
2. GDD 生成或更新全部 MDD；
3. 按照用户 `@` 指定的一份 MDD 实施。

三个动作彼此独立。不要自动继续下一阶段，不选择下一份 MDD，不实施依赖 MDD，不创建工作流状态。

## 动作完成契约

- 写入产物不代表当前动作已经完成；必须执行对应 reference 规定的写后验证闭环。
- 写后验证必须重新读取磁盘上的实际产物，并对照本次输入、当前工程事实和已加载规则检查，不能只依赖生成过程中的记忆。
- 能在当前动作授权范围内修正的问题应立即修正并重新验证；遇到需要用户决定的关键歧义或超出当前动作的冲突时停止，不报告完成。
- 写后验证属于当前动作内部步骤，不创建独立审查动作、审查文档或工作流状态，也不要求用户另开任务复检。

## 路由

### 策划案到 GDD

读取 [references/gdd.md](references/gdd.md)，只执行其中的 GDD 流程。这个动作不检查 Unity、JulyFramework 或 Luban。

### GDD 到 MDD

读取：

- [references/mdd.md](references/mdd.md)
- [references/july-architecture.md](references/july-architecture.md)

检查当前项目实际安装的 JulyFramework、Luban 和已有代码。某份 MDD 涉及 View 时，再读取 [references/july-ui-components.md](references/july-ui-components.md)。

### 实施指定 MDD

读取：

- [references/implementation.md](references/implementation.md)
- [references/july-architecture.md](references/july-architecture.md)

只实施一份明确指定的 MDD。涉及 View 时，再读取 [references/july-ui-components.md](references/july-ui-components.md)。

## 文件选择

用户通过 `@文件` 指定时使用该文件。未指定时，只使用当前项目中名称明确且唯一的策划案或 GDD；找不到时报告未执行，存在多个候选时询问用户，不自行猜测。

未指定输出位置时，GDD 与策划案同目录，MDD 位于 GDD 同级的 `MDD` 目录。不要求固定的设计目录名称。

目标已存在时：

- “生成”不覆盖，停止并说明目标已存在；
- “更新”在现有文档上修改；
- “重新生成”仅适用于 GDD，并且只在用户明确授权时重写；
- MDD 第一版只支持生成全部或更新全部，不支持重新生成；
- 不自动删除旧设计文档。

## 共同边界

- 默认使用中文编写说明、GDD、MDD、索引和实施报告；代码标识符使用英文。
- 不读取其他产品项目，不把其他产品结构作为设计依据。
- 不建立项目画像，不要求目标项目提供额外说明 Markdown。
- 不自动安装 July 包；需要的能力不存在时报告。
- 不生成或修改图片、图片提示词、UI 美术规划、Prefab、Scene、Inspector 绑定、材质、动画、音频或其他美术资源。
- 不调用图片或 UI 美术插件。
- 不自动生成目标项目测试、Mock、Fake、Fixture 或测试 asmdef。
- 只修改当前动作授权的设计文档、C# 代码和 Luban 作者源；Luban 生成产物只能由项目已有生成流程产生。
- 关键输入缺失或存在会改变产品、角色、状态所有权、公开接口的歧义时，停止并询问；每次只问一个问题，并给出推荐答案。
- 不通过默认值、静默返回、假实现或未授权功能伪造成功。

只有对应写后验证通过后，当前动作才算完成。随后立即停止，简洁报告实际产物、未完成项和验证结果。
