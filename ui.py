# affliated to 卷摆计时器.py

from PyQt5.QtWidgets import QGridLayout, QSizePolicy

from CustomWidgets import *
from SimpleAnimation import SimpleShrink


class Ui_Form(object):
    def setupUI(self, Form):
        
        # 创建一个显示时间的标签
        # self.time_label = QLabel(self)
        # self.time_label.setStyleSheet("font-size: 30px; font-family: 微软雅黑;")
        # self.time_label.setFixedHeight(40)
        
        # 创建摆计时按钮，上面显示摆时间
        self.relax_button = MouseEventPenetrateButton(Form)
        # self.relax_button.setStyleSheet('background-color: lightpink; font-size: 30px; font-family: Consolas;')
        # self.relax_button.setFixedSize(QSize(150, 50))
        # self.relax_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.relax_button_shrink = SimpleShrink(self.relax_button, shrink_to=ShrinkTo.center)
        # 创建卷计时按钮，上面显示卷时间
        self.work_button = MouseEventPenetrateButton(Form)
        # self.work_button.setStyleSheet('background-color: lightblue; font-size: 30px; font-family:  Consolas;')
        # self.work_button.setFixedSize(QSize(150, 50))
        # self.work_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.work_button_shrink = SimpleShrink(self.work_button, shrink_to=ShrinkTo.center)
        # 创建停止计时按钮，上面显示北京时间
        self.stop_button = MouseEventPenetrateButton(Form)
        # self.stop_button.setStyleSheet('background-color: lightgray; font-size: 30px; font-family: Consolas;')
        # self.stop_button.setFixedSize(QSize(150, 50))
        # self.stop_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stop_button_shrink = SimpleShrink(self.stop_button, shrink_to=ShrinkTo.center)

        self.relax_edit = MouseEventPenetrateLineEdit(Form)
        # self.relax_edit.setStyleSheet('background-color: lightpink; font-size: 30px; font-family: Consolas;')
        # self.relax_edit.setFixedSize(QSize(150, 50))
        # self.relax_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.relax_edit_shrink = SimpleShrink(self.relax_edit, shrink_to=ShrinkTo.vcenter_right)
        
        self.work_edit = MouseEventPenetrateLineEdit(Form)
        # self.work_edit.setStyleSheet('background-color: lightblue; font-size: 30px; font-family: Consolas;')
        # self.work_edit.setFixedSize(QSize(150, 50))
        # self.work_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.work_edit_shrink = SimpleShrink(self.work_edit, shrink_to=ShrinkTo.vcenter_right)
        
        self.clear_button = MouseEventPenetrateButton(Form, '〇')
        # self.clear_button.setStyleSheet('background-color: lightgray; font-size: 30px; font-family: Consolas;')
        # self.clear_button.setFixedSize(QSize(150, 50))
        # self.clear_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.clear_button_shrink = SimpleShrink(self.clear_button, shrink_to=ShrinkTo.vcenter_right)

        self.set_layout_normal(Form)

    def set_layout_normal(self, Form):
        # 布局管理器 QGridLayout
        layout = QGridLayout()
        layout.addWidget(self.relax_button, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        layout.addWidget(self.work_button, 1, 0, 1, 1, alignment=Qt.AlignCenter)
        layout.addWidget(self.stop_button, 2, 0, 1, 1, alignment=Qt.AlignCenter)
        layout.addWidget(self.relax_edit, 0, 1, 1, 1, alignment=Qt.AlignCenter)
        layout.addWidget(self.work_edit, 1, 1, 1, 1, alignment=Qt.AlignCenter)
        layout.addWidget(self.clear_button, 2, 1, 1, 1, alignment=Qt.AlignCenter)
        layout.setContentsMargins(5, 5, 5, 5)
        Form.setLayout(layout)
        
    def deleteOldLayout(self, Form):
        # 如果已有布局，先删除它
        old_layout = Form.layout()
        if old_layout:
            # 移除布局中的所有子部件
            while old_layout.count():
                child = old_layout.takeAt(0)
                # if child.widget():
                #     child.widget().deleteLater()
        
    def changeLayout_RelaxMini(self, Form):
        self.deleteOldLayout(Form)
        # 创建新的布局并设置
        layout = QGridLayout()
        layout.addWidget(self.relax_button, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        Form.setLayout(layout)
        
    def changeLayout_WorkMini(self, Form):
        self.deleteOldLayout(Form)
        # 创建新的布局并设置
        layout = QGridLayout()
        layout.addWidget(self.work_button, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        Form.setLayout(layout)
        
    def changeLayout_BjtimeMini(self, Form):
        self.deleteOldLayout(Form)
        # 创建新的布局并设置
        layout = QGridLayout()
        layout.addWidget(self.stop_button, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        Form.setLayout(layout)
        