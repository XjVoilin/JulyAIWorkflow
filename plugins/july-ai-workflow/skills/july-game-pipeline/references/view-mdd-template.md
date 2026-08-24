# View MDD 模板

每份 `Design/Docs/MDD/Views/V<N>_<视觉功能>.md` 描述一个玩家可见屏幕或视觉功能。目录不按 UI 与 2D 技术类型拆分；在 MDD 内声明实际形态。View 必须位于索引全产物拓扑序中，所用模块类型、生成类型、事件和资源必须已经由更早 MDD 提供或由当前白名单创建。

# V<N>_<视觉功能>

## 1. 视觉责任

- 对应 GDD：
- 玩家在何时看到：
- 视觉目标：
- 形态：Window / GameView / Window + GameView
- 包含区域：
- 明确排除：
- 打开/出现条件：
- 关闭/消失条件：

有设计图、Prefab 或场景时必须实际查看并记录信息层级、交互和制作约束。

## 2. 可见事实

| 视觉区域 | 玩家看到的事实 | 权威来源 | Data 字段 | 初始取得方式 | 变化通知 |
| --- | --- | --- | --- | --- | --- |
|  |  | Store/System/Luban/框架事实 |  |  | 空事件/不变化 |

View 不计算业务规则。格式化、颜色、动画进度等表现事实可以由 View 拥有；业务结论必须来自权威模块。

## 3. 玩家交互

| 动作 ID | 控件/场景交互 | 玩家意图 | 调用对象 | 规范调用 | 成功反馈 | 允许失败反馈 | 导航责任 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A___ |  |  | 业务System/UISystem/WindowData |  |  |  |  |

规则：

- Window 按钮可以直接调用业务 System 的公开方法；
- 纯表现导航由 Window 直接调用 UISystem；
- 依赖业务成功的导航由业务 System 或 Procedure 在成功后执行；
- Window 不修改 Store，不构造或运行 Procedure；
- GameView 的输入路径按当前工程和实际责任设计。
- 每一行必须引用索引动作合同；同一动作的参数、返回、失败与导航所有者不得在 View 中改写。
- 打开选择页面和确认选择提交若触发时机或输入不同，必须引用不同动作 ID。

## 4. WindowData 合同

每个 Window 强制拥有 Data。Window 打开期间始终持有同一个 Data 对象。

WindowData：

- 字段/属性可写，便于 GM/编辑器工具创建并赋值代表性展示数据；
- 仅实现实际需要的 `ICanGetStore`、`ICanGetSystem` 等当前 July 查询接口；
- 正常构造时直接从 Store/System 取得完整初始展示数据；
- 提供按视觉区域或事实命名的定向刷新方法；
- 每个定向刷新方法内部自行从 Store/System 读取最新事实；
- 不提供 `RefreshAll`；
- 不承担业务权威、业务规则、状态推进或存档。
- 使用的 Store/System/生成类型必须来自更早 MDD；如果提供者排在当前 View 之后，设计没有闭包。

### 字段

| 字段 | 类型 | 可写性 | 展示区域 | 来源 | 初始赋值 |
| --- | --- | --- | --- | --- | --- |
|  |  | public set/field |  |  | constructor |

### 定向刷新方法

| 方法 | 刷新字段 | 读取 Store/System | 对应空事件 | Window 重绘区域 |
| --- | --- | --- | --- | --- |
| `Refresh<Region>()` |  |  |  |  |

### C# 草图

以下只表达责任，继承和查询 API 必须按当前固定 July 版本填写：

```csharp
public sealed class CapabilityWindowData
    /* : required July WindowData base,
         ICanGetStore<CapabilityStore>,
         ICanGetSystem<CapabilitySystem> */
{
    public int Progress { get; set; }
    public bool CanExecute { get; set; }

    public CapabilityWindowData()
    {
        var store = /* GetStore<CapabilityStore>() */;
        var system = /* GetSystem<CapabilitySystem>() */;

        Progress = store.Progress;
        CanExecute = system.CanExecute();
    }

    public void RefreshProgress()
    {
        Progress = /* GetStore<CapabilityStore>() */.Progress;
    }

    public void RefreshAvailability()
    {
        CanExecute = /* GetSystem<CapabilitySystem>() */.CanExecute();
    }
}
```

GM/编辑器工具可以按当前 UI 打开合同创建该 Data、覆盖可写字段并打开 Window，以检查极值、空内容和不同组合。不要为此建立第二套测试 DTO。

## 5. Window 合同

Window 只从其 Data 渲染。它不直接读取 Store/System 来拼装展示数据。

```csharp
public sealed class CapabilityWindow /* : exact July Window base */
{
    private CapabilityWindowData Data { get; set; }

    private void OnOpen(CapabilityWindowData data)
    {
        Data = data;
        RenderInitial();
        SubscribeEvents();
    }

    private void OnCapabilityProgressChanged(CapabilityProgressChanged _)
    {
        Data.RefreshProgress();
        RenderProgress();
    }

    private void OnExecuteClicked()
    {
        /* GetSystem<CapabilitySystem>() */.Execute();
    }

    private void OnPureNavigationClicked()
    {
        /* GetSystem<UISystem>() */.OpenWindow(...);
    }
}
```

必须逐项设计：

- Data 如何按项目标准方式传入并在打开期间保持；
- 初始完整渲染方法；
- 每个视觉区域的局部渲染方法；
- 空事件的订阅与取消订阅生命周期；
- 每个按钮调用的业务 System 或 UISystem；
- 业务成功后导航发生的位置。

事件处理固定为：“收到空事件 → 调用 Data 指定刷新方法 → 刷新对应视觉区域”。

## 6. 业务事件

| 空事件 | 所属模块 | 发布者 | 发布条件 | Data 刷新方法 | Window 渲染方法 |
| --- | --- | --- | --- | --- | --- |
|  |  | Store/System | 一致变更完成后 |  |  |

事件类型不含业务数据、WindowData、旧值或新值。View 需要多个区域分别更新时使用清楚的业务变化事件和对应定向刷新，不以一个全局刷新事件替代。事件类型必须由拥有业务变化的更早模块 MDD 已经提供。

## 7. GameView 合同

仅在包含非 Window 的场景/世界表现时填写。不要强制套用 WindowData 规则。

- 绑定的场景对象和 Unity 生命周期：
- 业务驱动还是纯表现：
- 是否需要独立 Data，理由：
- 数据来源与刷新方式：
- 交互发布或 System 调用：
- 动画/临时选择等表现数据：
- 与 Window 的组合关系：

GameView 可以拥有动画进度和临时表现状态，但不能复制 Store 事实或计算业务结论。

## 8. Prefab、场景与资源

| 资产/对象 | 精确路径 | 组件/引用 | 制作要求 | 验证方式 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

记录：

- 层级与布局；
- 字体、图集、图片和本地化；
- 序列化引用；
- Window 配置/provider/资源地址；
- 目标分辨率和适配；
- 场景对象、排序、动画与输入；
- 缺失资源是否会改变设计。

## 9. 精确文件白名单

### 新增

```text
<逐个列出 WindowData、Window/GameView、Events、Prefab/资源等准确文件>
```

### 修改

```text
<逐个列出 Window 配置、Prefab、场景、本地化等准确文件及目的>
```

实施不得创建或修改白名单外产品文件。事件文件归属于拥有业务变化的模块；如果事件已由模块 MDD 声明，View MDD 只列为读取依赖，不重复创建。

## 10. 单份 MDD 闭包证明

| 引用的产品符号/文件/动作 ID | 提供者 | 稳定宿主/更早 MDD/当前 MDD | 已可用依据 |
| --- | --- | --- | --- |
|  |  |  |  |

逐项覆盖：Window 基类与配置、WindowData 使用的 Store/System、字段中的生成类型、业务事件、按钮规范调用、Prefab 脚本、本地化与资源。

闭包结论必须明确：

- 当前白名单一起创建后可以 Unity 编译；
- 不引用后续 Module/View 的类型或资源；
- 当前 Prefab/Inspector 和 GM 代表数据验收不需要后续 MDD；
- 动作签名和导航所有者与索引及模块 MDD 完全一致。

任一项不成立时，重新设计动作、导航、产品符号所有权或实施顺序，不把缺口留给实施阶段。

## 11. 验收

至少包含适用项：

- Unity 程序集编译和 Console；
- Window 打开时由构造完成的 Data 正确首屏渲染；
- Window 打开期间 Data 对象不被替换；
- 每个空事件调用对应 Data 定向刷新并只更新目标区域；
- 没有 `RefreshAll`；
- Window 不直接从 Store/System 组装显示事实；
- 按钮直接调用正确业务 System，纯导航调用 UISystem；
- 业务成功导航由 System/Procedure 负责；
- GM/编辑器以可写 Data 打开代表数据并检查表现；
- Prefab/Inspector/场景引用与目标分辨率；
- GameView 表现与交互路径；
- 文件白名单一致；
- 没有业务规则、持久化占位或测试代码。
- 所有产品符号来自稳定宿主、自有或更早 MDD，所有动作合同逐字一致。

## 12. 明确不实施

- 业务 Store 写入和 Procedure 直接运行；
- Window 中的业务计算；
- 携带数据的业务变化事件；
- 全量刷新接口；
- 本 MDD 白名单外的视觉功能；
- 单元测试、PlayMode 测试及测试脚手架；
- 持久化注册、保存/读取、保存失败、跨启动恢复和服务器/本地存储设计。

## 13. 结构化 MDD 合同

从暂存区 `.july-design-contract.json` 的 `artifacts` 中复制本 MDD 的完整对象，不改名、不删字段、不另行解释：

````text
```july-mdd-contract
{本 MDD 的完整 Artifact JSON}
```
````

正文中的 ID、路径、依赖、动作、产品符号和文件白名单必须与此对象逐字一致。该块不是进度状态；它是索引合同在本 MDD 的机器可验证投影。
