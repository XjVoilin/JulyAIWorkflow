# 结构化设计合同与产物工具

结构化合同是完整设计的机器权威。它不是项目进度、运行时状态或额外设计文档：设计期间保存为系统临时目录中的 `.july-design-contract.json`，发布后只以内嵌 JSON 的形式存在于 `MDD/索引.md` 和各 MDD 中。

工具位于本 Skill 的 `scripts/design_artifacts.py`，只使用 Python 标准库。

## 命令

```text
python scripts/design_artifacts.py create-stage --workspace <产品根目录>
python scripts/design_artifacts.py validate --source <暂存 Design/Docs 根目录> --mode partial --surface staging --workspace <产品根目录>
python scripts/design_artifacts.py validate --source <暂存 Design/Docs 根目录> --mode full --surface staging --workspace <产品根目录>
python scripts/design_artifacts.py validate --source <正式 Design/Docs 根目录> --mode full --surface published
python scripts/design_artifacts.py publish --staging <暂存 Design/Docs 根目录> --workspace <产品根目录>
python scripts/design_artifacts.py discard-stage --staging <本轮暂存目录>
```

`create-stage` 返回唯一系统临时目录，并写入 `.july-design-stage.json`，绑定产品根目录、策划案摘要和 Unity 项目版本。它只是本次事务的边界证明，不记录进度或工作流状态，不发布到产品。只在该目录生成 `.july-design-contract.json`、`GDD.md`、`MDD/索引.md`、`MDD/Modules/*.md` 和 `MDD/Views/*.md`。

`partial` 验证完整合同及已经生成的文档，允许合同中声明的部分 MDD 尚未出现。`full` 要求所有声明文件存在。`staging` 强制独立合同存在并与索引一致，同时核对暂存区确实属于 `--workspace` 且策划案、Unity 版本没有变化；`published` 强制正式目录不存在独立合同或暂存元数据。`publish` 会先做完整验证，把正式 `Design/Docs` 复制为同卷候选目录，只替换其中的 GDD/MDD、清除遗留临时合同，再以目录交换发布；普通失败会恢复旧设计。禁止手工逐文件发布。

`discard-stage` 只接受由 `create-stage` 创建、位于系统临时目录、名称以 `july-design-` 开头且包含有效绑定元数据的目录。验证或发布未完成时也应清理本轮暂存区；不要删除无法证明属于本轮的目录。

## 顶层合同

JSON 必须且只能包含以下字段：

```json
{
  "schemaVersion": 1,
  "product": "当前产品名",
  "artifacts": [],
  "actions": [],
  "implementationOrder": []
}
```

`artifacts` 必须按 `implementationOrder` 排列。Module 与 View 可交错；同种 MDD 的编号按它在全局顺序中的出现次序从 001 连续递增。

## Artifact 合同

每份 MDD 使用一个对象：

```json
{
  "id": "M001",
  "kind": "module",
  "title": "稳定业务能力名",
  "path": "MDD/Modules/M001_稳定业务能力名.md",
  "dependsOn": [],
  "actionsOwned": ["A001"],
  "actionsUsed": [],
  "provides": [
    {
      "id": "Product.CapabilitySystem",
      "kind": "CSharpType",
      "location": "Assets/Product/Runtime/CapabilitySystem.cs"
    }
  ],
  "consumes": [],
  "files": {
    "create": ["Assets/Product/Runtime/CapabilitySystem.cs"],
    "modify": ["Assets/Product/Runtime/ProductContext.cs"],
    "generated": []
  }
}
```

View 使用 `V001`、`kind: "view"` 和 `MDD/Views/`。路径全部相对产品根目录并使用 `/`。同一 MDD 的 `create`、`modify`、`generated` 不能重复；列表总和不能为空；同一产品文件不能由多份 MDD 声明创建。目标项目测试代码和 Editor 工具代码不能进入白名单；业务所需的作者数据、Prefab 与其他制作资产仍归实际 Module/View。

`provides` 列出所有被其他 MDD 使用的手写类型/成员/Event、Luban 类型、Window/Data、Prefab/资源合同和注册项。`id` 是全局唯一稳定标识。`location` 是准确文件或作者源。

`consumes` 逐项列出跨 MDD 消费：

```json
{
  "symbol": "Product.CapabilitySystem",
  "provider": "M001",
  "dependencyType": "compile",
  "reason": "V001 的按钮调用该业务动作"
}
```

`dependencyType` 写明 `compile`、`luban-authoring`、`registration`、`prefab` 或 `runtime-contract`。每个跨 MDD 消费的 provider 必须进入 `dependsOn`；每个 `dependsOn` 又必须由消费符号或使用该 owner 的动作证明，不能保留模糊依赖。

## Action 合同

每个原子玩家动作只出现一次：

```json
{
  "id": "A001",
  "intent": "玩家意图",
  "kind": "business",
  "owner": "M001",
  "signature": "CapabilitySystem.Execute(Input input)",
  "precondition": "准确前置",
  "success": "准确成功结果",
  "failure": "GDD 允许失败；无则写无",
  "navigationOwner": "CapabilitySystem",
  "navigationTarget": "成功后目标；无则写无",
  "gdd": "GDD 对应章节"
}
```

`kind` 可写 `business`、`navigation` 或 `view-local`。`owner` 必须是某一 MDD。该 MDD 的 `actionsOwned` 必须精确列出它拥有的全部动作；其他使用者放入 `actionsUsed` 并依赖 owner。每份相关 MDD 的正文必须逐字包含动作 ID 和 `signature`。

## 文档嵌入

索引末尾的“结构化设计合同”章节嵌入完整顶层 JSON：

````text
```july-design-contract
{完整 JSON}
```
````

每份 MDD 末尾嵌入它在 `artifacts` 中的完整对象：

````text
```july-mdd-contract
{该 Artifact JSON}
```
````

不要手工维护两套含义不同的表。先固定临时 JSON，再让索引表格、MDD 正文和内嵌块都从同一合同展开；验证器会拒绝内嵌合同与临时合同不一致、动作/符号重复、前向依赖、缺失文件、额外 MDD、占位内容、持久化设计以及工具职责伪装成业务模块。
