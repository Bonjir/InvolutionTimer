# ————————————————————————————————————————————————————

from pathlib import Path
import os

APP_NAME = 'WorkRelaxTimer'

_DATA_DIR = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / "Data"
        
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

# ————————————————————————————————————————————————————

import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QScrollArea)
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt

# ================= 可配置参数 =================
VISUAL_CONFIG = {
    'DAYS_SHOW': 7, # 显示的天数
    'HOUR_PIXELS': int(80 * 24 / 20),         # 每小时占用的像素宽度
    'LEFT_MARGIN': 120,        # 左侧边距
    'BLOCK_HEIGHT': 40,        # 时间段块高度 x
    'TIME_FONT_SIZE': 10,      # 时间文字大小
    'SEGMENT_FONT_SIZE': 5,    # 区块文字大小
    'HEADER_FONT_SIZE': 10,    # 头部文字大小
    'HEADER_MARGIN': 30,       # 头部时间与头部文字的距离
    'START_TIME': 8,           # 起始时间
    'AXIS_LINE_COLOR': QColor(150, 150, 150),
    'WORK_COLOR': QColor(70, 130, 180),     # 工作颜色
    'REST_COLOR': QColor(144, 238, 144),    # 休息颜色
    'BACKGROUND_COLOR': QColor(245, 245, 245)  # 背景色
}
# =============================================

class DailySchedule(QWidget):
    def __init__(self, date, day_data):
        super().__init__()
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.day_data = day_data
        
        # 计算控件宽度（24小时 * 每小时像素 + 左边距）
        self.total_width = VISUAL_CONFIG['LEFT_MARGIN'] + 24 * VISUAL_CONFIG['HOUR_PIXELS']
        self.setMinimumSize(self.total_width, 220)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), VISUAL_CONFIG['BACKGROUND_COLOR'])
        self.setPalette(palette)
        
        self.time_font = QFont('Arial', VISUAL_CONFIG['TIME_FONT_SIZE'])
        self.header_font = QFont('Arial', VISUAL_CONFIG['HEADER_FONT_SIZE'], QFont.Bold)
        self.segment_font = QFont('Arial', VISUAL_CONFIG['SEGMENT_FONT_SIZE'])
        self.setFont(self.time_font)
        
        self.header_margin = VISUAL_CONFIG['HEADER_MARGIN']
        self.block_height = VISUAL_CONFIG['BLOCK_HEIGHT']
        
        self.start_time = VISUAL_CONFIG['START_TIME']

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_header(painter)
        self.draw_time_axis(painter)
        self.draw_segments(painter)

    def draw_header(self, painter): 
        painter.setFont(self.header_font)
        header = (f"{self.date.strftime('%Y-%m-%d  %a')}  "
                 f"Work: {self.format_time(self.day_data['work_time'])}  "
                 f"Rest: {self.format_time(self.day_data['relax_time'])}")
        painter.setPen(Qt.darkBlue)
        painter.drawText(20, 30, header)

    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:02d}h{minutes:02d}m"

    def draw_time_axis(self, painter):
        painter.setFont(self.time_font)
        painter.setPen(QPen(VISUAL_CONFIG['AXIS_LINE_COLOR'], 1, Qt.DotLine))
        
        # 绘制从4点到次日4点的时间轴
        for hour_offset in range(25 - self.start_time + 4):  # 0-24小时偏移量
            x = VISUAL_CONFIG['LEFT_MARGIN'] + hour_offset * VISUAL_CONFIG['HOUR_PIXELS']
            painter.drawLine(x, 50 + self.header_margin, x, 180 + self.header_margin)
            
            # 每4小时显示一个刻度标签
            if hour_offset % 2 == 0:
                total_hour = self.start_time + hour_offset
                display_hour = total_hour % 24
                is_next_day = total_hour >= 24
                
                label = f"{display_hour:02d}:00"
                if is_next_day:
                    label = f"次日{display_hour:02d}:00"
                
                text_width = painter.fontMetrics().width(label.split('\n')[0])
                text_height = painter.fontMetrics().height() * (1 + label.count('\n'))
                
                painter.setPen(Qt.darkGray)
                # 调整文本位置避免重叠
                painter.drawText(x - text_width//2, 
                               45 + self.header_margin - text_height//2, 
                               label)
                painter.setPen(QPen(VISUAL_CONFIG['AXIS_LINE_COLOR'], 1, Qt.DotLine))

    def draw_segments(self, painter):
        painter.setFont(self.segment_font)
        for segment in self.day_data['segments']:
            start = datetime.strptime(segment['start'], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(segment['end'], "%Y-%m-%d %H:%M:%S")
            
            # 计算相对于当日4点的时间偏移
            def calculate_position(dt):
                base_time = dt.replace(hour=self.start_time, minute=0, second=0)
                if dt < base_time:
                    base_time -= timedelta(days=1)
                return (dt - base_time).total_seconds()
            
            start_sec = calculate_position(start)
            end_sec = calculate_position(end)
            
            x_start = int(VISUAL_CONFIG['LEFT_MARGIN'] + (start_sec / 3600) * VISUAL_CONFIG['HOUR_PIXELS'])
            x_end = int(VISUAL_CONFIG['LEFT_MARGIN'] + (end_sec / 3600) * VISUAL_CONFIG['HOUR_PIXELS'])
            
            # 绘制时间段块
            color = VISUAL_CONFIG['WORK_COLOR'] if segment['type'] == 'work' else VISUAL_CONFIG['REST_COLOR']
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x_start, 60 + self.header_margin, 
                                 x_end - x_start, self.block_height, 5, 5)
            
            # 绘制时间段文字
            time_range = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
            painter.setPen(Qt.white if segment['type'] == 'work' else Qt.darkGreen)
            text_width = painter.fontMetrics().width(time_range)
            if (x_end - x_start) > text_width + 10:
                painter.drawText(x_start + 5, 
                               60 + self.block_height//2 + self.header_margin + 5, 
                               time_range)

class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("5-Day Schedule")
        self.setGeometry(100, 100, 1600, 900)  # 初始窗口尺寸
        
        # 获取最近5天数据
        dates = sorted(data.keys(), reverse=True)
        recent_dates = dates[:VISUAL_CONFIG['DAYS_SHOW']]
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        
        for date in recent_dates:
            day_widget = DailySchedule(date, data[date])
            layout.addWidget(day_widget)
            layout.addSpacing(20)  # 增加日期之间的间距
        
        scroll.setWidget(content)
        self.setCentralWidget(scroll)

def load_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def load_data_for_dates(data_dir, dates):
    """
    根据日期列表加载对应的数据文件
    Args:
        data_dir: 数据目录路径
        dates: 需要加载的日期列表
    Returns:
        合并后的数据字典
    """
    all_data = {}
    # 遍历日期列表，加载对应的文件
    for date_str in dates:
        # 根据日期生成文件名（例如：2025-04.json）
        file_name = f"{date_str[:7]}.json"
        file_path = data_dir / file_name
        # 如果文件存在，则加载数据
        if file_path.exists():
            with open(file_path, 'r') as f:
                file_data = json.load(f)
                # 只添加需要的日期数据
                if date_str in file_data:
                    all_data[date_str] = file_data[date_str]
    return all_data

def get_recent_dates(days=7):
    """
    获取最近几天的日期
    Args:
        days: 需要获取的天数
    Returns:
        最近几天的日期列表
    """
    # 获取当前日期
    today = get_work_date()
    # 生成最近七天的日期列表
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

if __name__ == "__main__":
    import sys
    # 获取最近七天的日期
    recent_dates = get_recent_dates(VISUAL_CONFIG['DAYS_SHOW'])
    # 加载需要的文件数据
    recent_data = load_data_for_dates(_DATA_DIR, recent_dates)
    
    app = QApplication(sys.argv)
    window = MainWindow(recent_data)
    window.show()
    sys.exit(app.exec_())