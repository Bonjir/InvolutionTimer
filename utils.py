import os
import json
import signal
import atexit
from pathlib import Path
import sys

APP_NAME = 'WorkRelaxTimer'

import logging

# 获取系统标准路径（兼容所有Windows版本）
__LOG_DIR = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / "Logs"
__LOG_FILE = __LOG_DIR / "log.log"    # 保存程序状态（如窗口尺寸、数据）

# 确保目录存在
__LOG_DIR.mkdir(parents=True, exist_ok=True)

# 创建Handler（控制台输出 + 文件输出）
_CONSOLE_LOG_HANDLER = logging.StreamHandler()  # 控制台
_FILE_LOG_HANDLER = logging.FileHandler(__LOG_FILE)  # 输出到文件

# 设置Handler的日志级别和格式
_CONSOLE_LOG_HANDLER.setLevel(logging.INFO)  # 控制台只记录INFO及以上
_FILE_LOG_HANDLER.setLevel(logging.DEBUG)    # 文件记录所有DEBUG及以上

__log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
_CONSOLE_LOG_HANDLER.setFormatter(__log_formatter)
_FILE_LOG_HANDLER.setFormatter(__log_formatter)

class Logger:
    
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
    
    # 代理所有日志方法到 self.logger
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

_logger = Logger(__name__)
        
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
        
        pass
    
    def check_previous_crash(self):
        # 程序启动时立即检查
        if self.FLAG_FILE.exists():
            _logger.info("检测到上次未正常退出，尝试恢复...")
            # 执行恢复操作（例如加载 STATE_FILE）
            try:
                with open(self.STATE_FILE, 'r') as f:
                    saved_state = json.load(f)
                    _logger.info(f"恢复状态:{saved_state}")
                return saved_state
            except json.JSONDecodeError:
                _logger.error("状态文件损坏，使用默认配置")
        return None

    def set_state_func(self, state_func):
        self.state_func = state_func
    
    def save_app_state(self):
        """保存程序状态（根据实际需求定制）"""
        # current_state = {
        #     "window_size": [800, 600],
        #     "last_file": "/path/to/latest.doc",
        #     "user_prefs": {"theme": "dark"}
        # }
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.state_func(), f)

    def create_running_flag(self):
        """创建运行标志文件"""
        with open(self.FLAG_FILE, 'w') as f:
            f.write(str(os.getpid()))  # 可选：写入进程ID用于高级检查
    
    def clean_exit(self):
        """正常退出时的清理操作"""
        if self.FLAG_FILE.exists():
            self.FLAG_FILE.unlink()
        # print("程序正常退出")

    def _handle_exception(self, exc_type, exc_value, traceback):
        """全局异常处理"""
        _logger.warning(f"捕获异常: {exc_value}")
        self.save_app_state()  # 紧急保存状态
        self.clean_exit()      # 清理标志文件
        sys.__excepthook__(exc_type, exc_value, traceback)

    
    def _handle_signal(self, signum, frame):
        """处理系统信号（如Ctrl+C）"""
        _logger.info(f"接收信号 {signum}, frame:{frame}，执行清理...")
        self.save_app_state()
        self.clean_exit()
        sys.exit(0)

