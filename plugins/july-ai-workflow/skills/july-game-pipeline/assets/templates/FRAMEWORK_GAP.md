# FG-<编号>：<框架能力>

> 版本：v1.0 | 日期：YYYY-MM-DD | 状态：reviewed
> 当前产品：<项目名> | 当前阶段：<stage>

- 分类：July Framework 缺失
- Gate：BLOCKED
- 解决方式：pending / framework_update / scope_change
- 目标项目当前 pin：`<package>@<immutable-version>`
- 建议归属：`<July package>`

## 缺失判定

- 真实消费者：
- 当前公开合同证据：
- 缺失的最小能力：
- 为什么属于框架而不是产品：
- 具体失败方式与期望行为：

## 框架补充方案

### 最小公开合同

### 生命周期与失败语义

### 包内实现边界

### 不采用的方案

## 影响与迁移

- 受影响产品模块：
- 目标 manifest/依赖闭包变化：
- 兼容性与迁移：

## 验证计划

- package-level tests：
- 模板/集成验证：
- 目标产品验证：

## 恢复条件

### 路径 A：框架补充

- [ ] 方案已确认
- [ ] 框架实现与 package tests 通过
- [ ] 不可变版本已发布
- [ ] 目标项目 pin 已更新
- [ ] 目标集成验证通过
- [ ] 本文 Gate 已改为 `RESOLVED`

### 路径 B：当前范围调整

- [ ] 用户明确把触发缺口的能力移出当前版本
- [ ] 策划案/GDD 已删除对应玩家行为与临时替代路径
- [ ] GDD 审查保持 Gate PASS
- [ ] 本文记录未来重新启用时必须重新进入框架 Gate
- [ ] 本文 Gate 已改为 `RESOLVED`

## 完成证据

> 按实际解决路径填写，并把顶部 Gate 改为 `RESOLVED`；不适用的另一条路径不得伪造完成证据。

- 发布版本：
- 框架测试：
- 目标项目 pin：
- 集成验证：
- 完成说明：
