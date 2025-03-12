import os
import json
import signal
import atexit
from pathlib import Path

# 获取系统标准路径（兼容所有Windows版本）
APP_NAME = "WorkRelaxTimer"
STATE_DIR = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / "State"
STATE_FILE = STATE_DIR / "app_state.json"    # 保存程序状态（如窗口尺寸、数据）
FLAG_FILE = STATE_DIR / "running.flag"       # 运行标志文件

# 确保目录存在
STATE_DIR.mkdir(parents=True, exist_ok=True)

def check_previous_crash():
    """检测上次是否异常退出"""
    if FLAG_FILE.exists():
        print("检测到上次未正常退出，尝试恢复...")
        return True
    return False

# 程序启动时立即检查
if check_previous_crash():
    # 执行恢复操作（例如加载 STATE_FILE）
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                saved_state = json.load(f)
                print("恢复状态:", saved_state)
        except json.JSONDecodeError:
            print("状态文件损坏，使用默认配置")
            
            
def create_running_flag():
    """创建运行标志文件"""
    with open(FLAG_FILE, 'w') as f:
        f.write(str(os.getpid()))  # 可选：写入进程ID用于高级检查

# 程序启动后立即创建标志
create_running_flag()

def clean_exit():
    """正常退出时的清理操作"""
    if FLAG_FILE.exists():
        FLAG_FILE.unlink()
    print("程序正常退出")

# 注册退出处理
atexit.register(clean_exit)


import sys
def save_app_state():
    """保存程序状态（根据实际需求定制）"""
    current_state = {
        "window_size": [800, 600],
        "last_file": "/path/to/latest.doc",
        "user_prefs": {"theme": "dark"}
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(current_state, f)

def handle_exception(exc_type, exc_value, traceback):
    """全局异常处理"""
    print(f"捕获异常: {exc_value}")
    save_app_state()  # 紧急保存状态
    clean_exit()      # 清理标志文件
    sys.__excepthook__(exc_type, exc_value, traceback)

# 设置全局异常钩子
sys.excepthook = handle_exception

# 示例：手动保存状态（如定时保存/关键操作后）
save_app_state()


def handle_signal(signum, frame):
    """处理系统信号（如Ctrl+C）"""
    print(f"接收信号 {signum}, frame:{frame}，执行清理...")
    save_app_state()
    clean_exit()
    sys.exit(0)

# 捕获常见终止信号
signal.signal(signal.SIGINT, handle_signal)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_signal)  # 终止进程

while True:
    pass