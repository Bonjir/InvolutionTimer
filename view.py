# 
# TODO
# - 右键列表
# - 每日数据统计
# - tooltip
# - 机器学习判断卷摆(时间、日程、息屏等信息判断息屏时是否在学习、吃饭、娱乐)
# - 记录休眠时间数据，并添加提示框询问是否是卷摆 （记录：时间、长度、星期、正在计时卷/摆）
# - mini窗口label的显示，哪个启用显示哪个，然后双击锁定 v
# - 检测程序是否正常关闭并恢复 v 
# - 日志 v
# - 存储每日卷摆数据 ?

# TODO-CODE
# 把crash_handler和data_manager的初始化移到app.py中 v

# BUG
# - 从Crash中恢复之后label的显示数字没有变 x
# - miniwindow的layout更新后位置及大小出错问题 v
# - edit控件回车失效问题 v
# - 拖拽mini窗口后mini消失_dragging没有解除，需要再次在主窗口点击才能解除 v
# - 在animatedbutton类中添加font和(fixedsize)的stylesheet v
# - 双击和单击分离开 v
# - 长时间休眠后btn和label字体改变（添加每秒/从休眠中唤醒时 检测字体） （合盖之后仍存在问题） v
# - 拖拽时将不触发点击事件 v

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import win32api
import win32con
from datetime import datetime

from widgets import *
from ui.widget import Ui_Form 
from ui.palette import Palette
from utils import CrashHandler, Logger, get_work_date
from core import PairTimer, DataManager

_logger = Logger(__name__)


class Ui_MiniWindow:
    def setupUi(self, Form, *args):
        work_color, relax_color, bjtime_color = args

        # 控件初始化
        self.vlayout = QVBoxLayout()
        self.work_label = StylishLabel(Form, Palette.white, work_color, work_color)
        self.vlayout.addWidget(self.work_label)
        
        self.relax_label = StylishLabel(Form, Palette.white, relax_color, relax_color)
        self.vlayout.addWidget(self.relax_label)
        
        self.bjtime_label = StylishLabel(Form, Palette.white, bjtime_color, bjtime_color)
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
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint |
                            Qt.Tool |
                            Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowOpacity(0) # 设为全透明 
        self.set_opacity_startend(0.90, 0)
        self.setMouseTracking(True)
        for child in self.findChildren(QWidget):
            child.setMouseTracking(True)

        # 信号与槽
        work_signal.connect(self.on_worktime_update)
        relax_signal.connect(self.on_relaxtime_update)
        bjtime_signal.connect(self.on_bjtime_update)
    
    def enable_labels(self, enable: tuple):
        if enable[0]:
            self.work_label.show()
        else:
            self.work_label.hide()
        if enable[1]:
            self.relax_label.show()
        else:
            self.relax_label.hide()
        if enable[2]:
            self.bjtime_label.show()
        else:
            self.bjtime_label.hide()
            
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
        return super().on_fadingout(fading)

        
class WorkRelaxTimerWindow(FadeoutMixin, StylishFramelessWindow, Ui_Form):
    signal_worktime_update = pyqtSignal(str)
    signal_relaxtime_update = pyqtSignal(str)
    signal_bjtime_update = pyqtSignal(str)
    
    def __init__(self, crash_handler: CrashHandler = None, data_manager: DataManager = None):
        StylishFramelessWindow.__init__(self, clipped=True, outside_margin=3, inside_margin=3)
        FadeoutMixin.__init__(self, fade_when_idle = True)
        
        # 记录上次检查的工作日期
        self._last_check_date = get_work_date()
        
        # ui框架
        self.setupUi(self.form)
        self.work_button: PenetrateAnimatedButton
        self.relax_button: PenetrateAnimatedButton
        self.stop_button: PenetrateAnimatedButton
        self.clear_button: PenetrateAnimatedButton
        self.work_edit: PenetrateLineEdit
        self.relax_edit: PenetrateLineEdit
        
        # 设置按钮颜色
        self.work_button.set_bg_color(Palette.white, Palette.blue_light, Palette.blue)
        self.work_button.set_text_color(Palette.blue, Palette.blue_dark, Palette.white)
        
        self.relax_button.set_bg_color(Palette.white, Palette.orange_light, Palette.orange)
        self.relax_button.set_text_color(Palette.orange, Palette.orange_dark, Palette.white)
        
        self.stop_button.set_bg_color(Palette.white, Palette.green_light, Palette.green)
        self.stop_button.set_text_color(Palette.green, Palette.green_dark, Palette.white)
        
        self.clear_button.set_bg_color(Palette.white, Palette.red_light, Palette.red)
        self.clear_button.set_text_color(Palette.red, Palette.red_dark, Palette.white)
        self.clear_button.setText('clear')

        self.update_worktime(0)
        self.update_relaxtime(0)
        
        # 初始化计时器和数据管理器
        self.pair_timer = PairTimer()
        
        # 连接计时器信号
        self.pair_timer.work_timer_timeout.connect(self.update_worktime)
        self.pair_timer.relax_timer_timeout.connect(self.update_relaxtime)
        
        # 初始化mini窗口
        self.mini = MiniWindow(self, \
            Palette.blue, Palette.orange, Palette.green,\
            self.signal_worktime_update, self.signal_relaxtime_update, self.signal_bjtime_update)
        
        # 初始设置窗口大小、标题等
        self.setWindowTitle("WorkRelaxTimerWindow")
        minimum = self.minimumSizeHint()
        self.setGeometry(0, 0, minimum.width(), minimum.height())
        self.setWindowOpacity(0.9)
        self.set_opacity_startend(0.90, 0)
        self.setFocus()
        
        # 子控件事件连接
        self.work_button.singleClicked.connect(self.on_work_button_clicked)
        self.work_button.doubleClicked.connect(self.work_button.toggle)
        self.relax_button.singleClicked.connect(self.on_relax_button_clicked)
        self.relax_button.doubleClicked.connect(self.relax_button.toggle)
        self.stop_button.singleClicked.connect(self.on_stop_button_clicked)
        self.stop_button.doubleClicked.connect(self.stop_button.toggle)
        self.clear_button.singleClicked.connect(self.on_clear_button_clicked)
        self.clear_button.doubleClicked.connect(self.on_clear_button_doubleClicked)
        
        # 设置北京时间更新定时器
        self.bjtime_timer = QTimer(self)
        self.bjtime_timer.timeout.connect(self.update_bjtime)
        self.update_bjtime()
        self.bjtime_timer.start(1000)
        
        # 设置自检定时器
        self.self_check_timer = QTimer(self)
        self.self_check_timer.timeout.connect(self.self_check)
        self.self_check_timer.start(60*1000) # 60秒
        
        # 数据管理器
        self.data_manager = data_manager
        
        # 异常处理
        self.crash_handler = crash_handler
        if self.crash_handler:
            self.crash_handler.set_state_func(self.state_func)

        
    def _seconds_to_hms(self, seconds):
        # 使用 divmod 计算小时、分钟和秒数
        hours, remainder = divmod(seconds, 3600)  # 3600秒是1小时
        minutes, seconds = divmod(remainder, 60)  # 60秒是1分钟
        # 返回格式化后的字符串
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def on_work_button_clicked(self):
        add_segment = self.pair_timer.is_relax_active() and self.pair_timer.get_elapsed_time() > 100 * 1000 # 休息时间大于100秒则记录为休息
        segment_start_time = self.pair_timer.get_start_time()
        elapsed_time = self.pair_timer.get_elapsed_time() // 1000  # 转换为秒
        self.pair_timer.start_work()
        
        if add_segment and self.data_manager:
            self.data_manager.add_time_segment(
                start_time=segment_start_time,
                end_time=datetime.now(),
                work_time=self.pair_timer.get_work_time() // 1000,
                relax_time=self.pair_timer.get_relax_time() // 1000,
                is_work=False,
                elapsed_time=elapsed_time
            )
            
    def on_relax_button_clicked(self):
        add_segment = self.pair_timer.is_work_active() and self.pair_timer.get_elapsed_time() > 100 * 1000 # 工作时间大于100秒则记录为工作 
        segment_start_time = self.pair_timer.get_start_time()
        elapsed_time = self.pair_timer.get_elapsed_time() // 1000  # 转换为秒
        self.pair_timer.start_relax()
        
        if add_segment and self.data_manager:
            self.data_manager.add_time_segment(
                start_time=segment_start_time,
                end_time=datetime.now(),
                work_time=self.pair_timer.get_work_time() // 1000,
                relax_time=self.pair_timer.get_relax_time() // 1000,
                is_work=True,
                elapsed_time=elapsed_time
            )
    
    def on_stop_button_clicked(self):
        if self.pair_timer.is_work_active() and self.pair_timer.get_elapsed_time() > 100 * 1000:
            add_segment = 'work'
        elif self.pair_timer.is_relax_active() and self.pair_timer.get_elapsed_time() > 100 * 1000:
            add_segment = 'relax'
        else:
            add_segment = None
        segment_start_time = self.pair_timer.get_start_time()
        elapsed_time = self.pair_timer.get_elapsed_time() // 1000  # 转换为秒
        self.pair_timer.stop()
        
        if add_segment and self.data_manager:
            self.data_manager.add_time_segment(
                start_time=segment_start_time,
                end_time=datetime.now(),
                work_time=self.pair_timer.get_work_time() // 1000,
                relax_time=self.pair_timer.get_relax_time() // 1000,
                is_work=(add_segment == 'work'),
                elapsed_time=elapsed_time
            )

    def update_worktime(self, seconds: int):
        """更新卷时间显示"""
        work_time_hms = self._seconds_to_hms(seconds)
        self.work_button.setText(work_time_hms)
        self.signal_worktime_update.emit(work_time_hms)

    def update_relaxtime(self, seconds: int):
        """更新摆时间显示"""
        relax_time_hms = self._seconds_to_hms(seconds)
        self.relax_button.setText(relax_time_hms)
        self.signal_relaxtime_update.emit(relax_time_hms)
        
    def update_bjtime(self):
        """更新北京时间显示"""
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.stop_button.setText(current_time)
        self.signal_bjtime_update.emit(current_time)
        
        # 刷新一下各个按钮、label的样式
        self.stop_button.refresh_style()
        self.work_button.refresh_style()
        self.relax_button.refresh_style()
        self.mini.bjtime_label.refresh_style()
        self.mini.work_label.refresh_style()
        self.mini.relax_label.refresh_style()
        
        # 检查是否跨天
        current_work_date = get_work_date()
        if current_work_date != self._last_check_date:
            _logger.info(f"检测到日期变化(上次:{self._last_check_date}, 当前:{current_work_date})，重置计时器")
            self.pair_timer.reset()
            self.update_worktime(0)
            self.update_relaxtime(0)
            self._last_check_date = current_work_date
        
    def on_clear_button_clicked(self):
        self.pair_timer.clear()
        self.update_worktime(0)
        self.update_relaxtime(0)
    
    def on_clear_button_doubleClicked(self):
        # 双击清零退出
        self.on_stop_button_clicked()
        self.closeEvent(None)
    
    def editingFinishedEvent(self, event):
        try:
            work_suplement = int(self.work_edit.text())
            self.pair_timer.add_work_time(work_suplement * 60 * 1000)
        except:
            pass
        try:
            relax_suplement = int(self.relax_edit.text())
            self.pair_timer.add_relax_time(relax_suplement * 60 * 1000)
        except:
            pass
        self.update_worktime(self.pair_timer.get_work_time() // 1000)
        self.update_relaxtime(self.pair_timer.get_relax_time() // 1000)
        self.work_edit.setText('')
        self.relax_edit.setText('')
        
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
        QApplication.quit()  # 强制退出应用程序

    def on_fadingout(self, fading: bool):
        if fading:
            work_label_enabled = self.pair_timer.is_work_active() or self.work_button.toggled()
            relax_label_enabled = self.pair_timer.is_relax_active() or self.relax_button.toggled()
            bjtime_label_enabled = not self.pair_timer.is_work_active() and not self.pair_timer.is_relax_active() or self.stop_button.toggled()
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
        return super().on_fade_finished(faded)
    
    def state_func(self):
        return {
            'work': self.pair_timer.get_work_time() // 1000,
            'relax': self.pair_timer.get_relax_time() // 1000,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def self_check(self):
        """执行一些自检功能"""
        if self.crash_handler:
            self.crash_handler.save_app_state()
            
        if self.data_manager:
            self.data_manager.save_current_state(
                self.pair_timer.get_work_time() // 1000,
                self.pair_timer.get_relax_time() // 1000
            )
    
    def restore_from_state(self, state):
        """从状态恢复"""
        if state == None or state == {}:
            return True
        try:
            # 检查时间戳是否在同一个工作日
            saved_timestamp = datetime.strptime(state['timestamp'], '%Y-%m-%d %H:%M:%S')
            saved_work_date = get_work_date(saved_timestamp)
            current_work_date = get_work_date()
            
            if saved_work_date != current_work_date:
                _logger.info(f'状态({state["timestamp"]})不在当前工作日，跳过恢复')
                return False
                
            work_time = state['work'] * 1000  # 转换为毫秒
            relax_time = state['relax'] * 1000
            self.pair_timer._work_time = work_time
            self.pair_timer._relax_time = relax_time
            
            _logger.info(f'从状态恢复 - 工作时间: {work_time//1000}秒, 休息时间: {relax_time//1000}秒')
        except Exception as e:
            _logger.warning(f'恢复加载失败({state})')
            _logger.exception(e)
            return False
        self.update_worktime(work_time // 1000)
        self.update_relaxtime(relax_time // 1000)
        return True
    