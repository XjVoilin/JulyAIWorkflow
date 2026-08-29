# July AI Workflow

面向 JulyFramework、JulyArch 与 Luban 模板项目的 Codex 插件。插件只在显式调用 `$july-game-pipeline` 后运行，并将设计与实施拆成三个彼此独立的动作：

1. 按照策划案生成 GDD；
2. 按照 GDD 生成全部 MDD；
3. 按照用户指定的一份 MDD 实施代码与配置。

插件不维护流程状态，也不会自动进入下一步。

## 安装

在 Codex 中把本仓库添加为个人 Marketplace，然后安装 `July AI Workflow`。更新仓库中的插件版本后，需要在 Codex 中重新安装或更新插件，并新建任务使新版本生效。

仓库地址：<https://github.com/XjVoilin/JulyAIWorkflow>

## 使用

在已经由 July 模板创建好的 Unity 项目中开启 Codex 任务，并显式输入下列一种请求。

### 策划案生成 GDD

```text
$july-game-pipeline 按照 @DesignDoc/策划案.md 生成 GDD
```

GDD 只描述游戏产品设计，不写 JulyArch、类、接口、文件路径或 Luban 技术方案。遇到会实质影响产品设计的歧义时，插件一次只询问一个问题，并给出推荐项。

### GDD 生成全部 MDD

```text
$july-game-pipeline 按照 @DesignDoc/GDD.md 生成全部 MDD
```

插件按清晰职责拆分 MDD，生成一个简洁索引、全部普通 MDD，以及 `M999_项目集成收敛.md`。MDD 负责确定 JulyArch 角色、跨职责契约、WindowData、UI 代码结构与 Luban 作者源改动。

### 实施一份 MDD

```text
$july-game-pipeline 按照 @DesignDoc/MDD/M002_每日题目.md 实施
```

一次只实施一份明确指定的 MDD。当前 MDD 是本次功能范围的唯一授权来源；插件不会自动实现下一份 MDD，也不会在其他角色中预埋未声明功能。

## 文件定位

- 优先使用用户通过 `@` 明确指定的 Markdown 文件。
- 没有 `@` 时，只在当前项目的设计文档目录中按名称和语义寻找唯一候选；目录可以叫 `DesignDoc`，但不要求固定名称。
- 找不到文件或存在多个无法判断的候选时，插件会说明未执行，并要求用户明确指定。
- “生成”可以创建目标文档；“更新”保留未被新输入推翻的有效内容。
- “重新生成”只适用于 GDD；MDD 第一版只支持生成全部或更新全部。

## 实施边界

- 只修改 C# 代码、Luban 作者源以及本流程生成的 GDD/MDD 文档。
- 使用项目当前真实存在的 JulyFramework、JulyArch、UI 组件和 Luban 接口。
- 每个 Window 都必须有 WindowData；Window 只根据 Data 渲染，并通过 System 发起业务动作。
- Window 类型名固定以 `UI` 开头、以 `Window` 结尾；对应常量统一位于 `UIWindowID`，字段名与 Window 一致并对应 `TbUIWindow` 的 ID。
- 项目 System 直接使用具体类型；不生成项目级 `IXXSystem`、静态业务容器、成功失败 `Result` 包装或无明确边界的数据快照。
- 产品运行时代码按共同变化的业务知识放在 `Runtime/Modules/<模块名>`；模块边界先于 JulyArch 角色确定，每个模块最多一个项目业务 System、最多一个项目业务 Store，也可以缺少任一角色。共享 Store、MDD、调用方数量和代码规模不单独决定模块归属。
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
      mdd.md
      implementation.md
      july-architecture.md
      july-ui-components.md
```

Skill 保持最小结构。规则集中在入口和五份按动作加载的参考文档中，不依赖脚本、流程状态文件或额外机器契约。
