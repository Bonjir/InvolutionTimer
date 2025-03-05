# conda env etc
# last edit on 25/1/4 18:41

import sys
from PyQt5.QtCore import QTimer, QTime, Qt, QPoint, QEvent, QPropertyAnimation, QEasingCurve, \
    QRect, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMainWindow, \
    QGridLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QCursor
import typing
import win32.win32api as win32api
import win32.lib.win32con as win32con

from CustomWidgets import *
from ui import Ui_Form 

def seconds_to_hms(seconds):
    # 使用 divmod 计算小时、分钟和秒数
    hours, remainder = divmod(seconds, 3600)  # 3600秒是1小时
    minutes, seconds = divmod(remainder, 60)  # 60秒是1分钟
    # 返回格式化后的字符串
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

class WorkRelaxTimerWindow(ShrinkWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        
        # 初始设置窗口大小、标题等
        self.setWindowTitle("WorkRelaxTimerWindow")
        self.set_mini_size(QSize(150, 50))
        self.set_main_size(QSize(300, 150))
        self.setGeometry(0, 0, self.main_size.width(), self.main_size.height())  # 初始窗口大小
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint |
                            Qt.Tool |
                            Qt.MSWindowsFixedSizeDialogHint)
        
        self.setFocus()
        
        # ui框架
        self.setupUI(self)
        
        # 子控件事件连接
        self.work_button.clicked.connect(self.work_button_clicked)
        self.relax_button.clicked.connect(self.relax_button_clicked)
        self.stop_button.clicked.connect(self.stop_button_clicked)
        # self.relax_edit.editingFinished.connect(self.relax_edit_editingFinished)
        # self.work_edit.editingFinished.connect(self.work_edit_editingFinished)
        self.clear_button.clicked.connect(self.clear_button_clicked)
        self.clear_button.installEventFilter(self)
        
        # debug
        # self.work_button.setMinimumSize(0, 0)
        # self.work_button_shrink.set_normal_size(QSize(150, 150))
        # self.work_button_shrink.set_mini_size(QSize(20, 20))
        # self.work_button_shrink.set_restore_pos(QPoint(10, 10))
        # # self.work_button.clicked.connect(self.work_button_shrink.start_shrink_animation)
        # self.work_button.clicked.connect(self.work_button_shrink.start_restore_animation)
         
        # 初始化卷摆时间, 设为-1是因为第一次执行会+1
        self.work_time_sec = -1
        self.relax_time_sec = -1
        
        # 设置定时器更新时间显示
        self.work_timer = QTimer(self)
        self.work_timer.timeout.connect(self.update_worktime)
        self.update_worktime() # 设置的时候先执行一次
        self.relax_timer = QTimer(self)
        self.relax_timer.timeout.connect(self.update_relaxtime)
        self.update_relaxtime() # 设置的时候先执行一次
        self.bjtime_timer = QTimer(self)
        self.bjtime_timer.timeout.connect(self.update_bjtime)
        self.update_bjtime() # 设置的时候先执行一次
        self.bjtime_timer.start(1000)  # 每秒更新时间
        

    def work_button_clicked(self):
        self.work_timer.start(1000)
        self.relax_timer.stop()
        
    def update_worktime(self):
        """更新卷时间显示"""
        self.work_time_sec += 1
        work_time_hms = seconds_to_hms(self.work_time_sec)
        self.work_button.setText(work_time_hms)

    def relax_button_clicked(self):
        self.work_timer.stop()
        self.relax_timer.start(1000)
            
    def update_relaxtime(self):
        """更新摆时间显示"""
        self.relax_time_sec += 1
        relax_time_hms = seconds_to_hms(self.relax_time_sec)
        self.relax_button.setText(relax_time_hms)
        
    def stop_button_clicked(self):
        self.work_timer.stop()
        self.relax_timer.stop()
        
    def update_bjtime(self):
        """更新北京时间显示"""
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.stop_button.setText(current_time)
        
    def editingFinishedEvent(self, event):
        try:
            work_suplement = int(self.work_edit.text())
            self.work_time_sec += work_suplement
        except:
            pass
        try:
            relax_suplement = int(self.relax_edit.text())
            self.relax_time_sec += relax_suplement
        except:
            pass
        self.work_time_sec = max(-1, self.work_time_sec - 1)
        self.relax_time_sec = max(-1, self.relax_time_sec - 1)
        self.update_worktime()
        self.update_relaxtime()
        self.work_edit.setText('')
        self.relax_edit.setText('')
        
    def clear_button_clicked(self):
        # 初始化卷摆时间, 设为-1是因为第一次执行会+1
        self.work_time_sec = -1
        self.relax_time_sec = -1
        self.update_worktime()
        self.update_relaxtime()
    
    def clear_button_doubleClicked(self):
        # 双击清零退出
        self.closeEvent(None)
    
    
    def eventFilter(self, obj, event):
        if obj == self.clear_button:
            if event.type() == event.MouseButtonDblClick:
                self.clear_button_doubleClicked()
                return True  # 事件已经处理，不再传递
        return super().eventFilter(obj, event)

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Tab:
            print('tab pressed in main')
            a0.ignore()
            return
        return super().keyPressEvent(a0)
    
    def showEvent(self, a0):
        # 模拟点击消除掉tool窗口首次press的延迟
        def simulate_click():
            # 获取窗口的位置
            initial_pos = self.pos()
            cursorpos = QCursor.pos()
            # win32api模拟点击
            win32api.SetCursorPos((initial_pos.x(), initial_pos.y()))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            win32api.SetCursorPos((cursorpos.x(), cursorpos.y()))
        QTimer.singleShot(0, simulate_click)
        return super().showEvent(a0)
    
    def shrink_window(self):
        # self.relax_edit_shrink.start_shrink_animation(1000)
        # self.work_edit_shrink.start_shrink_animation(1000)
        # self.clear_button_shrink.start_shrink_animation(1000)
        if self.relax_timer.isActive():
            self.work_button_shrink.start_shrink_animation()
            self.stop_button_shrink.start_shrink_animation()
            self.changeLayout_RelaxMini(self)
        elif self.work_timer.isActive():
            self.relax_button_shrink.start_shrink_animation()
            self.stop_button_shrink.start_shrink_animation()
            self.changeLayout_WorkMini(self)
        else:
            self.work_button_shrink.start_shrink_animation()
            self.relax_button_shrink.start_shrink_animation()
            self.changeLayout_BjtimeMini(self)
        super().shrink_window()
    
# 主函数
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = WorkRelaxTimerWindow()
    window.show()  # 显示窗口

    sys.exit(app.exec_())  # 运行应用
