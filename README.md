# 卷摆计时器

一个对线上学习者非常有用的计时器小工具，一个计时器用于记录学习时间，另一个计时器用于记录放松时间，可以起到督促学习的效果。

**一些交互上的优点：**

窗口在不使用时会自动缩小减小屏幕占用；拖拽窗口和其任意组件可以移动窗口；双击按钮可以锁定该计时器的显示；在编辑框中输入数字可以更改记录的时间。

**代码优化：**

相较于旧版做了代码重构和美观优化，手动绘制了按钮和窗口渐变隐藏的动画，创建了非常多的可复用的mixin类可以在以后的程序中使用。

### 效果展示

![](https://github.com/Bonjir/WorkRelaxTimer/blob/main/.github/(1).png)![](https://github.com/Bonjir/WorkRelaxTimer/blob/main/.github/(2).png)![](https://github.com/Bonjir/WorkRelaxTimer/blob/main/.github/(3).png)![](https://github.com/Bonjir/WorkRelaxTimer/blob/main/.github/(4).png)

### TODO

- [x] ~~mini窗口label的显示，哪个启用显示哪个，然后双击锁定~~

- [ ] tooltip

- [ ] 右键列表
- [ ] 自动保存卷摆时间数据

### BUG

- [x] ~~拖拽mini窗口后mini消失_dragging没有解除，需要再次在主窗口点击才能解除~~

- [x] ~~miniwindow的layout更新后位置及大小出错问题~~

- [x] ~~edit控件回车失效问题~~

