
# TODO
# - mini窗口label的显示，哪个启用显示哪个，然后双击锁定 v
# - 检测程序是否正常关闭并恢复 v 
# - 日志 v
# - 双击和单击分离开 v
# - 存储每日卷摆数据
# - tooltip
# - 右键列表
# - 每日数据统计
# - 机器学习判断卷摆(时间、日程、息屏等信息判断息屏时是否在学习、吃饭、娱乐)

# BUG
# - miniwindow的layout更新后位置及大小出错问题 v
# - edit控件回车失效问题 v
# - 拖拽mini窗口后mini消失_dragging没有解除，需要再次在主窗口点击才能解除 v
# - 在animatedbutton类中添加font和(fixedsize)的stylesheet v
# - 长时间休眠后btn和label字体改变（添加每秒/从休眠中唤醒时 检测字体） v

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import win32api
import win32con

from customwidgets import *
from ui.widget import Ui_Form 
from ui.palette import Palette
from utils import CrashHandler, Logger

_logger = Logger(__name__)

class Ui_MiniWindow:
    def setupUi(self, Form, *args):
        work_color, relax_color, bjtime_color = args

        # 控件初始化
        self.vlayout = QVBoxLayout()
        self.work_label = QLabel(Form)
        self.work_label.setStyleSheet(f"""
                background-color: {'white'};
                color: {work_color.name()};
                border: 2px solid {work_color.name()};
                font-size: 9pt;
                padding: 5px;
                border-radius: 10px;
            """)
        self.work_label.setText('00:00:00')
        label_size = self.work_label.minimumSizeHint()
        # print('label_size:', label_size) # debug
        self.work_label.setFixedSize(label_size)
        # if labels_enable[0]:
        self.vlayout.addWidget(self.work_label)
        
        self.relax_label = QLabel(Form)
        self.relax_label.setStyleSheet(f"""
                background-color: {'white'};
                color: {relax_color.name()};
                border: 2px solid {relax_color.name()};
                font-size: 9pt;
                padding: 5px;
                border-radius: 10px;
            """)
        self.relax_label.setText('00:00:00')
        self.relax_label.setFixedSize(label_size)
        # if labels_enable[1]:
        self.vlayout.addWidget(self.relax_label)
        
        self.bjtime_label = QLabel(Form)
        self.bjtime_label.setStyleSheet(f"""
                background-color: {'white'};
                color: {bjtime_color.name()};
                border: 2px solid {bjtime_color.name()};
                font-size: 9pt;
                padding: 5px;
                border-radius: 10px;
            """)
        self.bjtime_label.setText('00:00:00')
        self.bjtime_label.setFixedSize(label_size)
        # if labels_enable[2]:
        self.vlayout.addWidget(self.bjtime_label)
        
        self.vlayout.setContentsMargins(0, 0, 0, 0) # 透明边框大小
        self.vlayout.setSpacing(2) # 间距
        Form.setLayout(self.vlayout)
        

class MiniWindow(MouseEventPenetrateMixin, FadeoutMixin, StylishFramelessWindow, Ui_MiniWindow):
    def __init__(self, parent, \
        work_color: QColor, relax_color: QColor, bjtime_color: QColor, \
        work_signal: pyqtSignal, relax_signal: pyqtSignal, bjtime_signal: pyqtSignal):
        
        StylishFramelessWindow.__init__(self, clipped=True, outside_margin=2, inside_margin=0, parent=parent, exframe_show=False)
        FadeoutMixin.__init__(self, fade_when_idle=False)
        
        self.setupUi(self.form, work_color, relax_color, bjtime_color)        
        self.vlayout:QVBoxLayout
        self.work_label:QLabel
        self.relax_label:QLabel
        self.bjtime_label:QLabel
        
        # 初始设置窗口大小、标题等
        self.adjustSize()
        self.setWindowTitle("WorkRelaxTimerMini")
        # minimum_size = self.minimumSizeHint()
        # pos = self.proper_pos(main_geometry, minimum_size)
        # self.setGeometry(*pos, minimum_size.width(), minimum_size.height())  # 初始窗口大小
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint |
                            Qt.Tool |
                            Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowOpacity(0) # 设为全透明 
        self.set_opacity_startend(0.75, 0)
        self.setMouseTracking(True)
        for child in self.findChildren(QWidget):
            child.setMouseTracking(True)

        # 信号与槽
        # if labels_enable[0]:
        work_signal.connect(self.on_worktime_update)
        # if labels_enable[1]:
        relax_signal.connect(self.on_relaxtime_update)
        # if labels_enable[2]:
        bjtime_signal.connect(self.on_bjtime_update)
    
    def enable_labels(self, enable: tuple):
        if enable[0]:
            self.work_label.show()
            # self.vlayout.addWidget(self.work_label)
        else:
            # self.vlayout.removeWidget(self.work_label)
            self.work_label.hide()
        if enable[1]:
            self.relax_label.show()
            # self.vlayout.addWidget(self.relax_label)
        else:
            # self.vlayout.removeWidget(self.relax_label)
            self.relax_label.hide()
        if enable[2]:
            self.bjtime_label.show()
            # self.vlayout.addWidget(self.bjtime_label)
        else:
            # self.vlayout.removeWidget(self.bjtime_label)
            self.bjtime_label.hide()
        # self.vlayout.setParent(self.form)
        # self.vlayout.setContentsMargins(0, 0, 0, 0) # 透明边框大小
        # self.vlayout.setSpacing(2) # 间距
        # self.form.setLayout(None)
        # self.form.setLayout(self.vlayout)
    
    def proper_pos(self, main_geometry: QRect, self_size: QRect):
        # 合理的屏幕范围
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        
        if main_geometry.left() <= screen_geometry.left() and main_geometry.top() <= screen_geometry.top():
            # return Positions.top_left
            return (main_geometry.left(), main_geometry.top())
        elif main_geometry.left() >= screen_geometry.right() - main_geometry.width() and main_geometry.top() <= screen_geometry.top():
            # return Positions.top_right
            return (main_geometry.right() - self_size.width(), main_geometry.top())
        elif main_geometry.top() <= screen_geometry.top():
            # return Positions.top_center
            return (int((main_geometry.left() + main_geometry.right()) / 2 - self_size.width() / 2), main_geometry.top())
        
        elif main_geometry.left() <= screen_geometry.left() and main_geometry.top() >= screen_geometry.bottom() - main_geometry.height():
            # return Positions.bottom_left
            return (main_geometry.left(), main_geometry.bottom() - self_size.height())
        elif main_geometry.left() >= screen_geometry.right() - main_geometry.width() and main_geometry.top() >= screen_geometry.bottom() - main_geometry.height():
            # return Positions.bottom_right
            return (main_geometry.right() - self_size.width(), main_geometry.bottom() - self_size.height())
        elif main_geometry.top() >= screen_geometry.bottom() - main_geometry.height():
            # return Positions.bottom_center
            return (int((main_geometry.left() + main_geometry.right()) / 2 - self_size.width() / 2), main_geometry.bottom() - self_size.height())
        
        elif main_geometry.left() <= screen_geometry.left():
            # return Positions.vcenter_left
            return (main_geometry.left(), int((main_geometry.top() + main_geometry.bottom()) / 2 - self_size.height() / 2))
        elif main_geometry.left() >= screen_geometry.right() - main_geometry.width():
            # return Positions.vcenter_right
            return (main_geometry.right() - self_size.width(), int((main_geometry.top() + main_geometry.bottom()) / 2 - self_size.height() / 2))
        else:
            # return Positions.center
            return (int((main_geometry.left() + main_geometry.right()) / 2 - self_size.width() / 2), int((main_geometry.top() + main_geometry.bottom()) / 2 - self_size.height() / 2))
        
    def on_worktime_update(self, str):
        self.work_label.setText(str)
        
    def on_relaxtime_update(self, str):
        self.relax_label.setText(str)
        
    def on_bjtime_update(self, str):
        self.bjtime_label.setText(str)
    
    def on_fade_finished(self, fading):
        # if self._dragging == True:
        #     self._dragging = False
        #     self.parent()._dragging = False
            
        return super().on_fadingout(fading)

    
class WorkRelaxTimerWindow(FadeoutMixin, StylishFramelessWindow, Ui_Form):
    signal_worktime_update = pyqtSignal(str)
    signal_relaxtime_update = pyqtSignal(str)
    signal_bjtime_update = pyqtSignal(str)
    
    def __init__(self):
        StylishFramelessWindow.__init__(self, clipped=True, outside_margin=3, inside_margin=3)
        FadeoutMixin.__init__(self, fade_when_idle = True)
        # DraggableMixin.__init__(self, clipped=True)
        # ui框架
        self.setupUi(self.form)
        self.work_button: PenetrateAnimatedButton
        self.relax_button: PenetrateAnimatedButton
        self.stop_button: PenetrateAnimatedButton
        self.clear_button: PenetrateAnimatedButton
        self.work_edit: PenetrateLineEdit
        self.relax_edit: PenetrateLineEdit
        
        self.work_button.set_bg_color(Palette.white, Palette.blue_light, Palette.blue)
        self.work_button.set_text_color(Palette.blue, Palette.blue_dark, Palette.white)
        
        self.relax_button.set_bg_color(Palette.white, Palette.orange_light, Palette.orange)
        self.relax_button.set_text_color(Palette.orange, Palette.orange_dark, Palette.white)
        
        self.stop_button.set_bg_color(Palette.white, Palette.green_light, Palette.green)
        self.stop_button.set_text_color(Palette.green, Palette.green_dark, Palette.white)
        
        self.clear_button.set_bg_color(Palette.white, Palette.red_light, Palette.red)
        self.clear_button.set_text_color(Palette.red, Palette.red_dark, Palette.white)
        self.clear_button.setText('clear')

        self.mini = MiniWindow(self, \
            Palette.blue, Palette.orange, Palette.green,\
            self.signal_worktime_update, self.signal_relaxtime_update, self.signal_bjtime_update)
        
        # 初始设置窗口大小、标题等
        self.setWindowTitle("WorkRelaxTimerWindow")
        minimum = self.minimumSizeHint()
        self.setGeometry(0, 0, minimum.width(), minimum.height())  # 初始窗口大小
        self.setWindowOpacity(0.9) # 设为全透明 
        self.set_opacity_startend(0.90, 0)
        self.setFocus()
        
        # 子控件事件连接
        self.work_button.singleClicked.connect(self.on_work_button_clicked)
        self.work_button.doubleClicked.connect(self.on_work_button_doubleClicked)
        self.relax_button.singleClicked.connect(self.on_relax_button_clicked)
        self.relax_button.doubleClicked.connect(self.on_relax_button_doubleClicked)
        self.stop_button.singleClicked.connect(self.on_stop_button_clicked)
        self.stop_button.doubleClicked.connect(self.on_stop_button_doubleClicked)
        self.clear_button.singleClicked.connect(self.on_clear_button_clicked)
        self.clear_button.doubleClicked.connect(self.on_clear_button_doubleClicked)
        # self.clear_button.installEventFilter(self)
        
        # 初始化卷摆时间, 设为-1是因为第一次执行会+1
        self._work_time_sec = -1
        self._relax_time_sec = -1
        
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
        
        self.self_check_timer = QTimer(self)
        self.self_check_timer.timeout.connect(self.self_check)
        self.self_check_timer.start(60*1000) # 每分钟自检一次
        
        # 异常处理
        self._crash_handler = CrashHandler()
        self._crash_handler.set_state_func(self.state_func)
        crash_state = self._crash_handler.check_previous_crash()
        self.restore_from_crash(crash_state)
        self._crash_handler.create_running_flag()
        
        
    def _seconds_to_hms(self, seconds):
        # 使用 divmod 计算小时、分钟和秒数
        hours, remainder = divmod(seconds, 3600)  # 3600秒是1小时
        minutes, seconds = divmod(remainder, 60)  # 60秒是1分钟
        # 返回格式化后的字符串
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def on_work_button_clicked(self):
        self.work_timer.start(1000)
        self.relax_timer.stop()
        
    def on_work_button_doubleClicked(self):
        self.work_button.set_toggled(not self.work_button.toggled())
    
    def update_worktime(self):
        """更新卷时间显示"""
        self._work_time_sec += 1
        work_time_hms = self._seconds_to_hms(self._work_time_sec)
        self.work_button.setText(work_time_hms)
        self.signal_worktime_update.emit(work_time_hms)

    def on_relax_button_clicked(self):
        self.work_timer.stop()
        self.relax_timer.start(1000)
            
    def on_relax_button_doubleClicked(self):
        self.relax_button.set_toggled(not self.relax_button.toggled())
    
    def update_relaxtime(self):
        """更新摆时间显示"""
        self._relax_time_sec += 1
        relax_time_hms = self._seconds_to_hms(self._relax_time_sec)
        self.relax_button.setText(relax_time_hms)
        self.signal_relaxtime_update.emit(relax_time_hms)
        
    def on_stop_button_clicked(self):
        self.work_timer.stop()
        self.relax_timer.stop()
        
    def on_stop_button_doubleClicked(self):
        self.stop_button.set_toggled(not self.stop_button.toggled())
    
    def update_bjtime(self):
        """更新北京时间显示"""
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.stop_button.setText(current_time)
        self.signal_bjtime_update.emit(current_time)
        
        # 为了刷新一下控件防止字体变化
        self._work_time_sec -= 1
        self.update_worktime()
        self._relax_time_sec -= 1
        self.update_relaxtime()
        
        
    def on_clear_button_clicked(self):
        # 初始化卷摆时间, 设为-1是因为第一次执行会+1
        self._work_time_sec = -1
        self._relax_time_sec = -1
        self.update_worktime()
        self.update_relaxtime()
    
    def on_clear_button_doubleClicked(self):
        # 双击清零退出
        self.closeEvent(None)
    
    def editingFinishedEvent(self, event):
        try:
            work_suplement = int(self.work_edit.text())
            self._work_time_sec += work_suplement * 60
        except:
            pass
        try:
            relax_suplement = int(self.relax_edit.text())
            self._relax_time_sec += relax_suplement * 60
        except:
            pass
        self._work_time_sec = max(-1, self._work_time_sec - 1)
        self._relax_time_sec = max(-1, self._relax_time_sec - 1)
        self.update_worktime()
        self.update_relaxtime()
        self.work_edit.setText('')
        self.relax_edit.setText('')
        
    # def keyPressEvent(self, a0):
    #     if a0.key() == Qt.Key.Key_Tab:
    #         # print('tab pressed in main')
    #         a0.ignore()
    #         return
    #     return super().keyPressEvent(a0)
    
    def showEvent(self, a0):
        # 模拟点击消除掉tool窗口首次press的延迟
        def simulate_click():
            # 获取窗口的位置
            initial_pos = self.pos()
            cursorpos = QCursor.pos()
            # win32api模拟点击
            win32api.SetCursorPos((initial_pos.x() + 5, initial_pos.y() + 5))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            win32api.SetCursorPos((cursorpos.x(), cursorpos.y()))
        QTimer.singleShot(0, simulate_click)
        return super().showEvent(a0)
    
    def closeEvent(self, event):
        # 在关闭前显示提示框
        self._crash_handler.clean_exit()
        QApplication.quit()  # 强制退出应用程序

    def on_fadingout(self, fading: bool):
        if fading:
            work_label_enabled = self.work_timer.isActive() or self.work_button.toggled()
            relax_label_enabled = self.relax_timer.isActive() or self.relax_button.toggled()
            bjtime_label_enabled = not self.work_timer.isActive() and not self.relax_timer.isActive() or self.stop_button.toggled()
            self.mini.enable_labels((work_label_enabled, relax_label_enabled, bjtime_label_enabled))
            
            def _delayed_task():
                # self.mini.adjustSize()
                mini_size_shadow = self.mini.minimumSizeHint()
                mini_size = self.mini._shadow_reduce_calculate_size(mini_size_shadow)
                mini_pos = self.mini.proper_pos(self.geometry(), mini_size)
                self.mini.setGeometry(QRect(*mini_pos, mini_size.width(), mini_size.height()))
            
            QTimer.singleShot(50, _delayed_task) # 在信号函数中处理ui需要手动延时
            
            self.mini.show()
            self.mini.toggle_animation(fading=False)
            
        else:
            self.mini.toggle_animation(fading=True)
            
        return super().on_fadingout(fading)
    
    def on_fade_finished(self, faded):
        # if not faded:
        #     self.mini.hide()
        
        return super().on_fade_finished(faded)
    
    def state_func(self):
        return {'work':self._work_time_sec, 'relax':self._relax_time_sec}
    
    def restore_from_crash(self, state):
        if state == None or state == {}:
            return True
        try:
            self._work_time_sec = state['work']
            self._relax_time_sec = state['relax']
        except:
            _logger.warning('恢复加载失败')
            return False
        self._work_time_sec = max(-1, self._work_time_sec - 1)
        self._relax_time_sec = max(-1, self._relax_time_sec - 1)
        self.update_worktime()
        self.update_relaxtime()
        return True
    
    def self_check(self):
        """
        执行一些自检功能，比如检测字体是否正常、自动保存状态。
        """
        # TODO 检测字体
        ...
        self._crash_handler.save_app_state()
    
# 主函数
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = WorkRelaxTimerWindow()
    window.show()  # 显示窗口

    sys.exit(app.exec_())  # 运行应用
