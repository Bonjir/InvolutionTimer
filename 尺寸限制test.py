from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt

from SimpleAnimation import *

app = QApplication([])

window = QWidget()
window.setGeometry(QRect(100, 100, 300, 200))
button = QPushButton("Click Me", window)

# 设置按钮的尺寸策略，允许它无最小尺寸限制
# button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
# 设置按钮的最小尺寸为 (0, 0)
# button.setMinimumSize(0, 0)

# layout = QGridLayout(window)
# layout.addWidget(button, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

animation = SimpleShrink(button, shrink_to=ShrinkTo.center)

animation.set_normal_size(QSize(150, 150))
# animation.set_mini_size(QSize(20, 20))
animation.set_restore_pos(QPoint(10, 10))


button.clicked.connect(animation.start_shrink_animation)
# button.clicked.connect(animation.start_restore_animation)

window.show()
app.exec_()
