# 模块 MDD 模板

每份 `Design/Docs/MDD/Modules/M<N>_<能力>.md` 是一个业务能力的完整实施合同。模板中的每节都必须得到具体答案；不适用时说明业务理由，不得用“实施时决定”替代结构设计。模块必须位于索引全产物拓扑序中，并且实施后可以独立编译验收。

# M<N>_<能力>

## 1. 能力定义

- 对应 GDD：
- 能力名称：
- 一句话责任：
- 玩家价值：
- 明确包含：
- 明确排除：
- 不负责的相邻能力及其所有者：

名称必须是稳定业务能力，不使用技术层、页面步骤、表格集合或宽泛容器名称。

## 2. 完整业务流程

列出由本模块发起或在本模块结束的完整玩家操作。跨模块调用直接写在这里。

### 流程：<玩家动作>

- 动作合同 ID：`A___`；
- 索引规范签名：
- 触发入口：
- 前置业务事实：
- 调用顺序：
- 本模块写入：
- 其他模块调用：
- 成功结果：
- GDD 允许的失败：
- 发布的空业务事件：
- 参与 View 及反馈：
- 导航责任：

用伪代码表达真实顺序：

```text
OwningSystem.PublicOperation(input)
    validate input boundary once
    read authoritative facts
    if bounded multistep work is required
        run OwningProcedure
    else
        calculate result
        owningStore.Apply(result)
    after success
        perform business-dependent navigation when required
```

不要把完整流程放入独立联通文件或总协调对象。同一动作的签名、失败合同和导航所有者必须与索引动作表及所有 View MDD 完全一致；本 MDD 不重新定义第二套合同。

## 3. 事实与数据所有权

| 事实 | 类型/形状 | 权威来源 | 写入者 | 读取者 | 更新时机 | 是否派生 |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

要求：

- 与索引的全局事实表一致；
- Store 只保存模块拥有的运行时事实；
- Luban 只保存作者事实；
- July/Unity 已提供的事实不复制；
- 派生值写明公式或算法，不成为重复字段；
- WindowData 不列为业务权威来源。

## 4. 实施依赖与消费者

### 前置 MDD

| 提供 MDD/稳定宿主 | 使用的产品符号/动作 ID | 依赖类型 | 必须先完成的原因 |
| --- | --- | --- | --- |
|  |  | 编译/Luban作者/注册/运行时合同 |  |

### 消费者

| 消费者 | 使用内容 | 调用时机 |
| --- | --- | --- |
|  |  |  |

每个产品符号都必须能在索引唯一提供表找到提供者。前置 MDD 必须位于全局实施顺序更早位置。不得依赖后续 Module、View、Luban Bean/枚举、WindowData、Event 或注册项，也不得把 Prefab 脚本或资产声明为 MDD 依赖。

确认本模块加入全产物依赖图后仍无环。若需要反向调用，重新检查事实、动作、导航或符号是否归错所有者。

## 5. 角色清单

| 类型 | 角色 | 核心责任 | 生命周期/创建位置 | 选择理由 |
| --- | --- | --- | --- | --- |
|  | Store/System/Procedure/普通类型/Luban生成类型/Event |  |  |  |

角色判断：

- Store：受控运行时业务状态；
- System：通过 `ArchContext` 管理或定位的稳定运行时能力；不要求复杂度或多个消费者；
- Procedure：一次有界、多步骤、异步、可取消或有提交点的操作；
- 普通类型：真实算法、不变量或值语义；
- Luban 生成类型：静态作者事实；
- Event：模块拥有事实变化后的空通知。

没有责任的角色不创建。模块可以只包含配置产物。

## 6. C# 数据结构草图

使用接近最终代码的 C# 形状，明确可见性、可写边界和字段类型。API 名称以当前固定 July 版本核实结果为准。

### Store 与 Data

```csharp
public sealed class CapabilityData
{
    public int VisibleValue { get; internal set; }
}

public sealed class CapabilityStore /* : exact July Store base */
{
    public CapabilityData Data { get; }

    public int VisibleValue => Data.VisibleValue;

    internal void ApplyValue(int value)
    {
        Data.VisibleValue = value;
        // Publish empty CapabilityValueChanged after state is consistent.
    }
}

public readonly struct CapabilityValueChanged
{
}
```

Store 对外公开读取，写方法限制在拥有模块可用范围。事件没有数据字段。

### System

```csharp
public sealed class CapabilitySystem /* : exact July System base */
{
    public OperationResult Execute(OperationInput input)
    {
        // Simple synchronous operation may complete here.
        // Multistep/async/cancellable operation delegates to a Procedure.
    }
}
```

System 方法表达业务动作，不做纯转发。

### Procedure

```csharp
public sealed class ExecuteCapabilityProcedure /* : exact July Procedure base */
{
    public async Task<OperationResult> ExecuteAsync(OperationInput input)
    {
        // Read dependencies, perform bounded work, commit through owning Store.
    }
}
```

只有真实有界操作才创建 Procedure。

### 普通算法/值类型

```csharp
public readonly struct OperationResult
{
    // Fields and invariants required by real consumers.
}

public static class CapabilityRule
{
    public static OperationResult Evaluate(/* authoritative inputs */)
    {
        // Deterministic business algorithm.
    }
}
```

不要为了命名方便创建没有行为的 Definition、镜像 DTO 或查表包装。

## 7. 公共接口合同

逐项写出模块外可使用的具体合同：

| 动作 ID | 所有者 | 规范成员签名 | 输入来源 | 返回/写入 | 失败合同 | 调用者 |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

约束：

- 直接使用具体 JulyArch 角色，不为模块统一创建 `Ixxx` 门面；
- 输入只包含操作真正需要的权威事实，不把未知事实压缩成占位布尔值；
- 内部不变量违约快速失败；
- 业务允许失败使用明确结果，不返回伪成功；
- 调用者必须是本次完整设计中已知的模块或 View。
- 签名必须逐字匹配索引动作合同，不能出现无参数预调用和另一处带参数正式调用同属一个动作。

## 8. 核心算法伪代码

每条规则写到足以判断所有权、输入、分支和结果，不只写方法名。

```text
Result Calculate(authoritativeInputA, authoredRowB)
    require boundary input is valid
    derivedValue = formula(authoritativeInputA, authoredRowB)
    if GDD-defined failure condition
        return explicit failure
    return explicit success(derivedValue)
```

说明：

- 算法使用哪些权威事实；
- 哪些检查位于外部边界；
- 哪些条件由类型/生成/生命周期保证而内部信任；
- 成功时由谁提交 Store；
- 何时发布哪个空事件；
- 是否以及为何需要 Procedure。

## 9. 业务事件

| 事件 | 所有者 | 发布条件 | 订阅者 | 订阅者刷新动作 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

业务事件只能表示事实已变化，不携带旧值、新值、WindowData 或计算结果。Store/System 在一致变更完成后发布。View 收到后调用自身 Data 的定向刷新方法。

## 10. Luban 配置合同

没有配置时写“本能力没有作者配置”，并说明规则来源。

有配置时完整列出：

### 作者源与生成

- 作者源目录：
- 表/Bean/枚举身份：
- 生成 C# 类型：
- 生成数据位置：
- 加载/注册入口：
- 直接消费者：

### Schema

| 表/Bean | 字段 | 类型 | 键/索引 | 含义 | 约束 | 所有者 | 消费者 | 示例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |

### 必要性检查

- 每个字段为什么是作者事实；
- 是否能从其他表、枚举、行数、时间或运行时事实派生；
- 是否错误地放入杂项配置；
- 是否存在手写镜像类型；
- 全量生成如何验证。

## 11. 注册与初始化

| 对象/配置 | 注册或加载位置 | 顺序 | 前置依赖 | 不注册的普通对象 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

只注册 Store/System 等框架管理对象。普通类型、Procedure、WindowData 和 Luban Bean 不作为长期角色注册。写出当前工程中的准确文件和组合位置。Store 不接入持久化系统，不登记保存键，不设计恢复顺序。

## 12. 新类型必要性审查

| 候选类型 | 删除后直接使用什么 | 会损失的独立责任 | 结论 |
| --- | --- | --- | --- |
|  |  |  | 创建/删除 |

无法写出独立行为、不变量、状态、生命周期或错误合同的候选类型必须删除。模块成立不要求手写产品类型。

## 13. 精确文件白名单

### 新增

```text
<逐个列出相对产品根目录的准确文件>
```

### 修改

```text
<逐个列出准确文件及修改目的>
```

### Luban 派生输出

```text
<仅列出由全量生成产生且预期变化的文件>
```

实施不得创建或修改白名单外的产品文件。发现缺项时先讨论并更新 MDD。

## 14. 单份 MDD 闭包证明

### 可用输入

| 引用的产品符号/文件/动作 ID | 提供者 | 稳定宿主/更早 MDD/当前 MDD | 已可用依据 |
| --- | --- | --- | --- |
|  |  |  |  |

逐项覆盖：基类、成员签名中的类型、生成 Bean/枚举、事件、Window/WindowData、注册项与作者源依赖。Prefab 不属于结构化闭包。

### 闭包结论

- 当前 MDD 白名单内文件一起创建后，不引用任何后续 MDD 产物；
- Unity 编译不要求后续 Module 或 View 提供类型；
- Luban 全量生成不要求后续 MDD 定义 Bean、枚举或表；
- 当前验收不要求打开后续 Window 或完成后续玩家流程，也不以任何 Prefab 作为前置；
- 若任一条不能成立，停止定稿并重新设计责任或 MDD 边界。

## 15. 验收

按实际范围选择并写成可重复步骤：

- Unity 程序集编译和 Console 无新增错误；
- Store/System/Procedure 的准确注册与调用；
- 核心规则通过编辑器或现有 GM 入口观察；
- Luban 全量生成、schema 与代表性生成产物；
- 完整玩家操作的成功与 GDD 允许失败；
- 空事件发布后对应 View 定向刷新；
- 文件白名单与实际差异一致；
- 没有多余类型、接口、目录、TODO、工具残留、持久化占位或测试代码。
- 所有动作签名与索引和 View MDD 一致；所有引用符号均来自稳定宿主、自有或更早 MDD。

## 16. 明确不实施

固定包含：

- 持久化注册、保存/读取调用、保存失败、跨启动恢复、本地/服务器存储、仓储、迁移和占位接口；
- 单元测试、PlayMode 测试、测试 asmdef、Mock、Fake、Fixture；
- 本 MDD 白名单外的能力和 View；
- 为未来需求预留的空角色、默认成功或兼容层。

## 17. 结构化 MDD 合同

从暂存区 `.july-design-contract.json` 的 `artifacts` 中复制本 MDD 的完整对象，不改名、不删字段、不另行解释：

````text
```july-mdd-contract
{本 MDD 的完整 Artifact JSON}
```
````

正文中的 ID、路径、依赖、动作、产品符号和文件白名单必须与此对象逐字一致。该块不是进度状态；它是索引合同在本 MDD 的机器可验证投影。
