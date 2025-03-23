# affliated to 卷摆计时器.py

from PyQt5.QtCore import Qt, QTime, QEasingCurve, \
    QPoint, QSize, QRect, \
    QTimer, QPropertyAnimation, pyqtProperty, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QApplication, QMenu, QAction
from PyQt5.QtGui import QCursor, QColor, QPainterPath, QPainter, QPen
import typing

from ui.palette import Palette, get_theme_colors
from utils import Logger

_logger = Logger(__name__) # 不要删它

class SeparateDoubleClickMixin:
    singleClicked = pyqtSignal()
    doubleClicked = pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # 传递所有参数
        self.__click_state = 0
        self.__click_timer = QTimer()
        self.__click_timer.setSingleShot(True)  # 单次触发定时器
        self.__click_timer.timeout.connect(self._handle_click)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.__click_state == 0:
                self.__click_state = 1
                # 检查父窗口是否在拖拽
                if hasattr(self.ancestor(), 'dragging') and self.ancestor().dragging():
                    self.__click_state = 0  # 重置状态
                    event.accept()
                    return super().mouseReleaseEvent(event)
                
                # 如果不在拖拽且定时器未激活，则启动定时器准备触发单击
                if not self.__click_timer.isActive():
                    self.__click_timer.start(200)  # 设置双击检测间隔为200毫秒
                    self.__click_event = event
        return super().mouseReleaseEvent(event)

    def _handle_click(self):
        if self.__click_state == 1:
            self.mouseSingleClickEvent(self.__click_event)
        # elif self.__click_count >= 2:
        #     self.mouseDoubleClickEvent(self.__click_event)
        self.__click_state = 0  # 重置计数器

    def mouseSingleClickEvent(self, event):
        self.singleClicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.__click_state = 2
        self.__click_event = event
        self.doubleClicked.emit()
        return super().mouseDoubleClickEvent(event)

class AnimatedButtonMixin:
    # doubleClicked = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 跳过所有参数
        self._bg_basic_color = Palette.white
        self._bg_hover_color = Palette.blue_light
        self._bg_press_color = Palette.blue
        self._bg_toggled_color = Palette.blue_light
        self._text_basic_color = Palette.blue
        self._text_hover_color = Palette.blue_dark
        self._text_press_color = Palette.white
        self._text_toggled_color = Palette.blue_dark
        
        self._bg_color = self._bg_basic_color  # 初始背景色（白）
        self._text_color = self._text_basic_color # 初始文字色（蓝）
        self._theme_color = Palette.blue
        self._update_style()
        
        # 悬停动画
        self._hover_animation = QPropertyAnimation(self, b"blend_color")
        self._hover_animation.setDuration(400)  # 动画时长 400ms
        self._hover_animation.setEasingCurve(QEasingCurve.Type.InOutSine)  # 平滑缓动
        
        self._hover_animation.setStartValue(self._bg_basic_color)
        self._hover_animation.setEndValue(self._bg_hover_color)

        self.enterEvent = lambda e: self._start_hover_animation(True)
        self.leaveEvent = lambda e: self._start_hover_animation(False)

        # 按下动画
        self._press_animation = QPropertyAnimation(self, b"blend_color")
        self._press_animation.setDuration(200)  # 动画时长 400ms
        self._press_animation.setEasingCurve(QEasingCurve.Type.InOutSine)  # 平滑缓动
        
        self._press_animation.setStartValue(self._bg_hover_color)
        self._press_animation.setEndValue(self._bg_press_color)

        self._mouse_pressed = False
        self._toggled = False  # For Toggle Button

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
            {self.__class__.__name__} {{
                background-color: {self._bg_color.name()};
                color: {self._text_color.name()};
                border: 2px solid {self._bg_press_color.name()};
                font-size: 9pt;
                padding: 10px;
                border-radius: 10px;
            }}
        """)
        
    def refresh_style(self):
        self._update_style()
        
        # 获取默认字体大小
        # default_font = self.font()
        # default_size = default_font.pointSize()  # 单位：pt
        # default_size_px = default_font.pixelSize()  # 单位：px（可能为 -1，取决于系统）
        # print(f"默认字体大小：{default_size}pt 或约 {default_size_px}px")

    def _start_hover_animation(self, forward):
        self._hover_animation.setDirection(QPropertyAnimation.Forward if forward else QPropertyAnimation.Backward)
        self._hover_animation.start()

    def _start_press_animation(self, forward):
        self._press_animation.setDirection(QPropertyAnimation.Forward if forward else QPropertyAnimation.Backward)
        self._press_animation.start()
    
    def twinkle(self):
        # 闪烁动画
        self._start_hover_animation(True)
        QTimer.singleShot(self._hover_animation.duration() + 100, lambda: self._start_hover_animation(False))
    
    def mousePressEvent(self, e):
        self._mouse_pressed = True
        self._start_press_animation(forward=True)
        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._mouse_pressed = False
        self._start_press_animation(forward=False)
        return super().mouseReleaseEvent(e)
    
    # def mouseDoubleClickEvent(self, e):
    #     self.doubleClicked.emit()
    
    def get_theme_color(self):
        return self._theme_color
    
    def set_theme_color(self, color):
        self._theme_color = color
        normal, light, dark = get_theme_colors(color)
        self.set_bg_color(Palette.white, light, normal, light)
        self.set_text_color(normal, dark, Palette.white, dark)
        # self._update_style()
        
    def set_bg_color(self, basic, hover, press, toggled = None):
        self._bg_basic_color = basic
        self._bg_hover_color = hover
        self._bg_press_color = press
        self._bg_toggled_color = toggled if toggled else hover
        self._bg_color = self._bg_basic_color
        self._update_style()
        
        self._hover_animation.setStartValue(self._bg_basic_color)
        self._hover_animation.setEndValue(self._bg_hover_color)
        self._press_animation.setStartValue(self._bg_hover_color)
        self._press_animation.setEndValue(self._bg_press_color)

    def set_text_color(self, basic, hover, press, toggled = None):
        self._text_basic_color = basic
        self._text_hover_color = hover
        self._text_press_color = press
        self._text_color = self._text_basic_color
        self._text_toggled_color = toggled if toggled else hover
        self._update_style()

    def set_toggled(self, toggled):
        self._toggled = toggled
        if toggled:
            self._hover_animation.setStartValue(self._bg_toggled_color)
        else:
            self._hover_animation.setStartValue(self._bg_basic_color)
    
    def toggle(self):
        # 切换Toggle按钮状态
        self.set_toggled(not self._toggled)
    
    def toggled(self):
        return self._toggled
    
class AnimatedPushButton(AnimatedButtonMixin, SeparateDoubleClickMixin, QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # 向上传递所有参数

class MouseEventPenetrateMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # 跳过所有参数
        pass
    
    def mousePressEvent(self, e):
        ret = super().mousePressEvent(e) # 否则正常处理
        self.ancestor().mousePressEvent(e) # 先把事件转发给主窗口
        return ret
    
    def mouseMoveEvent(self, e):
        self.ancestor().mouseMoveEvent(e)
        return super().mouseMoveEvent(e)
    
    def mouseReleaseEvent(self, e):
        ret = super().mouseReleaseEvent(e)
        self.ancestor().mouseReleaseEvent(e)
        return ret
    
    """用于获取最外层窗口的Mixin"""
    def get_ancestor_window(self):
        """递归查找最外层窗口"""
        parent = super().parent()
        if parent is None:
            return None
        
        # 向上遍历直到找到最外层窗口
        while parent.parent() is not None:
            parent = parent.parent()
        return parent

    def ancestor(self):
        """重写parent方法, 直接返回最外层窗口"""
        top_parent = self.get_ancestor_window()
        return top_parent if top_parent is not None else super().parent()

class PenetrateAnimatedButton(MouseEventPenetrateMixin, AnimatedPushButton):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None: ...
    @typing.overload
    def __init__(self, text: typing.Optional[str], parent: typing.Optional[QWidget] = ...) -> None: ...
    
    def __init__(self, *args, **kwargs):
        # 动态处理参数类型
        text = ""
        parent = None
        
        # 参数解析逻辑
        if args:
            if isinstance(args[0], str):
                text = args[0]
                if len(args) > 1 and isinstance(args[1], QWidget):
                    parent = args[1]
            elif isinstance(args[0], QWidget):
                parent = args[0]
        
        # 处理关键字参数
        text = kwargs.get('text', text)
        parent = kwargs.get('parent', parent)

        # 调用QPushButton的构造函数
        super().__init__(text, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

class PenetrateWidget(MouseEventPenetrateMixin, QWidget):
    def __init__(self, parent: QWidget = None):
        QWidget.__init__(self, parent)

class PenetrateButton(MouseEventPenetrateMixin, QPushButton):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None: ...
    @typing.overload
    def __init__(self, text: typing.Optional[str], parent: typing.Optional[QWidget] = ...) -> None: ...
    
    def __init__(self, *args, **kwargs):
        # 动态处理参数类型
        text = ""
        parent = None
        
        # 参数解析逻辑
        if args:
            if isinstance(args[0], str):
                text = args[0]
                if len(args) > 1 and isinstance(args[1], QWidget):
                    parent = args[1]
            elif isinstance(args[0], QWidget):
                parent = args[0]
        
        # 处理关键字参数
        text = kwargs.get('text', text)
        parent = kwargs.get('parent', parent)
        
        # 调用QPushButton的构造函数
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
        
        # 不转移焦点了
        # # 如果有下一个控件，则将焦点转移过去
        # while index + 1 < layout.count():
        #     index += 1
        #     next_widget = layout.itemAt(index).widget()
        #     # print(next_widget)
        #     if isinstance(next_widget, QLineEdit):
        #         next_widget.setFocus()
        #         return
            
        # 没有下一个Edit
        while parent != None:
            try:
                parent.editingFinishedEvent(event)
                parent.setFocus()
                break # 向上找到一个可以接受editingFinishedEvent的parent
            except:
                parent = parent.parent()
                        

class DraggableMixin:
    def __init__(self, clipped = False):

        # 最小拖拽的距离
        self.DRAG_OFFSET_MINIMUM = 5
        
        # 存储鼠标按下的初始位置
        self.__pressing = False
        self.__dragging = False
        self._drag_offset = QPoint()
        
        # 限制在屏幕内拖动
        self._clipped = clipped
        
        # # 阴影部分的偏移
        # self._shadow_offset = 0
        # self._shadow_offset_switch = shadow_offset_switch
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录鼠标按下时的窗口位置
            self.__pressing = True
            self.__dragging = False
            self._drag_offset = event.globalPos() - self.pos()
            self._first_drag_pos = event.globalPos()
            
            # 获取阴影部分的偏移
            # if self._shadow_offset
            # shadow_geo = self.frameGeometry()
            # geo = self.geometry()
            # self._shadow_offset = QSize(geo.x() - shadow_geo.x(), geo.y() - shadow_geo.y())

        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.__pressing:
            # 限制拖拽的最小距离
            # 第一次拖动之后就不再限制
            _drag_offset = event.globalPos() - self._first_drag_pos
            if not self.__dragging and \
                abs(_drag_offset.x()) <= self.DRAG_OFFSET_MINIMUM and abs(_drag_offset.y()) <= self.DRAG_OFFSET_MINIMUM:
                return
            self.__dragging = True # 拖动开始
            # self._first_drag_pos = QPoint(-100, -100) # 第一次拖动之后就不再限制
            
            # 合理的屏幕范围
            self._screen_geometry = QApplication.primaryScreen().availableGeometry()
            # 计算新的窗口位置
            new_pos = event.globalPos() - self._drag_offset
            if self._clipped == True:
                # 限制窗口位置在屏幕范围内
                new_x = max(self._screen_geometry.left(),\
                    min(new_pos.x(), \
                    self._screen_geometry.right() - self.geometry().width()))
                new_y = max(self._screen_geometry.top(),\
                    min(new_pos.y(), \
                    self._screen_geometry.bottom() - self.geometry().height()))
            else:
                new_x, new_y = new_pos.x(), new_pos.y()
            self.move(new_x, new_y)  # 更新窗口位置
        return super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__pressing = False
            self.__dragging = False
        # print(self.x(), self.y(), self.width(), self.geometry())
        return super().mouseReleaseEvent(event)
    
    def dragging(self):
        return self.__dragging
    
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

class FadeoutMixin:
    signal_fading = pyqtSignal(bool)
    signal_fading_finished = pyqtSignal(bool)
    
    def __init__(self, fade_when_idle = True):

        # 可缩小窗口的初始化
        # 初始化状态变量
        self._is_faded = False
        self._last_move_time = QTime.currentTime()
        self._fade_when_idle = fade_when_idle
        self._idle_span = 2000 # 空闲超时 2 秒
        
        if self._fade_when_idle:
            # 设置定时器检查空闲状态
            self.idle_timer = QTimer(self)
            self.idle_timer.timeout.connect(self._check_idle)
            self.idle_timer.start(1000)  # 每秒检查一次空闲状态

            # 设置鼠标移动事件监听
            self.setMouseTracking(True)
            self._pressing = False

        # 创建对象
        self.fadeout_animation = QPropertyAnimation(self, b'windowOpacity')
        self.fadeout_animation.setDuration(500)
        self.fadeout_animation.setStartValue(1.0)
        self.fadeout_animation.setEndValue(0.1)
        self.fadeout_animation.setEasingCurve(QEasingCurve.InOutQuad)
        # 信号与槽
        self.signal_fading.connect(self.on_fadingout)
        self.signal_fading_finished.connect(self.on_fade_finished)
        
        self._key_rect_list = []
    
    def set_init_opacity(self, opacity):
        self.fadeout_animation.setStartValue(opacity)
    
    def set_opacity_startend(self, opacity_start, opacity_end):
        self.fadeout_animation.setStartValue(opacity_start)
        self.fadeout_animation.setEndValue(opacity_end)
        
    def mousePressEvent(self, event):
        # print('pressed')
        if not self._fade_when_idle:
            return super().mousePressEvent(event)
        
        # self.fadeout_animation.pause()
        if event.button() == Qt.LeftButton:
            self._pressing = True
        return super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """鼠标进入窗口事件"""
        if not self._fade_when_idle:
            super().enterEvent(event)
            return 
        
        self._last_move_time = QTime.currentTime()
        if self._is_faded:
            self._start_fadeout_animation(False)
            self._is_faded = False
        super().enterEvent(event)
        
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if not self._fade_when_idle:
            return super().mouseMoveEvent(event)
        
        self._last_move_time = QTime.currentTime()
        if self._is_faded:
            self._start_fadeout_animation(False)
            self._is_faded = False
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self._fade_when_idle:
            return super().mouseReleaseEvent(event)
        
        if event.button() == Qt.LeftButton:
            self._pressing = False
        return super().mouseReleaseEvent(event)
    
    def add_key_fadeout_rect(self, rect: QRect):
        """添加关键矩形, 用于判断鼠标是否在窗口内"""
        self._key_rect_list.append(rect)
    
    def remove_key_fadeout_rect(self, rect: QRect):
        if rect in self._key_rect_list:
            self._key_rect_list.remove(rect)
    
    def _check_idle(self):
        """检查是否有空闲时间，如果空闲则缩小窗口"""
        if self._is_faded:
            return
        
        if self.geometry().contains(QCursor.pos()) or self._pressing:
            self._last_move_time = QTime.currentTime()
            return
        
        # 检查鼠标是否在关键矩形中
        for rect in self._key_rect_list:
            if rect.contains(QCursor.pos()):
                self._last_move_time = QTime.currentTime()
                return
        
        if self._last_move_time.msecsTo(QTime.currentTime()) > self._idle_span and \
          not self._is_faded:
            self._start_fadeout_animation(True)
            self._is_faded = True
            
    def _start_fadeout_animation(self, fading):
        # self.fadeout_animation.setDuration(1000 if forward else 500)
        self.fadeout_animation.setDirection(QPropertyAnimation.Forward if fading else QPropertyAnimation.Backward)
        self.fadeout_animation.start()
        self.signal_fading.emit(fading)
        self.fadeout_animation.finished.connect(self._on_fadeout_animation_finished)
    
    def _on_fadeout_animation_finished(self):
        self.signal_fading_finished.emit(self._is_faded)
    
    def on_fadingout(self, fading: bool):
        ...
    
    def on_fade_finished(self, faded: bool):
        ...
    
    def is_faded(self):
        return self._is_faded
    
    def try_fadeout_animation(self, fading: bool):
        if fading and self._is_faded:
            return
        if not fading and not self._is_faded:
            return
        
        self._start_fadeout_animation(fading)
        self._is_faded = fading
        if self._fade_when_idle:
            self._last_move_time = QTime.currentTime()

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QHBoxLayout, QGraphicsDropShadowEffect, QMenu)
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QColor, QPainterPath, QPainter, QPen

class FrameWidget(PenetrateWidget):
    def __init__(self, exframe_show, *args):
        super().__init__(*args)
        self._exframe_show = exframe_show
    
    def paintEvent(self, event):
        if not self._exframe_show:
            return
        # 绘制自定义边框
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect().adjusted(1, 1, -1, -1)), 15, 15) # 留出阴影空间
        
        # 绘制背景边框
        painter.setPen(QPen(QColor("#E0E0E0"), 2))
        painter.drawPath(path)
        
class StylishFramelessWindow(DraggableMixin, QWidget):
    def __init__(self, clipped, outside_margin, inside_margin, parent = None, exframe_show = True):
        QWidget.__init__(self, parent)
        DraggableMixin.__init__(self, clipped=clipped)
        self._outside_margin = outside_margin
        self._inside_margin = inside_margin
        self._shadow_radius = 25
        self._exframe_show = exframe_show
        self.setupWindow()
        self.setupUI_StylishFrame()
        self.setupStyle()

    def setupWindow(self):
        # 设置窗口标志
        self.setWindowFlags(
            Qt.FramelessWindowHint |          # 无边框
            Qt.WindowStaysOnTopHint |         # 始终置顶
            Qt.Tool |                         # 工具窗口
            Qt.MSWindowsFixedSizeDialogHint   # 固定大小
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        # self.setMinimumSize(400, 300)

    def setupUI_StylishFrame(self):
        # 边框层
        frame_layout = QVBoxLayout(self)
        frame_layout.setContentsMargins(*([self._shadow_radius] * 4))
        
        self._frame_widget = FrameWidget(self._exframe_show, self)
        self._frame_widget.setObjectName("frameWidget")
        
        # 主布局（保留边距用于显示阴影）
        main_layout = QVBoxLayout(self._frame_widget)
        main_layout.setContentsMargins(*([self._inside_margin] * 4))
        
        # 内容容器（实际显示区域）
        self._content_widget = PenetrateWidget()
        self._content_widget.setObjectName("contentWidget")
        # self._content_layout = QVBoxLayout(self._content_widget)
        
        # # 标题栏
        # title_bar = QWidget()
        # title_bar.setFixedHeight(40)
        # title_bar.setObjectName("titleBar")
        # title_layout = QHBoxLayout(title_bar)
        # title_layout.setContentsMargins(10, 0, 10, 0)
        
        # self.title_label = QLabel("自定义窗口")
        # close_btn = QPushButton("×")
        # close_btn.setFixedSize(30, 30)
        # close_btn.clicked.connect(self.close)
        
        # title_layout.addWidget(self.title_label)
        # title_layout.addStretch()
        # title_layout.addWidget(close_btn)
        
        # 内容区域
        # self._content_layout.addWidget(title_bar)
        # self._content_layout.addWidget(QLabel("主内容区域", self))
        # self._content_layout.addStretch()
        
        main_layout.addWidget(self._content_widget)
        
        frame_layout.addWidget(self._frame_widget)
        
    @property
    def form(self):
        return self._content_widget

    def setupStyle(self):
        # 窗口样式表
        self.setStyleSheet("""
            #contentWidget {
                background: #FFFFFF;
                border-radius: 12px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self._shadow_radius)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        self.findChild(QWidget, "frameWidget").setGraphicsEffect(shadow)
        # self.findChild(QWidget, "contentWidget").setGraphicsEffect(shadow)
        # self.setGraphicsEffect(shadow)

    def closeEvent(self, a0):
        QApplication.quit()
        return super().closeEvent(a0)

    def geometry(self):
        frame_geo = self._frame_widget.geometry()
        frame_geo.adjust(-self._outside_margin, -self._outside_margin, self._outside_margin, self._outside_margin)
        return QRect(self.mapToGlobal(frame_geo.topLeft()), frame_geo.size())
    
    def _true_pos(self):
        return QWidget.pos(self)
    
    def _true_size(self):
        return QWidget.size(self)
    
    def _true_geometry(self):
        return QWidget.geometry(self)
    
    def x(self):
        return self.mapToGlobal(self._frame_widget.pos()).x() - self._outside_margin
        # return self._frame_widget.x() - self._outside_margin
    
    def y(self):
        return self.mapToGlobal(self._frame_widget.pos()).y() - self._outside_margin
        # return self._frame_widget.y() - self._outside_margin
    
    def width(self):
        return self._frame_widget.width() + self._outside_margin * 2
    
    def height(self):
        return self._frame_widget.height() + self._outside_margin * 2
    
    def pos(self):
        return QPoint(self.x(), self.y())
    
    def size(self):
        return QSize(self.width(), self.height())
    
    @typing.overload
    def move(self, x: int, y: int): ...
    @typing.overload
    def move(self, a0: QPoint): ...
    def move(self, *args):
        if len(args) == 2:
            x, y = args
        elif len(args) == 1:
            a0 = args[0]
            x = a0.x()
            y = a0.y()
        else:
            raise Exception(f'Invalid arguments in {self.__class__.__name__}.move()')
        x = x - self._shadow_radius + self._outside_margin # x = x - (self._true_x() - self._frame_widget.x())
        y = y - self._shadow_radius + self._outside_margin
        QWidget.move(self, QPoint(x, y))
    
    @typing.overload
    def setGeometry(self, x: int, y: int, w: int, h: int): ...
    @typing.overload
    def setGeometry(self, a0: QRect): ...
    def setGeometry(self, *args):
        if len(args) == 4:
            x, y, w, h = args
            # _expected_rect = QRect(x, y, w, h)
        elif len(args) == 1:
            _expected_rect = args[0]
            x, y, w, h = _expected_rect.x(), _expected_rect.y(), _expected_rect.width(), _expected_rect.height()
        else:
            raise Exception(f'Invalid arguments in {self.__class__.__name__}.setGeometry()')
        x += - self._shadow_radius + self._outside_margin
        y += - self._shadow_radius + self._outside_margin
        # w += (self._shadow_radius - self._outside_margin) * 2
        # h += ( - self._outside_margin) 
        # _expected_rect.adjust(- self._shadow_radius + self._outside_margin, - self._shadow_radius + self._outside_margin, \
        #    self._shadow_radius - self._outside_margin, self._shadow_radius - self._outside_margin)
        # QWidget.setGeometry(self, _expected_rect)
        QWidget.setGeometry(self, x, y, w, h)

    def _shadow_reduce_calculate_size(self, size: QSize):
        return size - QSize((self._shadow_radius - self._outside_margin) * 2, (self._shadow_radius - self._outside_margin) * 2)


class StylishLabel(QLabel):
    def __init__(self, parent, background_color, text_color, border_color):
        super().__init__(parent)
        self._background_color = background_color
        self._text_color = text_color
        self._border_color = border_color
        self._update_style(background_color, text_color, border_color)
        self.setText('00:00:00')
        self.setFixedSize(self.minimumSizeHint())
        
    def _update_style(self, background_color, text_color, border_color):
        self.setStyleSheet(f"""
                background-color: {background_color.name()};
                color: {text_color.name()};
                border: 2px solid {border_color.name()};
                font-size: 9pt;
                padding: 5px;
                border-radius: 10px;
            """)
    
    def refresh_style(self):
        self._update_style(self._background_color, self._text_color, self._border_color)

class AnimatedMenu(FadeoutMixin, QMenu):
    """具有淡入淡出和弹出动画效果的菜单类"""
    
    def __init__(self, parent=None, fade_when_idle=False):
        QMenu.__init__(self, parent)
        FadeoutMixin.__init__(self, fade_when_idle)
        
        # 设置窗口标志和属性以启用圆角和背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建弹出动画
        # self.popup_animation = QPropertyAnimation(self, b"pos")
        # self.popup_animation.setDuration(200)  # 动画持续200毫秒
        # self.popup_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 设置默认样式
        self._setup_style()
        
        # 设置淡入淡出透明度范围
        self.set_opacity_startend(0.9, 0.0)
        
        # 关联的窗口列表： 会在 [显示时和关闭时] 向其申请 [添加和删除关键矩形]
        self.related_widgets_list = []
        if self.parent() is not None and hasattr(self.parent(), 'add_key_rect'):
            self.related_widgets_list.append(self.parent())
    
    def _setup_style(self):
        """设置菜单样式"""
        self.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 255, 255, 0.90);
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 10px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 5px;
                margin: 2px 5px;
            }
            QMenu::item:selected {
                background-color: rgba(230, 230, 230, 0.8);
                color: rgba(0, 0, 0, 0.9);
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(200, 200, 200, 0.7);
                margin: 4px 10px;
            }
        """)
    
    def set_theme(self, bg_color, text_color, highlight_bg, highlight_text):
        """自定义菜单主题颜色"""
        self.setStyleSheet(f"""
            QMenu {{
                background-color: rgba(255, 255, 255, 0.90);
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 10px;
                padding: 5px;
            }}
            QMenu::item {{
                color: {text_color.name(QColor.HexArgb)};
                padding: 8px 20px;
                border-radius: 5px;
                margin: 2px 5px;
            }}
            QMenu::item:selected {{
                background-color: {highlight_bg.name(QColor.HexArgb)};
                color: {highlight_text.name(QColor.HexArgb)};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {QColor(bg_color).darker(110).name(QColor.HexArgb)};
                margin: 4px 10px;
            }}
        """)
    
    def add_related_fadeout_widget(self, widget):
        """添加关联的窗口"""
        if widget not in self.related_widgets_list:
            self.related_widgets_list.append(widget)
    
    def remove_related_fadeout_widget(self, widget):
        """移除关联的窗口"""
        if widget in self.related_widgets_list:
            self.related_widgets_list.remove(widget)
    
    def showEvent(self, event):
        """菜单显示时的动画效果"""
        # 下面是一些废弃的动画效果
        # # 获取目标位置
        # target_pos = self.pos()
        # # 设置起始位置（稍微向下偏移）
        # self.move(target_pos.x(), target_pos.y() + 15)
        # self.popup_animation.setStartValue(self.pos())
        # self.popup_animation.setEndValue(target_pos)
        # self.popup_animation.start()
        
        # 设置动画
        self.try_fadeout_animation(False)
        
        super().showEvent(event)

        for widget in self.related_widgets_list:
            if hasattr(widget, 'add_key_fadeout_rect'):
                widget.add_key_fadeout_rect(self.geometry())
        
    def closeEvent(self, event):
        for widget in self.related_widgets_list:
            if hasattr(widget, 'remove_key_fadeout_rect'):
                widget.remove_key_fadeout_rect(self.geometry())
        super().closeEvent(event)
            
    def on_fadingout(self, fading: bool):
        """淡入淡出过程中的回调"""
        pass
    
    def on_fade_finished(self, faded: bool):
        """淡入淡出完成后的回调"""
        if faded:
            # 如果已经淡出了，可以在这里做一些处理
            self.close()
            pass
    
    def exec_(self, pos=None):
        """执行菜单显示，可以指定位置"""
        if pos:
            return super().exec_(pos)
        return super().exec_(QCursor.pos())
    
    def add_styled_action(self, text, callback, icon=None):
        """添加一个带样式的操作项"""
        action = QAction(text, self)
        if icon:
            action.setIcon(icon)
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def paintEvent(self, event):
        """自定义绘制事件，添加阴影效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制阴影
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 10, 10)
        
        # 半透明背景
        painter.fillPath(path, QColor(0, 0, 0, 15))
        
        # 调用原生绘制
        super().paintEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.parent().mouseMoveEvent(event)

