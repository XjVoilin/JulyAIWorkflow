# JulyArch 角色与协作

本文件是插件唯一的 JulyArch 角色语义来源。这里只记录会改变设计决策的正向职责。

生成或实施 MDD 时，必须核对当前项目安装的 JulyFramework 源码、版本、基类和 API。若本参考与实际源码冲突，停止并报告插件需要更新，不自行兼容。

## 1. Store

Store 是运行时领域状态的所有者。

- 继承当前 Framework 的 Store 基类；
- 保存该领域的权威运行时状态；
- 通过有业务语义的方法修改状态并维护不变量；
- 一致修改完成后再发布相应事件或标记 Dirty；
- `GetData()` 可供读取、传输和持久化接入，但外部角色不得直接修改返回对象的字段或集合；
- `ReplaceData()` 用于完整数据替换，不代替普通业务修改。

System 和 Procedure读取 Store Data，但所有运行时状态变化必须调用具体 Store 的语义方法。

## 2. System

System 是由 ArchContext 管理或定位的长期业务能力。

- 提供稳定的业务入口；
- 可以读取 System、Store、View 和事件能力；
- 可以直接完成属于自身职责的业务动作；
- MDD 已设计 Procedure 时，由 System 创建并运行该 Procedure；
- 可以被多份 MDD 按明确实施范围逐步扩展；
- 实施时保持 MDD 已确定的角色。

## 3. Procedure

Procedure 是一次性的有界流程协调对象。

- 每次调用创建新实例；
- 可以等待、取消和嵌套；
- 协调一次由 MDD 明确定义的操作或流程；
- 可以读取 Store/System/View，并通过 Store 语义方法提交状态；
- 由 System 创建和运行；
- Window 和产品 GameView 不直接构造或运行 Procedure；
- 实施时保持 MDD 已确定的角色和调用关系。

推荐业务调用方向：

```text
Window/GameView
  → System 业务入口
    → Procedure（MDD 需要时）
      → System / Store 语义方法
```

## 4. 普通类型

普通 C# 类型承担不需要 JulyArch 生命周期或运行时定位的真实职责，例如：

- 确定性规则和算法；
- 值对象与结果类型；
- 不变量；
- 纯数据转换。

角色选择依据职责。不要为了未来可能需要创建没有当前 MDD 职责的接口、包装和扩展点。

## 5. UIView / Window

Window 是由 UISystem 管理生命周期的页面。

- 负责页面打开、关闭、页面级协调和渲染；
- 使用对应 WindowData 作为唯一显示输入；
- 将玩家业务意图交给 System；
- 管理页面级纯表现状态；
- 不直接从 Store/System 读取并组装显示内容；
- 不直接修改 Store；
- 不直接构造或运行产品 Procedure。

## 6. GameView

GameView 是场景对象或独立 UI 子组件，不限于世界/场景表现。

它可以负责：

- 独立显示区域；
- 重复交互项；
- 拖拽和指针交互；
- 动画区域；
- 临时选中和其他纯表现状态。

复杂 Window 是否拆分 GameView 由真实 UI 职责决定，不使用序列化字段数量、代码行数等机械阈值。UI 子 GameView 的显示输入来自 WindowData 中对应数据，不绕过 Data 直接读取 Store 来渲染。

## 7. WindowData

每个 Window 都有对应 WindowData，用于正常运行和 GM 显示测试。

WindowData：

- 正常构造时通过当前 July 查询能力从 Store/System 取得首屏展示数据；
- 可以根据页面实际复杂度提供一个 `Refresh()` 或多个局部刷新方法；
- 展示字段可由 GM 创建和覆盖；
- 不修改 Store；
- 不执行业务动作；
- 不负责导航；
- 不创建或运行 Procedure。

Window 使用注入的 WindowData；未注入时创建默认 WindowData。Window 始终只根据该 Data 渲染。

业务事件不强制为空，可以携带表示业务事实所需的最小稳定数据；不要把 WindowData 放进业务事件。刷新可以简单全量，也可以按 MDD 的真实需要局部更新。

## 8. Luban

Luban 保存策划配置事实。具体表、Bean、枚举和生成方式以当前项目实际作者源为准。

- 不用运行时 Store 重复保存静态配置事实；
- 不手写与生成类型语义相同的镜像类型；
- 不直接编辑生成产物；
- 运行时变化仍由 Store 拥有。

## 9. 业务状态与表现状态

- Store 只保存真实业务状态；
- 拖拽影子、按钮按压、动画进度、逐项播放位置等属于 Window/GameView；
- 业务结果先完整提交，再由 View 根据 WindowData 播放表现；
- 普通动画结束不反向决定业务结果是否成立；
- 只有 GDD 明确赋予业务意义的确认、交互或等待状态，才能进入 Store/System/Procedure。

## 10. 角色稳定规则

- 角色在 GDD 生成全部 MDD 时确定；
- 实施 MDD 时忠实落地，不擅自删除、合并、替换或绕过角色；
- 发现角色、状态所有权或公开边界不合理时停止，先修改 MDD；
- 当前 MDD 之外的功能不得进入任何角色，即使它已经出现在 GDD 或其他 MDD 中。
