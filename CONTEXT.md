# July AI Workflow

本上下文定义插件在渐进研发中的核心语言，避免把产品功能、业务模块、View 和流程接线混为同一种实施任务。

## Language

**功能切片**:
GDD 中一段玩家可观察的完整功能或流程，可以跨越多个业务模块、View 和接线步骤。
_Avoid_: 模块 MDD、单次实现边界

**业务模块**:
围绕共同状态、不变量和生命周期形成的业务所有者，提供可被下游使用的具体能力。
_Avoid_: 功能切片、技术层、Content/Common/Core 总容器

**架构基线 MDD**:
记录模块图、依赖方向、计划 View/流程和阶段门禁的非执行文档。
_Avoid_: 骨架代码、纵向切片实现

**模块 MDD**:
只实现一个业务模块的角色、规则和边界；不生成 View、Prefab、完整玩家流程或测试代码。
_Avoid_: 功能切片 MDD、空角色清单

**UI View MDD**:
使用 WindowData、Events 和 Window 表达一个稳定屏幕职责的 MDD。
_Avoid_: 领域模块、完整玩家流程

**2D View MDD**:
使用 ViewData、Events 和 View 表达场景空间对象、交互和表现的 MDD。
_Avoid_: UIWindow、领域规则

**流程接线 MDD**:
把已确认模块和 View 连接成一个相邻起点到终点，负责意图、调用、Data 映射、刷新和导航。
_Avoid_: 新业务规则、ApplicationSystem、大型流程协调器

**框架能力审计**:
以业务需要、候选能力、匹配程度、决定和证据判断是否复用固定版本 July 能力。
_Avoid_: 看到相似 API 就强行使用、完全忽略已有能力

**待人工审查**:
AI 已完成实现和可用验证，等待用户检查的状态。
_Avoid_: 已确认、自动完成

**已确认**:
用户明确接受当前 MDD 结果的状态。
_Avoid_: AI 根据编译或自己的判断自动写入
