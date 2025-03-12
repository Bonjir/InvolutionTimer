
from utils import *

logger = Logger('test')
# 记录日志
logger.debug("调试信息（仅文件可见）")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")

exit(0)

import logging

# 创建Logger实例
logger = logging.getLogger("my_logger")  # 建议用模块名命名，如 __name__
logger.setLevel(logging.DEBUG)  # 设置日志级别（DEBUG及以上会记录）

# 创建Handler（控制台输出 + 文件输出）
console_handler = logging.StreamHandler()  # 控制台
file_handler = logging.FileHandler("app.log")  # 输出到文件

# 设置Handler的日志级别和格式
console_handler.setLevel(logging.INFO)  # 控制台只记录INFO及以上
file_handler.setLevel(logging.DEBUG)    # 文件记录所有DEBUG及以上

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将Handler添加到Logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 记录日志
logger.debug("调试信息（仅文件可见）")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")