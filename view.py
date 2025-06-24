import random
import sys
import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import win32api
import win32con
from datetime import datetime, timedelta
from system_hotkey import SystemHotkey

from widgets import *
from ui.widget import Ui_Form 
from ui.palette import Palette, get_theme_colors
from utils import CrashHandler, Logger, get_work_date, _LOG_DIR, _DATA_DIR
from core import PairTimer, DataManager
from utils import HotkeyHandler, _KeyBoard_Hotkey

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
        self.work_label:StylishLabel
        self.relax_label:StylishLabel
        self.bjtime_label:StylishLabel
        
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
        # self._last_check_date = get_work_date()
        self._last_check_timestamp = datetime.now()
        
        # ui框架
        self.setupUi(self.form)
        self.work_button: PenetrateAnimatedButton
        self.relax_button: PenetrateAnimatedButton
        self.stop_button: PenetrateAnimatedButton
        self.clear_button: PenetrateAnimatedButton
        self.work_edit: PenetrateLineEdit
        self.relax_edit: PenetrateLineEdit
        
        # 设置按钮颜色
        # self.work_button.set_bg_color(Palette.white, Palette.blue_light, Palette.blue)
        # self.work_button.set_text_color(Palette.blue, Palette.blue_dark, Palette.white)
        
        # self.relax_button.set_bg_color(Palette.white, Palette.orange_light, Palette.orange)
        # self.relax_button.set_text_color(Palette.orange, Palette.orange_dark, Palette.white)
        
        # self.stop_button.set_bg_color(Palette.white, Palette.green_light, Palette.green)
        # self.stop_button.set_text_color(Palette.green, Palette.green_dark, Palette.white)
        
        # self.clear_button.set_bg_color(Palette.white, Palette.red_light, Palette.red)
        # self.clear_button.set_text_color(Palette.red, Palette.red_dark, Palette.white)
        
        self.work_button.set_theme_color(Palette.blue)
        self.relax_button.set_theme_color(Palette.orange)
        self.stop_button.set_theme_color(Palette.green)
        self.clear_button.set_theme_color(Palette.red)
        
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
            
        # 初始化右键菜单
        self.context_menu_manager = ContextMenuManager(self)
        
        # 为主窗口和各个控件添加右键菜单
        self.context_menu_manager.create_menu_for_widget(self.form)
        self.context_menu_manager.create_menu_for_widget(self.work_edit)
        self.context_menu_manager.create_menu_for_widget(self.relax_edit)
        
        # 初始化热键
        self.hotkey_handler = HotkeyHandler()
        self.hotkey_handler.register_hotkey('<ctrl>+<alt>+1', self.on_work_shortcut_activated)
        self.hotkey_handler.register_hotkey('<ctrl>+<alt>+2', self.on_relax_shortcut_activated)
        self.hotkey_handler.register_hotkey('<ctrl>+<alt>+3', self.on_stop_shortcut_activated)
        self.hotkey_handler.start_listener()
        
        
        # debug for keyboard hotkey
        self._work_hotkey = _KeyBoard_Hotkey('ctrl+alt+1')
        self._work_hotkey.triggered.connect(self._debug_on_work_hotkey_keyboard_triggered)
        self._relax_hotkey = _KeyBoard_Hotkey('ctrl+alt+2')
        self._relax_hotkey.triggered.connect(self._debug_on_relax_hotkey_keyboard_triggered)
        self._stop_hotkey = _KeyBoard_Hotkey('ctrl+alt+3')
        self._stop_hotkey.triggered.connect(self._debug_on_stop_hotkey_keyboard_triggered)

    def _debug_on_work_hotkey_keyboard_triggered(self):
        _logger.info("keyboard- 快捷键触发 - 工作模式")
        
    def _debug_on_relax_hotkey_keyboard_triggered(self):
        _logger.info("keyboard- 快捷键触发 - 放松模式")
        
    def _debug_on_stop_hotkey_keyboard_triggered(self):
        _logger.info("keyboard- 快捷键触发 - 停止模式")
        
        
    def on_work_shortcut_activated(self):
        self.try_fadeout_animation(False)
        self.mini.try_fadeout_animation(True)
        self.on_work_button_clicked()
        self.work_button.twinkle()
        _logger.info("快捷键触发 - 工作模式")

    def on_relax_shortcut_activated(self):
        self.try_fadeout_animation(False)
        self.mini.try_fadeout_animation(True)
        self.on_relax_button_clicked()
        self.relax_button.twinkle()
        _logger.info("快捷键触发 - 放松模式")
        
    def on_stop_shortcut_activated(self):
        self.try_fadeout_animation(False)
        self.mini.try_fadeout_animation(True)
        self.on_stop_button_clicked()
        self.stop_button.twinkle()
        _logger.info("快捷键触发 - 停止模式")

    def _seconds_to_hms(self, seconds):
        # 使用 divmod 计算小时、分钟和秒数
        hours, remainder = divmod(seconds, 3600)  # 3600秒是1小时
        minutes, seconds = divmod(remainder, 60)  # 60秒是1分钟
        # 返回格式化后的字符串
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def on_work_button_clicked(self):
        try:
            _logger.debug(f'on_work_button_clicked')
            add_segment = self.pair_timer.is_relax_active() and self.pair_timer.get_elapsed_time() > 100  # 休息时间大于100秒则记录为休息
            segment_start_time = self.pair_timer.get_start_time()
            elapsed_time = self.pair_timer.get_elapsed_time()  # 已经是秒
            self.pair_timer.start_work()
            
            if add_segment and self.data_manager:
                self.data_manager.add_time_segment(
                    start_time=segment_start_time,
                    end_time=datetime.now(),
                    work_time=self.pair_timer.get_work_time(),
                    relax_time=self.pair_timer.get_relax_time(),
                    is_work=False,
                    elapsed_time=elapsed_time
                )
        except Exception as e:
            _logger.exception(e)
            
    def on_relax_button_clicked(self):
        try:
            _logger.debug(f'on_relax_button_clicked')
            add_segment = self.pair_timer.is_work_active() and self.pair_timer.get_elapsed_time() > 100  # 工作时间大于100秒则记录为工作 
            segment_start_time = self.pair_timer.get_start_time()
            elapsed_time = self.pair_timer.get_elapsed_time()  # 已经是秒
            self.pair_timer.start_relax()
            
            if add_segment and self.data_manager:
                self.data_manager.add_time_segment(
                    start_time=segment_start_time,
                    end_time=datetime.now(),
                    work_time=self.pair_timer.get_work_time(),
                    relax_time=self.pair_timer.get_relax_time(),
                    is_work=True,
                    elapsed_time=elapsed_time
                )
        except Exception as e:
            _logger.exception(e)
    
    def on_stop_button_clicked(self):
        try:
            _logger.debug(f'on_stop_button_clicked')
            if self.pair_timer.is_work_active() and self.pair_timer.get_elapsed_time() > 100:
                add_segment = 'work'
            elif self.pair_timer.is_relax_active() and self.pair_timer.get_elapsed_time() > 100:
                add_segment = 'relax'
            else:
                add_segment = None
            segment_start_time = self.pair_timer.get_start_time()
            elapsed_time = self.pair_timer.get_elapsed_time()  # 已经是秒
            self.pair_timer.stop()
            
            if add_segment and self.data_manager:
                self.data_manager.add_time_segment(
                    start_time=segment_start_time,
                    end_time=datetime.now(),
                    work_time=self.pair_timer.get_work_time(),
                    relax_time=self.pair_timer.get_relax_time(),
                    is_work=(add_segment == 'work'),
                    elapsed_time=elapsed_time
                )
        except Exception as e:
            _logger.exception(e)

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
        last_check_date = get_work_date(self._last_check_timestamp)
        if current_work_date != last_check_date:
            # 如果跨天时计时器仍在运行，则利用datamanager添加昨天最后一条记录
            _logger.info(f"检测到日期变化(上次:{last_check_date}, 当前:{current_work_date})，重置计时器")
            if self.pair_timer.is_any_active():
                self.data_manager.add_time_segment(
                    start_time=self.pair_timer.get_start_time(),
                    end_time=self._last_check_timestamp,
                    work_time=self.pair_timer.get_work_time(),
                    relax_time=self.pair_timer.get_relax_time(),
                    is_work=self.pair_timer.is_work_active(),
                    elapsed_time=self.pair_timer.get_elapsed_time()
                )
                _logger.info(f"添加昨天最后一条记录")
            self.pair_timer.reset()
            self.update_worktime(0)
            self.update_relaxtime(0)
            
        self._last_check_timestamp = datetime.now() # 更新检查时间戳 要在添加记录的外面
            
    def on_clear_button_clicked(self):
        try:
            _logger.debug(f'on_clear_button_clicked')
            self.pair_timer.clear()
            self.update_worktime(0)
            self.update_relaxtime(0)
        except Exception as e:
            _logger.exception(e)
    
    def on_clear_button_doubleClicked(self):
        # 双击清零退出
        self.on_stop_button_clicked()
        self.closeEvent(None)
    
    def editingFinishedEvent(self, event):
        try:
            work_suplement = int(self.work_edit.text())
        except:
            try:
                text = self.work_edit.text()
                # 去掉text中所有字母
                text = re.sub(r'[a-zA-Z]', '', text)
                work_suplement = int(eval(text))
            except:
                work_suplement = 0
        try:
            relax_suplement = int(self.relax_edit.text())
        except:
            try:
                text = self.relax_edit.text()
                text = re.sub(r'[a-zA-Z]', '', text)
                relax_suplement = int(eval(text))
            except:
                relax_suplement = 0
        self.pair_timer.add_work_time(work_suplement * 60)  # 转换为秒
        self.pair_timer.add_relax_time(relax_suplement * 60)  # 转换为秒
        self.update_worktime(self.pair_timer.get_work_time())
        self.update_relaxtime(self.pair_timer.get_relax_time())
        self.work_edit.setText('')
        self.relax_edit.setText('')
        _logger.info(f'手动添加工作时间: {work_suplement}分, 休息时间: {relax_suplement}分, 当前工作时间: {self.pair_timer.get_work_time()}秒, 当前休息时间: {self.pair_timer.get_relax_time()}秒')
        
        
    # def showEvent(self, a0):
    #     # 模拟点击消除掉tool窗口首次press的延迟 # 似乎并不需要
    #     def simulate_click():
    #         # 获取窗口的位置
    #         initial_pos = self.pos()
    #         cursorpos = QCursor.pos()
    #         # win32api模拟点击
    #         win32api.SetCursorPos((initial_pos.x() + 5, initial_pos.y() + 5))
    #         win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    #         win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    #         win32api.SetCursorPos((cursorpos.x(), cursorpos.y()))
    #     QTimer.singleShot(0, simulate_click)
    #     return super().showEvent(a0)
    
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
            self.mini._start_fadeout_animation(fading=False)
            
        else:
            self.mini._start_fadeout_animation(fading=True)
            
        return super().on_fadingout(fading)
    
    def on_fade_finished(self, faded):
        return super().on_fade_finished(faded)
    
    def state_func(self):
        return {
            'work': self.pair_timer.get_work_time(),
            'relax': self.pair_timer.get_relax_time(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def self_check(self):
        """执行一些自检功能"""
        if self.crash_handler:
            self.crash_handler.save_app_state()
            
        if self.data_manager:
            self.data_manager.save_current_state(
                self.pair_timer.get_work_time(),
                self.pair_timer.get_relax_time()
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
                
            work_time = state['work']  # 已经是秒
            relax_time = state['relax']  # 已经是秒
            self.pair_timer._work_time = work_time
            self.pair_timer._relax_time = relax_time
            
            _logger.info(f'从状态恢复 - 工作时间: {work_time}秒, 休息时间: {relax_time}秒')
        except Exception as e:
            _logger.warning(f'恢复加载失败({state})')
            _logger.exception(e)
            return False
        self.update_worktime(work_time)
        self.update_relaxtime(relax_time)
        return True
    
    def mousePressEvent(self, event):
        # 更新最后活动时间
        self.last_activity_time = QDateTime.currentDateTime()
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        # 更新最后活动时间 
        self.last_activity_time = QDateTime.currentDateTime()
        return super().mouseMoveEvent(event)
        
    def keyPressEvent(self, event):
        # 更新最后活动时间
        self.last_activity_time = QDateTime.currentDateTime()
        return super().keyPressEvent(event)


class ContextMenuManager:
    """右键菜单管理器，用于为控件添加右键菜单"""
    
    def __init__(self, parent):
        self.parent : WorkRelaxTimerWindow
        self.parent = parent
        
    def create_menu_for_widget(self, widget):
        """为指定控件创建右键菜单，所有控件使用统一的菜单"""
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(
            lambda pos: self.show_unified_menu(widget, pos))
            
    def _create_base_menu(self, parent):
        """创建基本菜单"""
        menu = AnimatedMenu(parent, fade_when_idle=True)
        menu.set_opacity_startend(0.95, 0.0)
        
        # 使用灰色主题
        bg_color = Palette.white
        text_color = Palette.gray 
        highlight_bg = Palette.gray_light.lighter(120)
        highlight_text = Palette.gray_dark
        menu.set_theme(bg_color, text_color, highlight_bg, highlight_text)
        
        return menu
            
    def show_unified_menu(self, widget, pos):
        """显示统一的右键菜单"""
        
        # 随机主题颜色
        random_theme_color = random.choice([Palette.red, Palette.green, Palette.blue, Palette.orange, Palette.gray])
        theme_color, theme_color_light, theme_color_dark = get_theme_colors(random_theme_color)
        
        menu = self._create_base_menu(self.parent)
        menu.set_theme(Palette.white, theme_color, theme_color_light.lighter(120), theme_color_dark.darker(120))
        
        # 添加菜单项
        menu.add_styled_action("保存当前状态", lambda: self.parent.self_check())
        
        # 文件访问菜单
        files_menu = self._create_base_menu(self.parent)
        files_menu.add_styled_action("打开日志文件", lambda: self.open_log_file())
        files_menu.add_styled_action("打开数据文件", lambda: self.open_data_file())
        files_menu.set_theme(Palette.white, theme_color, theme_color_light.lighter(120), theme_color_dark)
        
        files_action = QAction("文件访问", menu)
        files_action.setMenu(files_menu)
        menu.addAction(files_action)
        
        # 设置相关选项
        settings_menu = self._create_base_menu(self.parent)
        settings_menu.add_styled_action("置顶窗口", lambda: self.toggle_window_on_top())
        settings_menu.add_styled_action("调整透明度", lambda: self.adjust_opacity())
        settings_menu.add_styled_action("显示/隐藏迷你窗口", lambda: self.toggle_mini_window())
        # settings_menu.add_styled_action("重置界面位置", lambda: self.reset_ui())
        settings_menu.set_theme(Palette.white, theme_color, theme_color_light.lighter(120), theme_color_dark)
        # 使菜单互相关联
        settings_menu.add_related_fadeout_widget(menu)
        menu.add_related_fadeout_widget(settings_menu)
        
        settings_action = QAction("设置", menu)
        settings_action.setMenu(settings_menu)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        menu.add_styled_action("退出", lambda: self.parent.closeEvent(None))
        
        # 显示菜单
        menu.exec_(widget.mapToGlobal(pos))
        
    # 菜单项功能实现
    def toggle_window_on_top(self):
        """切换窗口置顶状态"""
        flags = self.parent.windowFlags()
        if flags & Qt.WindowStaysOnTopHint:
            self.parent.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
            _logger.info("窗口取消置顶")
        else:
            self.parent.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
            _logger.info("窗口置顶")
        self.parent.show()
        
    def adjust_opacity(self):
        """调整窗口透明度"""
        # 简单实现，实际应用中可能需要显示一个滑块供用户调整
        current = self.parent.windowOpacity()
        if current > 0.7:
            self.parent.setWindowOpacity(0.7)
            self.parent.set_opacity_startend(0.7, 0)
            self.parent.mini.setWindowOpacity(0.7)
            self.parent.mini.set_opacity_startend(0.7, 0)
        else:
            self.parent.setWindowOpacity(0.9)
            self.parent.set_opacity_startend(0.9, 0)
            self.parent.mini.setWindowOpacity(0.9)
            self.parent.mini.set_opacity_startend(0.9, 0)
        

    def toggle_mini_window(self):
        """显示/隐藏迷你窗口"""
        self.parent.try_fadeout_animation(True)
            
    # def reset_ui(self):
    #     """重置界面位置和大小"""
    #     # 获取屏幕中心位置
    #     screen = QApplication.primaryScreen().availableGeometry()
    #     size = self.parent.size()
    #     x = int((screen.width() - size.width()) / 2)
    #     y = int((screen.height() - size.height()) / 2)
    #     self.parent.move(x, y)
    #     _logger.info("重置界面位置")
    
    def open_log_file(self):
        """打开日志文件所在目录"""
        import os
        import subprocess
        
        # 获取日志文件目录
        log_dir = _LOG_DIR
        
        if os.path.exists(log_dir):
            _logger.info(f"打开日志文件目录: {log_dir}")
            # 使用 Windows 资源管理器打开目录
            subprocess.run(['explorer', log_dir])
        else:
            _logger.warning(f"日志文件目录不存在: {log_dir}")
    
    def open_data_file(self):
        """打开数据文件所在目录"""
        import os
        import subprocess
        
        # 获取数据文件目录
        data_dir = _DATA_DIR
        
        if os.path.exists(data_dir):
            _logger.info(f"打开数据文件目录: {data_dir}")
            # 使用 Windows 资源管理器打开目录
            subprocess.run(['explorer', data_dir])
        else:
            _logger.warning(f"数据文件目录不存在: {data_dir}")