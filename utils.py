import os
import json
import signal
import atexit
from pathlib import Path
import sys
from typing import Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal
import keyboard

APP_NAME = 'WorkRelaxTimer'

import logging

# 获取系统标准路径（兼容所有Windows版本）
_DATA_DIR = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / "Data"
# _DATA_FILE = _DATA_DIR / "data.json" 

# 确保目录存在
_DATA_DIR.mkdir(parents=True, exist_ok=True)


# 获取系统标准路径（兼容所有Windows版本）
_LOG_DIR = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / "Logs"
_LOG_FILE = _LOG_DIR / "log.log"    # 保存程序状态（如窗口尺寸、数据）

# 确保目录存在
_LOG_DIR.mkdir(parents=True, exist_ok=True)


# 创建Handler（控制台输出 + 文件输出）
_CONSOLE_LOG_HANDLER = logging.StreamHandler()  # 控制台
_FILE_LOG_HANDLER = logging.FileHandler(_LOG_FILE)  # 输出到文件

# 设置Handler的日志级别和格式
_CONSOLE_LOG_HANDLER.setLevel(logging.INFO)  # 控制台只记录INFO及以上
_FILE_LOG_HANDLER.setLevel(logging.DEBUG)    # 文件记录所有DEBUG及以上

_log_formatter = logging.Formatter(
    f"%(asctime)s - {os.getpid()} - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
_CONSOLE_LOG_HANDLER.setFormatter(_log_formatter)
_FILE_LOG_HANDLER.setFormatter(_log_formatter)

class Logger:
    _last_check_date = None  # 上次检查的日期
    
    @classmethod
    def check_and_rotate_log(cls):
        """检查是否需要切换日志文件（每天4点切换）"""
        from datetime import datetime, timedelta
        
        current_time = datetime.now()
        current_date = current_time.date()
        
        # 如果是第一次检查，记录当前日期
        if cls._last_check_date is None:
            cls._last_check_date = current_date
            return
            
        # 检查是否过了凌晨4点
        is_after_4am = current_time.hour >= 4
        is_previous_day = cls._last_check_date < current_date
        
        if is_previous_day and is_after_4am:
            # 切换到新的日志文件
            new_log_file = cls.set_log_file_by_date()
            _logger = logging.getLogger(__class__.__name__)
            _logger.info(f"日志文件已自动切换到: {new_log_file}")
            
            # 清理旧日志文件
            cls.clean_old_logs()
            
            # 更新检查日期
            cls._last_check_date = current_date
    
    @classmethod
    def clean_old_logs(cls, keep_days: int = 3):
        """清理指定天数之前的日志文件"""
        from datetime import datetime, timedelta
        
        # 获取当前日期
        current_date = datetime.now().date()
        
        # 遍历日志目录
        for log_file in _LOG_DIR.glob("*.log"):
            try:
                # 从文件名解析日期
                file_date = datetime.strptime(log_file.stem, "%Y-%m-%d").date()
                
                # 如果文件超过保留天数，则删除
                if (current_date - file_date).days > keep_days:
                    log_file.unlink()
                    _logger = logging.getLogger(__class__.__name__)
                    _logger.info(f"已删除旧日志文件: {log_file}")
            except (ValueError, OSError) as e:
                # 如果文件名不符合日期格式或删除失败，则跳过
                continue
    
    @classmethod
    def set_log_file_by_date(cls):
        """根据当前日期设置日志文件名"""
        from datetime import datetime
        current_date = datetime.now()
        log_file_name = f"{current_date.strftime('%Y-%m-%d')}.log"
        cls.set_log_file(log_file_name)
        return log_file_name
    
    @classmethod
    def set_log_file(cls, log_file_name: str):
        """
        设置新的日志文件路径
        Args:
            log_file_path: 新的日志文件路径
        """
        global _FILE_LOG_HANDLER
        global _LOG_DIR
        global _LOG_FILE
        
        # 确保目录存在
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        _LOG_FILE = _LOG_DIR / log_file_name

        # 创建新的文件处理器
        new_handler = logging.FileHandler(_LOG_FILE)
        new_handler.setLevel(logging.DEBUG)
        new_handler.setFormatter(_log_formatter)
        
        # 获取所有使用旧处理器的logger
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        
        # 替换所有logger中的旧处理器
        for logger in loggers:
            if _FILE_LOG_HANDLER in logger.handlers:
                logger.removeHandler(_FILE_LOG_HANDLER)
                logger.addHandler(new_handler)
        
        # 关闭旧的处理器
        _FILE_LOG_HANDLER.close()
        
        # 更新全局处理器
        _FILE_LOG_HANDLER = new_handler
        
    @staticmethod
    def auto_check(func):
        """装饰器：在调用日志函数前检查是否需要切换日志文件"""
        def wrapper(self, *args, **kwargs):
            Logger.check_and_rotate_log()
            return func(self, *args, **kwargs)
        return wrapper
    
    def __init__(self, module_name = APP_NAME):
        global _CONSOLE_LOG_HANDLER
        global _FILE_LOG_HANDLER
        # 创建Logger实例
        self.logger = logging.getLogger(module_name)  # 建议用模块名命名，如 __name__
        self.logger.setLevel(logging.DEBUG)  # 设置日志级别（DEBUG及以上会记录）

        # 将Handler添加到Logger
        self.logger.addHandler( _CONSOLE_LOG_HANDLER )
        self.logger.addHandler( _FILE_LOG_HANDLER )

        pass
    
    def prompt(self, msg, *args, **kwargs):
        print(msg, *args, **kwargs)
        
    # 代理所有日志方法到 self.logger，并添加自动检查装饰器
    @auto_check
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    @auto_check
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    @auto_check
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    @auto_check
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    @auto_check
    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    @auto_check
    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

_logger = Logger(__name__)


class GlobalHotkey(QObject):
    """基础快捷键类"""
    triggered = pyqtSignal()  # 基础触发信号
    
    def __init__(self, key_sequence: str):
        super().__init__()
        self._logger = Logger(__class__.__name__)
        self._key_sequence = key_sequence
        self._registered = False
        self._register()
    
    def _register(self):
        """注册快捷键"""
        try:
            keyboard.add_hotkey(self._key_sequence, self.triggered.emit)
            self._registered = True
            self._logger.info(f"成功注册快捷键: {self._key_sequence}")
        except Exception as e:
            self._logger.error(f"注册快捷键 {self._key_sequence} 失败: {e}")
            
    def unregister(self):
        """注销快捷键"""
        if self._registered:
            try:
                keyboard.remove_hotkey(self._key_sequence)
                self._registered = False
                self._logger.info(f"成功注销快捷键: {self._key_sequence}")
            except Exception as e:
                self._logger.error(f"注销快捷键 {self._key_sequence} 失败: {e}")
                
    def __del__(self):
        """析构函数，确保注销快捷键"""
        self.unregister()
        
    def reset_hotkey(self):
        """检查快捷键是否失效，如果失效则尝试重新注册"""
        if not self._registered:
            return False
        
        try:
            keyboard.remove_hotkey(self._key_sequence)
            self._registered = False
        except Exception as e:
            self._logger.error(f"检查到快捷键 {self._key_sequence} 失效: {e}")
            
        try:
            keyboard.add_hotkey(self._key_sequence, self.triggered.emit)
            self._registered = True
            self._logger.info(f"重新注册快捷键: {self._key_sequence}")
        except Exception as e:
            self._logger.error(f"重新注册快捷键 {self._key_sequence} 失败: {e}")
            
        return self._registered
    
from datetime import datetime, timedelta, date

def get_work_date(target_time: datetime = None) -> date:
    """
    获取工作日期（4点前算作前一天）
    Args:
        target_time: 目标时间，默认为当前时间
    Returns:
        工作日期
    """
    if target_time is None:
        target_time = datetime.now()
        
    # 如果小于4点，日期要减一天
    if target_time.hour < 4:
        return (target_time - timedelta(days=1)).date()
    return target_time.date()

class CrashHandler:
    def __init__(self):
        
        # 获取系统标准路径（兼容所有Windows版本）
        self.APP_NAME = APP_NAME
        self.STATE_DIR = Path(os.getenv('LOCALAPPDATA')) / self.APP_NAME / "State"
        self.STATE_FILE = self.STATE_DIR / "app_state.json"    # 保存程序状态（如窗口尺寸、数据）
        self.FLAG_FILE = self.STATE_DIR / "running.flag"       # 运行标志文件

        # 确保目录存在
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)

        # 注册退出处理
        atexit.register(self.clean_exit)
        
        # 设置全局异常钩子
        sys.excepthook = self._handle_exception

        # 捕获常见终止信号
        signal.signal(signal.SIGINT, self._handle_signal)   # Ctrl+C
        signal.signal(signal.SIGTERM, self._handle_signal)  # 终止进程

        # 设置允许更改的app状态函数
        self.state_func = lambda : {'state_func':'unset'}
        
        # 标记是否禁用写入文件操作
        self.file_operations_disabled = False
        
    def get_last_state(self) -> Optional[Dict]:
        """
        读取上一次保存的状态
        Returns:
            Dict: 状态数据，如果文件不存在或读取失败则返回None
        """
            
        try:
            if self.STATE_FILE.exists():
                with open(self.STATE_FILE, 'r') as f:
                    state = json.load(f)
                    _logger.debug(f"读取上次状态: {state}")
                    return state
        except Exception as e:
            _logger.error(f"读取状态文件失败: {e}")
        return None
    
    def _is_process_running(self, pid):
        """检查指定PID的进程是否在运行"""
        try:
            import psutil
            return psutil.pid_exists(pid)
        except ImportError:
            # 如果没有psutil，使用os模块（仅适用于Unix系统）
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
    
    def check_previous_crash(self):
        """检查是否存在之前的崩溃，并检查是否有其他实例在运行"""
        if self.FLAG_FILE.exists():
            try:
                # 读取FLAG文件中的PID
                with open(self.FLAG_FILE, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # 检查该PID是否仍在运行
                if self._is_process_running(old_pid):
                    _logger.warning(f"检测到另一个实例正在运行(PID: {old_pid})，禁用文件写入...")
                    self.file_operations_disabled = True
                    # return None # 如果仍在运行也恢复
                else:
                    _logger.info("检测到上次未正常退出，尝试恢复...")
                    # 这里没删是因为这是标准的flag文件检测流程
                    # 执行恢复操作
                    try:
                        with open(self.STATE_FILE, 'r') as f:
                            saved_state = json.load(f)
                            _logger.info(f"恢复状态:{saved_state}")
                        return saved_state
                    except json.JSONDecodeError:
                        _logger.error("状态文件损坏，使用默认配置")
                        return None
            except (ValueError, OSError) as e:
                _logger.error(f"读取PID出错: {e}")
                self.FLAG_FILE.unlink(missing_ok=True)
        
        # flag文件存在也恢复
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, 'r') as f:
                    saved_state = json.load(f)
                    _logger.info(f"读取状态:{saved_state}")
                return saved_state
            except json.JSONDecodeError:
                _logger.error("状态文件损坏，使用默认配置")
                return None
            except Exception as e:
                _logger.exception(f"读取状态文件失败: {e}")
                return None
        

    def is_file_operations_disabled(self):
        return self.file_operations_disabled
    
    def set_state_func(self, state_func):
        self.state_func = state_func
    
    def save_app_state(self):
        """保存程序状态"""
        if self.file_operations_disabled:
            _logger.debug("文件操作已禁用，跳过状态保存")
            return
            
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.state_func(), f)

    def create_running_flag(self):
        """创建运行标志文件"""
        if self.file_operations_disabled:
            _logger.debug("文件操作已禁用，跳过创建运行标志")
            return
            
        with open(self.FLAG_FILE, 'w') as f:
            f.write(str(os.getpid()))
    
    def clean_exit(self):
        """正常退出时的清理操作"""
        _logger.info("标准退出")
        if not self.file_operations_disabled and self.FLAG_FILE.exists():
            _logger.info("清理运行标志文件")
            try:
                self.FLAG_FILE.unlink()
            except (ValueError, OSError):
                # 如果读取失败，为安全起见不删除文件
                pass

    def _handle_exception(self, exc_type, exc_value, traceback):
        """全局异常处理"""
        _logger.exception(f"捕获异常: {exc_type}: {exc_value}\n{traceback}")
        if not self.file_operations_disabled:
            self.save_app_state()  # 紧急保存状态
        self.clean_exit()      # 清理标志文件
        sys.__excepthook__(exc_type, exc_value, traceback)
    
    def _handle_signal(self, signum, frame):
        """处理系统信号（如Ctrl+C）"""
        _logger.info(f"接收信号 {signum}, frame:{frame}，执行清理...")
        if not self.file_operations_disabled:
            self.save_app_state()
        self.clean_exit()
        sys.exit(0)
