# July UI 组件选择指南

仅在当前 MDD 涉及 View 代码时读取。本文件只记录常用组件的选择原则；具体成员、生命周期和安装版本始终以当前项目的 `com.july.ui` 源码为准。

插件只创建或修改 C# 代码，可以声明组件序列化字段，但不创建或修改 Prefab、Scene、Inspector 绑定和美术资源。

## 1. 按钮与选择

- `UISmartButton`：项目普通按钮的默认选择，复用点击、按压反馈、冷却和声音能力；不要默认改用 Unity `Button` 重新实现同类行为。
- `UISmartButtonGray`：按钮不可交互时需要同步置灰的选择；按当前源码要求配合 `UIGrayGroup`。
- `UIGrayGroup`：需要对子节点 Graphic/TMP 整体切换灰度时使用。
- `UICloseButton`：标准关闭父级 UIView 时优先评估，避免每个 Window 重复维护关闭监听。
- `UIToggleButton`：单个开关或选中按钮。
- `UIToggleGroup`、`UIToggleItem`：互斥选择、锁定项和已有选择流程能力。

## 2. 通用展示

- `UIProgressBar`：普通进度显示。
- `UIArtNumber`：通过数字 Sprite 显示整数。
- `UIItemSlot`：图标、数量、空状态、选中状态和点击的通用物品格；业务规则仍由上层角色负责。
- `UIPageNavigator`、`UIPageDot`：分页、页码状态和页面过渡。
- `WebImage`：当前项目确实需要网络图片时使用。

## 3. 输入与表现辅助

- `UIInputBlocker`：面板激活期间需要屏蔽游戏输入时使用。
- `UIEmptyGraphic`：需要参与 UI 射线检测但不需要绘制时使用。
- `UIBtnEffectGroup` 及 Scale/Move/Rotate 效果：需要复用按钮子元素反馈时评估。
- `TMPLinkClickable`：TMP 文本链接点击。
- `AutoHideScrollbar`、`FixedHandleScrollRect`：滚动区域存在对应需要时使用。
- `WorldAnchoredUI`：世界对象对应 UI 定位。
- `UIModelPreview`：UI 中模型预览。
- `PageTransition` 系列：分页 Fade、Slide、Scale 过渡。

## 4. 选择规则

1. 先确认当前项目已安装组件及其真实 API；
2. 已有组件能够承担当前 MDD 职责时直接复用；
3. 不在 Window 中重复实现按钮冷却、置灰、分页、进度裁剪等已有能力；
4. 不因为组件存在就强行使用；只有当前 View 责任真实需要时才声明；
5. 不为尚未实施的 MDD 提前添加组件字段；
6. 不通过运行时查找、自动挂载或空值兜底弥补 Prefab/Inspector 尚未制作；
7. MDD 和代码可以写出需要的组件类型与职责，但本插件不交付其 Prefab 绑定。

## 5. 复杂页面

Window 负责页面级生命周期、导航和子区域协调。独立显示、重复交互、拖拽或动画区域可以拆成 GameView。

拆分依据是职责和交互生命周期，不是字段数量。WindowData 可以包含子 ViewData，Window 把对应数据交给 GameView；子 GameView 不直接读取 Store 来决定显示。
