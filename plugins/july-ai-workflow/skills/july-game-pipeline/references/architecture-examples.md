# 最小完整示例：一次制作

仅在需要校准职责粒度或解释完整调用链时读取。本文件不定义规则，也不是项目模板；角色、协作与复用规则分别见 [july-architecture.md](july-architecture.md) 和 [code-quality.md](code-quality.md)。不因读取本例改变当前工作流阶段的产物范围。

## 选择与适用范围

一次制作同步消耗固定材料并增加一件成品；材料不足或货架满时拒绝，两份计数都不变。它们只有同一项制作规则、同一生命周期，因此先放在一个所有者中。为两个计数另建库存类、货架类和协调层，没有隐藏额外知识。

下面是独立可编译的 C# 控制台示例，展示创建 → 输入适配 → 规则与状态修改 → 结果及状态读取 → 输出。它不依赖 July API：业务是否进入 System 由目标项目的定位与生命周期需求决定；需要时可以直接将这些成员放入 System，不必保留同形的内核包装。接入 July Window 时，显示映射仍由 WindowData 完成。

```csharp
using System;

public sealed class Workshop
{
    private readonly int materialCost;
    private readonly int productCapacity;
    public int MaterialCount { get; private set; }
    public int ProductCount { get; private set; }

    public Workshop(int initialMaterials, int productCapacity, int materialCost)
    {
        // 示例配置边界：非法值会造成错误扣料或容量判断。
        if (initialMaterials < 0)
            throw new ArgumentOutOfRangeException(nameof(initialMaterials));
        if (productCapacity < 0)
            throw new ArgumentOutOfRangeException(nameof(productCapacity));
        if (materialCost <= 0)
            throw new ArgumentOutOfRangeException(nameof(materialCost));

        MaterialCount = initialMaterials;
        this.productCapacity = productCapacity;
        this.materialCost = materialCost;
    }

    public bool TryMake()
    {
        if (MaterialCount < materialCost || ProductCount >= productCapacity)
            return false;

        // 单线程同步提交；两次写入之间没有回调或外部等待。
        MaterialCount -= materialCost;
        ProductCount++;
        return true;
    }
}

public static class WorkshopConsole
{
    public static void Main()
    {
        var workshop = new Workshop(5, 2, 2);
        RequestMake(workshop);
        RequestMake(workshop);
        RequestMake(workshop);
    }

    private static void RequestMake(Workshop workshop)
    {
        var accepted = workshop.TryMake();
        Console.WriteLine(
            $"accepted={accepted}, materials={workshop.MaterialCount}, products={workshop.ProductCount}");
    }
}
```

输入适配只发起意图和显示结果，不预判是否能制作。`TryMake` 拥有准入和完整修改，调用方不能绕过它写计数；当前只需要接受或拒绝，所以返回 `bool`。表现可以随时移除，不影响业务结果。

## 行为核对

| 配置或场景 | 预期行为 |
|---|---|
| 材料 5、容量 2、成本 2，连续请求三次 | 依次为 `True/3/1`、`True/1/2`、`False/1/2`，格式为接受/材料/成品 |
| 材料 1、容量 2、成本 2 | 拒绝，材料仍为 1，成品为 0 |
| 材料 4、容量 1、成本 2，第二次请求 | 拒绝，材料仍为 2，成品仍为 1；即使材料充足也不多扣 |
| 容量 0 | 拒绝，不消耗材料 |
| 负初始材料、负容量或非正成本 | 在创建边界抛出参数异常 |

这些结果验证规则，不规定内部类或字段形状。本文代码可独立验证，不替代目标项目的 Framework、配置与 UI 集成验证。

## 哪些变化会使这个形状失效

- **库存需要批次选择、独立共享或持久化：**库存成为独立所有者，隐藏选择和扣除规则；制作入口只协调真实的跨所有者操作。不能只把两个计数分别搬进空壳类。
- **制作需要等待或取消：**必须明确材料何时占用、何时消耗及取消后的处理，同步预检不能保证等待后仍有效。返回 `Task` 本身不解决这些问题。
- **需要显示每次制作过程：**最终计数不能恢复过程，已提交事实可以成为表现事件；只显示当前数量时继续读取即可。
- **引入远端或持久化写入：**本例没有异常回滚或并发保证，必须按一致性要求重新确定提交与故障处理边界。

跨场景评审同样检查有效期和提交语义：回合制按行动推进，无需固定 Tick；实时物理由物理步和接触事实确定顺序；编辑器撤销需要保留可恢复数据，不能照搬丢弃会话的失败策略。这些是默认方案的失效条件，不是要求项目预建对应机制。
