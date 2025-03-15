import sys
from PyQt5.QtWidgets import QApplication
from view import WorkRelaxTimerWindow
from utils import CrashHandler, Logger
from core import DataManager

_logger = Logger(__name__)

# 主函数
if __name__ == "__main__":
    # 设置日志文件
    Logger.set_log_file_by_date()
    
    app = QApplication(sys.argv)
    
    # 初始化异常处理器
    crash_handler = CrashHandler()
    
    # 初始化数据管理器
    data_manager = DataManager(is_file_operations_disabled=crash_handler.is_file_operations_disabled())
    
    # 创建主窗口
    window = WorkRelaxTimerWindow(
        crash_handler=crash_handler,
        data_manager=data_manager
    )
    
    # 检查之前的崩溃状态
    previous_state = crash_handler.check_previous_crash()
    if previous_state:
        window.restore_from_state(previous_state)
    
    # 创建运行标志
    crash_handler.create_running_flag()
    
    # 显示窗口
    window.show()

    # 运行应用
    exit_code = app.exec_()
    
    # 程序退出时清理
    # crash_handler.clean_exit()
    sys.exit(exit_code)
