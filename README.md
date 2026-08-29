# July AI Workflow

面向 JulyFramework、JulyArch 与 Luban 模板项目的 Codex 插件。插件只在显式调用 `$july-game-pipeline` 后运行。默认根据用户 `@` 的一份文档识别当前阶段，并执行唯一下一步：

1. 按照策划案生成 GDD；
2. 按照 GDD 生成模块设计；
3. 按照模块设计生成全部 MDD；
4. 按照用户指定的一份 MDD 实施代码与配置。

插件不维护流程状态，一次调用只推进一个阶段，不会完成当前动作后继续下一步。

## 安装

在 Codex 中把本仓库添加为个人 Marketplace，然后安装 `July AI Workflow`。更新仓库中的插件版本后，需要在 Codex 中重新安装或更新插件，并新建任务使新版本生效。

仓库地址：<https://github.com/XjVoilin/JulyAIWorkflow>

## 使用

在已经由 July 模板创建好的 Unity 项目中开启 Codex 任务，默认使用统一口令：

```text
$july-game-pipeline @一份文档 执行
```

插件使用明确的文档类型标识、规范结构、文件名和标题识别阶段，不把任意 Markdown 猜成策划案。无法唯一识别、同时指定多份文件或文档标识与结构冲突时会停止并要求澄清。

### 策划案生成 GDD

```text
$july-game-pipeline @DesignDoc/策划案.md 执行
```

GDD 只描述游戏产品设计，不写 JulyArch、类、接口、文件路径或 Luban 技术方案。遇到会实质影响产品设计的歧义时，插件一次只询问一个问题，并给出推荐项。

### GDD 生成模块设计

```text
$july-game-pipeline @DesignDoc/GDD.md 执行
```

插件从完整 GDD 提取业务决策，结合当前工程建立候选模块图并执行全局归一化，生成与 GDD 同目录的 `模块设计.md`。模块设计记录业务决策归属、模块职责、权威状态、稳定语义接口、事务编排、依赖方向和 JulyArch 角色规划，供用户在进入 MDD 前独立审查。

### 模块设计生成全部 MDD

```text
$july-game-pipeline @DesignDoc/模块设计.md 执行
```

模块设计记录唯一来源 GDD；插件会自动读取该 GDD 取得产品规则，用户不需要在口令中再次指定。这个阶段不能重新拆分模块，只能把已确认的模块职责和角色规划细化为具体类型、公开签名、文件路径和适合逐份实施的 MDD，并生成简洁索引与 `M999_项目集成收敛.md`。

### 实施一份 MDD

```text
$july-game-pipeline @DesignDoc/MDD/M002_每日题目.md 执行
```

一次只实施一份明确指定的 MDD。当前 MDD 是本次功能范围的唯一授权来源；插件不会自动实现下一份 MDD，也不会在其他角色中预埋未声明功能。

## 执行与覆盖

- 对策划案、GDD 或模块设计说“执行”时，如果紧邻的下游目标不存在就直接生成；目标已存在则先询问是否更新。
- 对 MDD 说“执行”时直接进入实施前检查；已有代码由 MDD 决定创建、修改或复用，不额外询问是否更新代码。
- 一次确认只授权当前紧邻阶段，不自动级联更新后续设计或代码。
- 仍可使用“生成 GDD”“更新模块设计”“更新全部 MDD”“实施”等明确动作覆盖默认选择；动作必须与输入文档类型匹配。

## 文件定位

- 只说“执行”时必须通过 `@` 明确指定且只指定一份 Markdown 文件。
- 使用明确动作但没有 `@` 时，只在当前项目中寻找名称和结构都明确且唯一的对应输入；目录可以叫 `DesignDoc`，但不要求固定名称。
- 找不到文件或存在多个无法判断的候选时，插件会说明未执行，并要求用户明确指定。
- 新生成的 GDD、模块设计和 MDD 都写入稳定文档类型标识；已有规范产物可按旧结构兼容识别。
- “生成”可以创建目标文档；“更新”保留未被新输入推翻的有效内容。
- “重新生成”只适用于 GDD；MDD 第一版只支持生成全部或更新全部。

## 实施边界

- 只修改 C# 代码、Luban 作者源以及本流程生成的 GDD、模块设计与 MDD 文档。
- 使用项目当前真实存在的 JulyFramework、JulyArch、UI 组件和 Luban 接口。
- 每个 Window 都必须有 WindowData；Window 只根据 Data 渲染，并通过 System 发起业务动作。
- Window 类型名固定以 `UI` 开头、以 `Window` 结尾；对应常量统一位于 `UIWindowID`，字段名与 Window 一致并对应 `TbUIWindow` 的 ID。
- 项目 System 直接使用具体类型；不生成项目级 `IXXSystem`、静态业务容器、成功失败 `Result` 包装或无明确边界的数据快照。
- 产品运行时代码按独立业务决策及一致性所有权放在 `Runtime/Modules/<模块名>`；共同变化是归组证据，模块数量更少只在边界同样正确时作为次级选择。模块边界先于 JulyArch 角色确定，每个模块最多一个项目业务 System、最多一个项目业务 Store，也可以缺少任一角色；`Modules` 下不要求独立 asmdef。
- 模块设计记录来源 GDD；每份 MDD 同时记录来源模块设计和来源 GDD。产品规则以 GDD 为准，模块职责和角色规划以模块设计为准，具体实施范围以当前 MDD 为准。
- 第一版不创建项目业务 ConfigSystem、ContentSystem 或配置聚合入口；各业务模块直接使用框架 `IConfigSystem`，C# 不重复 Luban 已保存的具体配置事实。
- 默认信任 Framework 生命周期、Luban 生成配置和模块内部契约；不生成启动巡检、重复状态校验或只为更友好报错存在的防御代码，只有错误会继续运行并污染状态或 GDD 明确要求恢复时才校验。
- 新增 Luban 业务作者源 Excel 使用“中文业务名_英文标识.xlsx”；控制文件保持 Luban 固定名称，已有作者源不自动重命名。
- 普通 MDD 实施完成后要求编译通过，但不要求立即形成可见或可玩的完整闭环。
- 普通 MDD 的前置依赖必须存在可执行顺序，不能循环等待。
- 跨 MDD 的延后连接登记到 `M999_项目集成收敛.md`，最后由用户明确指定后统一实施。
- 不生成图片、Prefab、Scene、材质、动画、音频、美术计划或测试代码。

## 仓库结构

```text
.agents/plugins/marketplace.json
plugins/july-ai-workflow/
  .codex-plugin/plugin.json
  skills/july-game-pipeline/
    SKILL.md
    agents/openai.yaml
    references/
      gdd.md
      module-design.md
      mdd.md
      implementation.md
      july-architecture.md
      july-ui-components.md
```

Skill 保持最小结构。规则集中在入口和六份按动作加载的参考文档中，不依赖脚本、流程状态文件或额外机器契约。
