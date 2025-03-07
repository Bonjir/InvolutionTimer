import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import typing

from customwidgets import DraggableMixin, PenetrateWidget
from ui.widget import Ui_Form 

class FrameWidget(PenetrateWidget):
    def __init__(self, *args):
        super().__init__(*args)
    
    def paintEvent(self, event):
        # 绘制自定义边框
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect().adjusted(1, 1, -1, -1)), 15, 15) # 留出阴影空间
        
        # 绘制背景边框
        painter.setPen(QPen(QColor("#E0E0E0"), 2))
        painter.drawPath(path)
        
class StylishFramelessWindow(DraggableMixin, QWidget):
    def __init__(self, clipped, outside_margin, inside_margin, shadow_radius = 15):
        QWidget.__init__(self)
        DraggableMixin.__init__(self, clipped=clipped)
        self._outside_margin = outside_margin
        self._inside_margin = inside_margin
        self._shadow_radius = shadow_radius
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
        self.setMinimumSize(400, 300)

    def setupUI_StylishFrame(self):
        # 边框层
        frame_layout = QVBoxLayout(self)
        frame_layout.setContentsMargins(*([self._shadow_radius] * 4))
        
        self._frame_widget = FrameWidget(self)
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
    

class Window(StylishFramelessWindow, Ui_Form):
    def __init__(self):
        super().__init__(clipped=True, outside_margin=3, inside_margin=10)
        # self.set_geometry_func(self.frameGeometry)
        self.setupUi(self._content_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # window = StylishFramelessWindow()
    window = Window()
    window.show()
    sys.exit(app.exec_())