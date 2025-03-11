import os
import json
import signal
import atexit
from pathlib import Path
import sys


class CrashHandler:
    def __init__(self, appname:str = 'test'):
        
        # 获取系统标准路径（兼容所有Windows版本）
        self.APP_NAME = appname
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
            print("检测到上次未正常退出，尝试恢复...")
            # 执行恢复操作（例如加载 STATE_FILE）
            try:
                with open(self.STATE_FILE, 'r') as f:
                    saved_state = json.load(f)
                    print("恢复状态:", saved_state)
                return saved_state
            except json.JSONDecodeError:
                print("状态文件损坏，使用默认配置")
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
        print(f"捕获异常: {exc_value}")
        self.save_app_state()  # 紧急保存状态
        self.clean_exit()      # 清理标志文件
        sys.__excepthook__(exc_type, exc_value, traceback)

    
    def _handle_signal(self, signum, frame):
        """处理系统信号（如Ctrl+C）"""
        print(f"接收信号 {signum}, frame:{frame}，执行清理...")
        self.save_app_state()
        self.clean_exit()
        sys.exit(0)
