# affliated to 卷摆计时器.py

from PyQt5.QtCore import Qt, QTime, QEasingCurve, \
    QPoint, QSize, QRect, \
    QTimer, QPropertyAnimation, pyqtProperty
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QApplication
from PyQt5.QtGui import QCursor, QColor

from SimpleAnimation import SimpleShrink, ShrinkTo


class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._bg_basic_color = QColor(255, 255, 255)
        self._bg_hover_color = QColor(169, 206, 254)
        self._bg_press_color = QColor(112, 169, 254) # QColor(52, 152, 219)
        self._text_basic_color = QColor(112, 169, 254)
        self._text_hover_color = QColor(112, 169, 254)
        self._text_press_color = QColor(255, 255, 255)
        
        self._bg_color = self._bg_basic_color  # 初始背景色（白）
        self._text_color = self._text_basic_color # 初始文字色（蓝）
        self._update_style()
        
        # 悬停动画
        self._hover_animation = QPropertyAnimation(self, b"blend_color")
        self._hover_animation.setDuration(400)  # 动画时长 400ms
        self._hover_animation.setEasingCurve(QEasingCurve.Type.InOutSine)  # 平滑缓动
        
        self._hover_animation.setStartValue(self._bg_basic_color)
        self._hover_animation.setEndValue(self._bg_hover_color)

        self.enterEvent = lambda e: self._toggle_hover_animation(forward=True)
        self.leaveEvent = lambda e: self._toggle_hover_animation(forward=False)

        # 按下动画
        self._press_animation = QPropertyAnimation(self, b"blend_color")
        self._press_animation.setDuration(200)  # 动画时长 400ms
        self._press_animation.setEasingCurve(QEasingCurve.Type.InOutSine)  # 平滑缓动
        
        self._press_animation.setStartValue(self._bg_hover_color)
        self._press_animation.setEndValue(self._bg_press_color)

        self._mouse_pressed = False

    # 定义动态属性（供动画驱动）
    @pyqtProperty(QColor)
    def blend_color(self):
        return self._bg_color  # 仅需一个属性驱动双色变化

    @blend_color.setter
    def blend_color(self, color):
        # 背景色直接使用动画插值
        self._bg_color = color
        
        def _similar_transform(x1, x2, y1, y2, x):
            return int((x - x1) / (x2 - x1 + 1e-6) * (y2 - y1) + y1)
        
        if self._mouse_pressed:
            red = _similar_transform(self._bg_hover_color.red(), self._bg_press_color.red(), self._text_hover_color.red(), self._text_press_color.red(), color.red())
            green = _similar_transform(self._bg_hover_color.green(), self._bg_press_color.green(), self._text_hover_color.green(), self._text_press_color.green(), color.green())
            blue = _similar_transform(self._bg_hover_color.blue(), self._bg_press_color.blue(), self._text_hover_color.blue(), self._text_press_color.blue(), color.blue())
        else:    
            red = _similar_transform(self._bg_basic_color.red(), self._bg_hover_color.red(), self._text_basic_color.red(), self._text_hover_color.red(), color.red())
            green = _similar_transform(self._bg_basic_color.green(), self._bg_hover_color.green(), self._text_basic_color.green(), self._text_hover_color.green(), color.green())
            blue = _similar_transform(self._bg_basic_color.blue(), self._bg_hover_color.blue(), self._text_basic_color.blue(), self._text_hover_color.blue(), color.blue())
        
        # 文字色根据背景亮度反向计算（白色或蓝色）
        self._text_color = QColor(red, green, blue)
        # self._text_color = QColor(255, 255, 255) if color.lightness() < 200 else QColor(52, 152, 219)
        
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(f"""
            AnimatedButton {{
                background-color: {self._bg_color.name()};
                color: {self._text_color.name()};
                border: 2px solid #3498db;
                padding: 10px;
                border-radius: 5px;
            }}
        """)
        
    def _toggle_hover_animation(self, forward):
        self._hover_animation.setDirection(QPropertyAnimation.Forward if forward else QPropertyAnimation.Backward)
        self._hover_animation.start()

    def _toggle_press_animation(self, forward):
        self._press_animation.setDirection(QPropertyAnimation.Forward if forward else QPropertyAnimation.Backward)
        self._press_animation.start()
    
    def mousePressEvent(self, e):
        self._mouse_pressed = True
        self._toggle_press_animation(forward=True)
        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._mouse_pressed = False
        self._toggle_press_animation(forward=False)
        return super().mouseReleaseEvent(e)
    
    def set_bg_color(self, basic, hover, press):
        self._bg_basic_color = basic
        self._bg_hover_color = hover
        self._bg_press_color = press
        
        self._hover_animation.setStartValue(self._bg_basic_color)
        self._hover_animation.setEndValue(self._bg_hover_color)
        self._press_animation.setStartValue(self._bg_hover_color)
        self._press_animation.setEndValue(self._bg_press_color)

    def set_text_color(self, basic, hover, press):
        self._text_basic_color = basic
        self._text_hover_color = hover
        self._text_press_color = press

class MouseEventPenetrateMixin:
    
    def mousePressEvent(self, e):
        self.parent().mousePressEvent(e) # 把事件转发给主窗口
        return super().mousePressEvent(e)
    
    def mouseMoveEvent(self, e):
        self.parent().mouseMoveEvent(e)
        return super().mouseMoveEvent(e)
    
    def mouseReleaseEvent(self, e):
        self.parent().mouseReleaseEvent(e) # 把事件转发给主窗口
        return super().mouseReleaseEvent(e)

class PenetrateAnimatedButton(MouseEventPenetrateMixin, AnimatedButton):
    def __init__(self, text: str = '', parent: QWidget = None):
        AnimatedButton.__init__(self, text, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

class PenetrateWidget(MouseEventPenetrateMixin, QWidget):
    def __init__(self, parent: QWidget = None):
        QWidget.__init__(self, parent)

class PenetrateButton(MouseEventPenetrateMixin, QPushButton):
    def __init__(self, text: str = '', parent: QWidget = None):
        QPushButton.__init__(self, text, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

class PenetrateLineEdit(MouseEventPenetrateMixin, QLineEdit):
    def __init__(self, parent = None):
        QLineEdit.__init__(self, parent)
        
    def keyPressEvent(self, event):
        # if event.key() == Qt.Key.Key_Tab:
        #     print('tab pressed')
            
        if event.key() == Qt.Key.Key_Return:
            self.on_return_pressed(event)
            event.accept()
            return # 已经处理，不再转发
        
        if event.key() == Qt.Key.Key_Escape:
            self.parent().setFocus()
            event.accept()
            return
        
        return super().keyPressEvent(event)
    
    def on_return_pressed(self, event):
        """将焦点转移到下一个lineEdit控件，如果没有则触发父窗口editingFinishedEvent事件"""
        # 获取当前控件的父级
        parent = self.parent()
        
        # 获取父级布局
        layout = parent.layout() if parent else None
        if not layout:
            return
        # 获取控件在布局中的索引
        index = layout.indexOf(self)
        
        if index == -1:
            return
        # 如果有下一个控件，则将焦点转移过去
        if index + 1 < layout.count():
            next_widget = layout.itemAt(index + 1).widget()
            if isinstance(next_widget, QLineEdit):
                next_widget.setFocus()
            else:
                parent.editingFinishedEvent(event)
                parent.setFocus()

class DraggableMixin:
    def __init__(self, clipped = False):
        super().__init__()

        # 最小拖拽的距离
        self.DRAG_OFFSET_MINIMUM = 5
        
        # 存储鼠标按下的初始位置
        self.dragging = False
        self.drag_offset = QPoint()
        
        # 限制在屏幕内拖动
        self.clipped = clipped

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录鼠标按下时的窗口位置
            self.dragging = True
            self.drag_offset = event.globalPos() - self.pos()
            self.first_drag_pos = event.globalPos()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            # 限制拖拽的最小距离
            drag_offset = event.globalPos() - self.first_drag_pos
            if abs(drag_offset.x()) <= self.DRAG_OFFSET_MINIMUM and abs(drag_offset.y()) <= self.DRAG_OFFSET_MINIMUM:
                return
            self.first_drag_pos = QPoint(-100, -100)
            
            # 合理的屏幕范围
            self.screen_geometry = QApplication.primaryScreen().availableGeometry()
            # 计算新的窗口位置
            new_pos = event.globalPos() - self.drag_offset
            if self.clipped == True:
                # 限制窗口位置在屏幕范围内
                new_x = max(self.screen_geometry.left(), min(new_pos.x(), self.screen_geometry.right() - self.width()))
                new_y = max(self.screen_geometry.top(), min(new_pos.y(), self.screen_geometry.bottom() - self.height()))
            else:
                new_x, new_y = new_pos.x(), new_pos.y()
            self.move(new_x, new_y)  # 更新窗口位置
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        else:
            super().mouseMoveEvent(event)
            
# 只作为基类
# class DraggableMainWindow(DraggableMixin, QMainWindow):
#     def __init__(self, clipped = False):
#         DraggableMixin.__init__(self, clipped)
        
# class DraggableDialog(DraggableMixin, QDialog):
#     def __init__(self, clipped = False):
#         DraggableMixin.__init__(self, clipped)

# class DraggableWidget(DraggableMixin, QWidget):
#     def __init__(self, clipped = False):
#         DraggableMixin.__init__(self, clipped)

class ShrinkWindow(DraggableMixin, QWidget):
    def __init__(self):
        super().__init__()

        # 可缩小窗口的初始化
        # 初始化状态变量
        self.is_shrunk = False
        self.last_move_time = QTime.currentTime()

        # 设置定时器检查空闲状态
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.check_idle)
        self.idle_timer.start(1000)  # 每秒检查一次空闲状态

        # 设置鼠标移动事件监听
        self.setMouseTracking(True)

        # 创建SimpleShrink对象
        self.animation = SimpleShrink(self)
        # 创建 QPropertyAnimation 对象
        # self.shrink_animation = QPropertyAnimation(self, b"geometry")
        # self.restore_animation = QPropertyAnimation(self, b"geometry")
        
    def set_mini_size(self, size: QSize):
        '''重新设置迷你窗口大小'''
        # min_hint = self.minimumSizeHint()
        # if size.width() < min_hint.width() or size.height() < min_hint.height():
            # print(f'mini窗口尺寸可能较小，期望尺寸：{(min_hint.width(), min_hint.height())}')
        minimum = self.minimumSize()
        mw = minimum.width()
        mh = minimum.height()
        w = max(size.width(), mw)
        h = max(size.height(), mh)
        self.mini_size = QSize(w, h)
        self.animation.set_mini_size(self.mini_size) # 动画的大小也要设置
        return size.width() >= mw and size.height() >= mh
    
    def set_main_size(self, size: QSize):
        minimum = self.minimumSize()
        mw = minimum.width()
        mh = minimum.height()
        w = max(size.width(), mw)
        h = max(size.height(), mh)
        self.main_size = QSize(w, h)
        self.animation.set_normal_size(self.main_size) # 动画的大小也要设置
        return size.width() >= mw and size.height() >= mh
    
    def noshrink_heartbeat(self):
        self.last_move_time = QTime.currentTime()
    
    def mousePressEvent(self, event):
        # self.shrink_animation.stop()
        # self.restore_animation.stop()
        self.animation.stop_animation()
        return super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """鼠标进入窗口事件"""
        self.noshrink_heartbeat()
        if self.is_shrunk:
            self.restore_window()
        super().enterEvent(event)
        
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""

        self.noshrink_heartbeat()
        if self.is_shrunk:
            self.restore_window()

        super().mouseMoveEvent(event=event)

    def check_idle(self):
        """检查是否有空闲时间，如果空闲则缩小窗口"""
        idle_threshold = 3  # 空闲超时 3秒
        if self.last_move_time.msecsTo(QTime.currentTime()) > idle_threshold * 1000 and \
            not self.is_shrunk and\
            not self.geometry().contains(QCursor.pos()):
            self.shrink_window()

    def shrink_window(self):
        """隐藏主窗口，显示迷你窗口"""
        if self.is_shrunk:
            return
        
        # 合理的屏幕范围
        self.screen_geometry = QApplication.primaryScreen().availableGeometry()
        
        # ...放弃自校正
        # if not self.set_mini_size(self.mini_size): # 校正mini窗口尺寸
        #     print(f'mini窗口设置过小, 请尝试调整layout边距或mini窗口尺寸, 最小尺寸为：{(self.minimumSize().width(), self.minimumSize().height())}')
            
        x = self.x()
        y = self.y()
        
        if x <= self.screen_geometry.left() and y <= self.screen_geometry.top():
            self.animation.set_shrink_to(ShrinkTo.top_left)
        elif x >= self.screen_geometry.right() - self.width() and y <= self.screen_geometry.top():
            self.animation.set_shrink_to(ShrinkTo.top_right)
        elif y <= self.screen_geometry.top():
            self.animation.set_shrink_to(ShrinkTo.top_center)
        
        elif x <= self.screen_geometry.left() and y >= self.screen_geometry.bottom() - self.height():
            self.animation.set_shrink_to(ShrinkTo.bottom_left)
        elif x >= self.screen_geometry.right() - self.width() and y >= self.screen_geometry.bottom() - self.height():
            self.animation.set_shrink_to(ShrinkTo.bottom_right)
        elif y >= self.screen_geometry.bottom() - self.height():
            self.animation.set_shrink_to(ShrinkTo.bottom_center)
        
        elif x <= self.screen_geometry.left():
            self.animation.set_shrink_to(ShrinkTo.vcenter_left)
        elif x >= self.screen_geometry.right() - self.width():
            self.animation.set_shrink_to(ShrinkTo.vcenter_right)
        else:
            self.animation.set_shrink_to(ShrinkTo.center)
        
        self.animation.start_shrink_animation(1000)
        
        # 下面是不用simpleshrink实现的部分
        # PERMISSIBLE_DISTANCE = 10
        # if x <= self.screen_geometry.left() + PERMISSIBLE_DISTANCE:
        #     mini_x = self.screen_geometry.left()
        # elif x >= self.screen_geometry.right() - self.width() - PERMISSIBLE_DISTANCE:
        #     mini_x = self.screen_geometry.right() - self.mini_size.width()
        # else:
        #     mini_x = int(x + (self.width() - self.mini_size.width()) / 2)
        
        # if y <= self.screen_geometry.top() + PERMISSIBLE_DISTANCE:
        #     mini_y = self.screen_geometry.top()
        # elif y >= self.screen_geometry.bottom() - self.height() - PERMISSIBLE_DISTANCE:
        #     mini_y = self.screen_geometry.bottom() - self.mini_size.height()
        # else:
        #     mini_y = int(y + (self.height() - self.mini_size.height()) / 2)
        
        # # 设置动画的起始值和结束值
        # start_rect = self.geometry()
        # end_rect = QRect(mini_x, mini_y, self.mini_size.width(), self.mini_size.height())
        # self.shrink_animation.setStartValue(start_rect)
        # self.shrink_animation.setEndValue(end_rect)
        # self.shrink_animation.setDuration(1000) # 设置动画持续时间
        # self.shrink_animation.setEasingCurve(QEasingCurve.OutBounce) # 出弹跳动画
        # self.shrink_animation.start()
        
        # self.preshrunk_geometry = QRect(x, y, self.main_size.width(), self.main_size.height())
        self.is_shrunk = True

    def restore_window(self):
        """恢复主窗口"""
        if not self.is_shrunk:
            return
        # ...放弃自校正
        # if not self.set_main_size(self.main_size): # 校正主窗口尺寸
        #     print(f'主窗口设置过小, 请尝试调整layout边距或主窗口尺寸, 最小尺寸为：{(self.minimumSize().width(), self.minimumSize().height())}')
        
        self.animation.start_restore_animation(1000)
        
        # 下面是不使用simpleanimation的实现
        # # 设置动画的起始值和结束值
        # start_rect = self.geometry()
        # end_rect = QRect(self.preshrunk_geometry)
        # self.restore_animation.setStartValue(start_rect)
        # self.restore_animation.setEndValue(end_rect)
        # self.restore_animation.setDuration(1000) # 设置动画持续时间
        # self.restore_animation.setEasingCurve(QEasingCurve.OutElastic) # 出弹性动画
        # self.restore_animation.start()
        
        self.is_shrunk = False

    def closeEvent(self, event):
        # 在关闭前显示提示框
        # print("Window is about to be closed.")
        QApplication.quit()  # 强制退出应用程序

    def destroyEvent(self, event):
        print("Window is being destroyed.")
        # 执行一些清理操作，比如释放资源或保存状态
        event.accept()
