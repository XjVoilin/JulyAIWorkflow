# {产品名} — GDD 审查

> 版本：v1.0 | 日期：YYYY-MM-DD | 状态：draft
> 上游：`GDD.md` vX.Y

## 结论

- Gate：PASS / BLOCKED
- Blocker：0
- Major：0
- Minor：0

## 问题

### Q001 — {标题}

- 严重度：blocker / major / minor
- 证据：文档位置和冲突事实
- 影响：为什么会导致产品或实现错误
- 责任产物：策划案 / GDD
- 所需修正：可验证的修正结果
- 状态：open / resolved

## 覆盖检查

| 维度 | 状态 | 证据/说明 |
|---|---|---|
| 策划案目标与范围 | pass/fail |  |
| 核心循环与状态 | pass/fail |  |
| 胜负、退出、重试 | pass/fail |  |
| 交互与边界 | pass/fail |  |
| 内容、难度、持久化 | pass/fail |  |
| UI、文本与反馈 | pass/fail |  |
| July/平台可行性 | pass/risk/fail | 列出所需能力、当前证据，以及是否必须进入 MDD 框架充足性审计；不得以“包已安装”代替接口证据 |
| Luban 配置候选 | pass/fail |  |
| 验收场景可判定性 | pass/fail |  |

## 移交 MDD 的技术能力风险

| GDD 所需能力 | 当前工程证据 | 已验证/待验证 | MDD 必须回答的问题 |
|---|---|---|---|
|  | manifest pin/工程代码 | verified / requires MDD audit | 产品能力、现有框架能力或框架缺口？成功、缺失、损坏、取消、恢复和初始化结果是否都可由消费者区分？ |

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | YYYY-MM-DD | 初次审查 |
