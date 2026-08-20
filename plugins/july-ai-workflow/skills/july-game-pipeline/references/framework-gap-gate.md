# 框架能力缺口 Gate

当任一阶段发现目标项目需要的能力在当前 July Framework 精确 pin 中不存在或契约不足时，使用本 Gate。目标是先确定责任边界，再决定是否停止产品流程；不能因为实现方便就把产品需求升级为框架能力，也不能在产品项目里复制应由框架拥有的基础设施。

## 1. 缺失判定

先收集以下证据：目标 `Packages/manifest.json` 的不可变 pin、对应 package 的公开接口与测试、模板组合方式，以及 MDD 中真实消费者。然后做所有权判断：

- **产品拥有**：玩法规则、内容、产品状态、场景/UI、项目组合、Provider 选择、只针对一个平台或产品的 adapter。继续产品流程，并在 MDD 中定义。
- **框架拥有**：能被多个产品复用，属于已有 July package 的职责，却缺少必要公开契约、生命周期、可靠性或测试能力；或者新增能力有清晰稳定的跨产品合同。判定为 `July Framework 缺失`。
- **尚不明确**：消费者和稳定合同不足，或只有假设中的第二个使用者。停止当前实现并先讨论，不创建“未来可能复用”的框架抽象。

具体框架缺陷、为什么可能发生、期望失败行为和消费者必须能够被说明；无法说明时，不添加兜底或抽象。

## 2. 阻塞动作

确认框架缺失后：

1. 从 [框架缺口模板](../assets/templates/FRAMEWORK_GAP.md) 创建 `DesignDoc/<项目名>/框架缺口/FG-<编号>_<能力>.md`。
2. 记录精确 pin 证据、最小跨产品合同、包归属、备选方案、迁移影响、包级测试和恢复条件，并与用户讨论方案。
3. 将方案 Gate 设为 `BLOCKED`，执行：

```text
python scripts/flow.py block --product <项目名> --stage <当前阶段> --reason <缺失摘要> --proposal DesignDoc/<项目名>/框架缺口/FG-<编号>_<能力>.md
```

4. 停止产品阶段。禁止在产品代码中复制该能力、建立临时兼容层、用私有抽象遮住缺口，或完成当前 Stage。

框架仓库中的修改是独立工作范围；未经用户授权，不因本 Gate 自动修改、发布或推送框架。

## 3. 框架补充完成条件

恢复产品流程前必须同时满足：

- 方案中的包归属和公开合同已经确认；
- 框架实现遵循边界验证、内部不变量快速失败，没有产品特例；
- package-level 测试通过，并覆盖合同、生命周期和已知失败语义；
- 新框架版本以不可变 tag/version 发布；
- 目标项目 `Packages/manifest.json` 已更新到该版本及正确依赖闭包；
- 目标项目完成编译或最小集成测试，证明真实消费者可使用新能力；
- 方案文档补充版本、测试、目标 pin 和集成证据，并把 Gate 改为 `RESOLVED`。

另一种合法解除方式是用户明确把触发缺口的能力移出当前版本范围。此时不伪造框架完成证据；必须先更新 GDD 的玩家可观察范围、更新 GDD 审查并保持 Gate PASS，在缺口方案中记录范围决定及未来重新启用时必须重新进入本 Gate，然后把方案 Gate 改为 `RESOLVED`。

## 4. 恢复动作

执行 `resume`，证据必须包含同一方案、目标 `Packages/manifest.json` 和至少一份框架/目标集成验证文件：

```text
python scripts/flow.py resume --product <项目名> --stage <当前阶段> --resolution <完成说明> \
  --evidence DesignDoc/<项目名>/框架缺口/FG-<编号>_<能力>.md \
  --evidence Packages/manifest.json \
  --evidence <框架或目标项目验证报告>
```

`resume` 只恢复原 Stage 为 `in_progress`；不会自动接受旧设计或完成该阶段。恢复后重新核对精确 pin 接口，必要时更新 MDD，再继续实现。

若通过范围调整解除，使用：

```text
python scripts/flow.py resume --product <项目名> --stage <当前阶段> \
  --resolution-kind scope_change --resolution <范围调整说明> \
  --evidence DesignDoc/<项目名>/框架缺口/FG-<编号>_<能力>.md \
  --evidence DesignDoc/<项目名>/GDD.md \
  --evidence DesignDoc/<项目名>/QA_GDD.md
```

范围调整只证明当前版本不再消费缺失能力；它不表示框架已经补齐。未来把该能力重新加入范围时，必须重新核对框架并在仍缺失时重新阻塞。
