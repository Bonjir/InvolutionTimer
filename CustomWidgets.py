# affliated to 卷摆计时器.py

from PyQt5.QtCore import Qt, QTime, QEasingCurve, \
    QPoint, QSize, QRect, \
    QTimer, QPropertyAnimation, pyqtProperty, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QApplication
from PyQt5.QtGui import QCursor, QColor, QPainterPath
import typing

from ui.palette import Palette

class AnimatedButtonMixin:
    doubleClicked = pyqtSignal()
    def __init__(self, *args):
        super().__init__(*args)  # 跳过所有参数
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
        self._update_style()
        
        # 悬停动画
        self._hover_animation = QPropertyAnimation(self, b"blend_color")
        self._hover_animation.setDuration(400)  # 动画时长 400ms
        self._hover_animation.setEasingCurve(QEasingCurve.Type.InOutSine)  # 平滑缓动
        
        self._hover_animation.setStartValue(self._bg_basic_color)
        self._hover_animation.setEndValue(self._bg_hover_color)

        self.enterEvent = lambda e: self._toggle_hover_animation(True)
        self.leaveEvent = lambda e: self._toggle_hover_animation(False)

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
                padding: 10px;
                border-radius: 10px;
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
    
    def mouseDoubleClickEvent(self, e):
        self.doubleClicked.emit()
    
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
    
    def toggled(self):
        return self._toggled
    
class AnimatedPushButton(AnimatedButtonMixin, QPushButton):
    def __init__(self, *args):
        super().__init__(*args) # 向上传递所有参数


class MouseEventPenetrateMixin:
    def __init__(self, *args):
        super().__init__(*args) # 跳过所有参数
        pass
    
    def mousePressEvent(self, e):
        self.parent().mousePressEvent(e) # 把事件转发给主窗口
        return super().mousePressEvent(e)
    
    def mouseMoveEvent(self, e):
        self.parent().mouseMoveEvent(e)
        return super().mouseMoveEvent(e)
    
    def mouseReleaseEvent(self, e):
        self.parent().mouseReleaseEvent(e) # 其实对于penetrate button来说这个多余的，会多出一个release event，但是对于edit又是必要的
        return super().mouseReleaseEvent(e)

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
        
        # 如果有下一个控件，则将焦点转移过去
        while index + 1 < layout.count():
            index += 1
            next_widget = layout.itemAt(index).widget()
            # print(next_widget)
            if isinstance(next_widget, QLineEdit):
                next_widget.setFocus()
                return
            
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
        self._dragging = False
        self._drag_offset = QPoint()
        
        # 限制在屏幕内拖动
        self._clipped = clipped
        
        # # 阴影部分的偏移
        # self._shadow_offset = 0
        # self._shadow_offset_switch = shadow_offset_switch
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录鼠标按下时的窗口位置
            self._dragging = True
            self._drag_offset = event.globalPos() - self.pos()
            self._first_drag_pos = event.globalPos()
            
            # 获取阴影部分的偏移
            # if self._shadow_offset
            # shadow_geo = self.frameGeometry()
            # geo = self.geometry()
            # self._shadow_offset = QSize(geo.x() - shadow_geo.x(), geo.y() - shadow_geo.y())

        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._dragging:
            # 限制拖拽的最小距离
            _drag_offset = event.globalPos() - self._first_drag_pos
            if abs(_drag_offset.x()) <= self.DRAG_OFFSET_MINIMUM and abs(_drag_offset.y()) <= self.DRAG_OFFSET_MINIMUM:
                return
            self._first_drag_pos = QPoint(-100, -100) # 第一次拖动之后就不再限制
            
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
            self._dragging = False
        
        # print(self.x(), self.y(), self.width(), self.geometry())
        return super().mouseReleaseEvent(event)
            
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
            self.toggle_animation(False)
            self._is_faded = False
        super().enterEvent(event)
        
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if not self._fade_when_idle:
            return super().mouseMoveEvent(event)
        
        self._last_move_time = QTime.currentTime()
        if self._is_faded:
            self.toggle_animation(False)
            self._is_faded = False
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self._fade_when_idle:
            return super().mouseReleaseEvent(event)
        
        if event.button() == Qt.LeftButton:
            self._pressing = False
        return super().mouseReleaseEvent(event)
    
    def _check_idle(self):
        """检查是否有空闲时间，如果空闲则缩小窗口"""
        if self.geometry().contains(QCursor.pos()) or self._pressing:
            self._last_move_time = QTime.currentTime()
            return
        
        if self._last_move_time.msecsTo(QTime.currentTime()) > self._idle_span and \
          not self._is_faded:
            self.toggle_animation(True)
            self._is_faded = True
            
    def toggle_animation(self, fading):
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
        

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QHBoxLayout, QGraphicsDropShadowEffect)
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
