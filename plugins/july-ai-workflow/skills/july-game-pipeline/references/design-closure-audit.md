# 设计闭包门禁

完整设计必须同时通过语义审查和 `scripts/design_artifacts.py` 的机械门禁。模型的自我确认、Markdown 勾选框或“看起来完整”不能替代退出码为 0 的验证结果。

机械门禁还要求暂存区绑定当前工作区与未变化的策划案/Unity 版本；正文使用真实 Markdown 标题，各必需章节包含可审查内容，并逐字引用合同中的 MDD、动作签名、跨 MDD 符号和精确文件路径。结构化 JSON 正确但正文空洞或漂移，仍然不能发布。

## 1. 语义门禁

在固定结构化合同前确认：

- 当前版本全部玩家流程和 View 已知；
- 每个业务事实只有一个权威来源；
- 每个原子动作只有一个 owner、signature、失败合同和导航所有者；
- Module 是稳定业务能力，不是页面步骤、技术层或 Editor 工具、验证、生成、发布任务；
- 每个新增类型拥有不可被现有角色替代的责任；
- Luban 只承载作者事实，派生值不重复配置；
- 每份 MDD 的白名单可以完成自身代码、配置、注册、非 Prefab 制作和自动验收；View 的 Prefab 人工交付要求另列且不伪装成已完成；
- 没有持久化设计和目标项目测试代码。

语义门禁失败时继续讨论，不能开始暂存文档生成。

## 2. 机械门禁

验证器必须拒绝：

- 缺少 GDD、索引、Module MDD 或 View MDD；
- 索引声明文件与实际 MDD 文件集合不一致；
- 空文档、必需章节缺失或未解决占位；
- `.july-design-contract.json`、索引内嵌合同和 MDD 内嵌合同不一致；
- 重复 MDD ID、动作 ID 或产品符号 provider；
- Artifact 顺序与 `implementationOrder` 不一致；
- M/V 编号不连续或不符合全局拓扑顺序；
- 依赖不存在、自依赖、前向依赖或无产品符号/动作依据的模糊依赖；
- 消费符号不存在或 provider 声明错误；
- 动作 owner 与 `actionsOwned` 不一致；
- 使用其他 MDD 动作却未依赖 owner；
- MDD 正文没有逐字引用相关动作 ID 与规范 signature；
- Module 标题表现为工具、验证、验收、测试、发布、生成器或编辑器职责；
- 白名单为空、越界、重复，或包含目标 Tests/Editor 工具文件；
- 白名单、产品符号或 dependencyType 声明 Prefab 产物；
- 排除章节以外出现持久化实施合同；
- 暂存区位于目标产品内部；
- 发布前或发布后的完整验证失败。

## 3. 单份 MDD 闭包

按 `implementationOrder` 模拟可用集合：

```text
available = 稳定宿主 + 固定 July/Luban API + 所有更早 MDD 提供的符号 + 当前 MDD 白名单产物

for each 当前 MDD 消费的产品符号:
    require provider 在 dependsOn
    require provider 早于当前 MDD
    require provider 的 provides 含该 symbol

for each 当前 MDD 使用的动作:
    require 全局动作存在
    require owner 是自身或更早依赖
    require 正文逐字使用唯一 signature
```

合同只能证明声明层闭包。设计者还必须核对 C# 草图、Luban schema、注册、非 Prefab 资源和自动验收步骤确实覆盖合同列出的依赖；不能通过少声明依赖骗过验证器。View 正文还必须给出 Prefab 的资源名、预期路径、布局与人工接线要求，并明确它不属于当前合同闭包。

## 4. 发布原子性边界

所有生成发生在系统临时目录。正式产品只由 `publish` 修改。正常的生成中断、验证错误、复制错误或发布后校验错误不会留下半套设计：发布器要么保留旧 `Design/Docs`，要么安装完整新目录，并在可恢复错误上回滚。

操作系统崩溃或断电无法由普通进程提供绝对保证；同卷事务目录会保留恢复依据。若发现 `.july-design-txn-*`，停止自动写入并先确认正式 `Docs` 与事务目录状态，不猜测删除。

## 5. 实施入口门禁

任何单份 MDD 实施前先对正式 `Design/Docs` 执行 `full --surface published` 验证。失败说明完整设计集无效，必须停止且不修改产品文件。不能以“先实施更早 MDD”掩盖缺失索引、前向引用或不完整 View 集合。
