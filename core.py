# TODO-CODE
# 数据管理器默认存储位置改成用户目录 v
# addSegment似乎要改 v

from PyQt5.QtCore import QTimer, QElapsedTimer, QObject, pyqtSignal
from utils import CrashHandler, Logger, _DATA_DIR

_logger = Logger(__name__)

class PairTimer(QObject):
    """实现一个两个计时器的类，一个计时器工作，一个计时器休息"""    
    # 定义信号
    work_timer_timeout = pyqtSignal(int)  # 发送工作时间（秒）
    relax_timer_timeout = pyqtSignal(int)  # 发送休息时间（秒）
    
    def __init__(self):
        super().__init__()
        self.work_timer = QTimer()  # 用于触发计时更新
        self.relax_timer = QTimer()
        
        self.work_elapsed = QElapsedTimer()  # 用于记录实际经过的时间
        self.relax_elapsed = QElapsedTimer()
        
        self._work_time = 0  # 累计工作时间（毫秒）
        self._relax_time = 0  # 累计休息时间（毫秒）
        self._start_time = None  # 开始时间
        
        # 设置定时器间隔并连接信号
        self.work_timer.setInterval(100)  # 500毫秒刷新一次
        self.relax_timer.setInterval(100)  # 500毫秒刷新一次
        self.work_timer.timeout.connect(self._on_work_timer)
        self.relax_timer.timeout.connect(self._on_relax_timer)
        
    def _on_work_timer(self):
        """工作定时器触发时发送信号"""
        seconds = self.get_work_time() // 1000  # 转换为秒
        self.work_timer_timeout.emit(seconds)
        
    def _on_relax_timer(self):
        """休息定时器触发时发送信号"""
        seconds = self.get_relax_time() // 1000  # 转换为秒
        self.relax_timer_timeout.emit(seconds)
        
    def start_work(self):
        """开始工作计时"""
        if not self.work_elapsed.isValid():
            self.work_elapsed.start()
        self.work_timer.start()
        self._start_time = datetime.now()
        self.relax_timer.stop()
        if self.relax_elapsed.isValid():
            self._relax_time += self.relax_elapsed.elapsed()
            self.relax_elapsed.invalidate()
        
    def start_relax(self):
        """开始休息计时"""
        if not self.relax_elapsed.isValid():
            self.relax_elapsed.start()
        self.work_timer.stop()
        self._start_time = datetime.now()
        self.relax_timer.start()
        if self.work_elapsed.isValid():
            self._work_time += self.work_elapsed.elapsed()
            self.work_elapsed.invalidate()
        
    def stop(self):
        """停止所有计时"""
        self._start_time = None
        self.work_timer.stop()
        self.relax_timer.stop()
        if self.work_elapsed.isValid():
            self._work_time += self.work_elapsed.elapsed()
            self.work_elapsed.invalidate()
        if self.relax_elapsed.isValid():
            self._relax_time += self.relax_elapsed.elapsed()
            self.relax_elapsed.invalidate()
        
    def get_work_time(self):
        """获取工作时间（毫秒）"""
        current = self.work_elapsed.elapsed() if self.work_elapsed.isValid() else 0
        return self._work_time + current
    
    def get_relax_time(self):
        """获取休息时间（毫秒）"""
        current = self.relax_elapsed.elapsed() if self.relax_elapsed.isValid() else 0
        return self._relax_time + current
    
    def get_start_time(self):
        """获取开始时间"""
        return self._start_time
    
    def reset(self):
        """重置所有计时器"""
        self.work_timer.stop()
        self.relax_timer.stop()
        self.work_elapsed.invalidate()
        self.relax_elapsed.invalidate()
        self._work_time = 0
        self._relax_time = 0
        
    def clear(self):
        """清空所有计时器"""
        self._work_time = 0
        self._relax_time = 0
        self.work_elapsed.restart()
        self.relax_elapsed.restart()
        
    def get_total_time(self):
        """获取总时间（毫秒）"""
        return self.get_work_time() + self.get_relax_time()
        
    def get_elapsed_time(self):
        """获取当前计时器的时间（毫秒）"""
        if self.work_elapsed.isValid():
            return self.work_elapsed.elapsed()
        elif self.relax_elapsed.isValid():
            return self.relax_elapsed.elapsed()
        return 0
        
    def add_work_time(self, milliseconds: int):
        """
        手动添加工作时间
        Args:
            milliseconds: 要添加的时间（毫秒）
        """
        # 如果当前正在计时，先保存当前计时
        if self.work_elapsed.isValid():
            self._work_time += self.work_elapsed.elapsed()
            self.work_elapsed.restart()
        self._work_time += milliseconds
        # 触发一次信号更新显示
        self._on_work_timer()
    
    def add_relax_time(self, milliseconds: int):
        """
        手动添加休息时间
        Args:
            milliseconds: 要添加的时间（毫秒）
        """
        # 如果当前正在计时，先保存当前计时
        if self.relax_elapsed.isValid():
            self._relax_time += self.relax_elapsed.elapsed()
            self.relax_elapsed.restart()
        self._relax_time += milliseconds
        # 触发一次信号更新显示
        self._on_relax_timer()
    
    def is_work_active(self) -> bool:
        """
        检查工作计时器是否在运行
        Returns:
            bool: 是否在运行
        """
        return self.work_timer.isActive()
    
    def is_relax_active(self) -> bool:
        """
        检查休息计时器是否在运行
        Returns:
            bool: 是否在运行
        """
        return self.relax_timer.isActive()
    
    def is_any_active(self) -> bool:
        """
        检查是否有任何计时器在运行
        Returns:
            bool: 是否有计时器在运行
        """
        return self.is_work_active() or self.is_relax_active()
        

import json
from datetime import datetime, date, timedelta
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from utils import get_work_date


class DataManager:
    """管理每日卷摆时间数据"""
    
    def __init__(self, is_file_operations_disabled: bool = False):
        """
        初始化数据管理器
        Args:
            is_file_operations_disabled: 是否禁用文件操作
        """
        self.data_dir = str(_DATA_DIR)  # 将 _DATA_DIR 转换为字符串
        self._is_file_operations_disabled = is_file_operations_disabled
        self._current_date = None  # 记录当前正在操作的日期
        self._current_date_data = None  # 当前日期的数据
        
        if not self._is_file_operations_disabled and not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            _logger.info(f"创建数据目录: {self.data_dir}")
            
        # 初始化时切换到当前工作日期
        self.change_work_date(get_work_date())
    
    def _get_date_filename(self, target_date: date) -> str:
        """获取指定日期的数据文件名"""
        return os.path.join(self.data_dir, f"{target_date.strftime('%Y-%m')}.json")
    
    def _load_month_data(self, target_date: date) -> Dict:
        """加载指定月份的数据"""
        filename = self._get_date_filename(target_date)
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def change_work_date(self, target_date: date) -> bool:
        """
        切换工作日期，如果日期发生变化则重新加载数据
        Args:
            target_date: 目标日期
        Returns:
            bool: 日期是否发生变化
        """
        if self._current_date == target_date:
            return False
            
        _logger.info(f"切换到新的工作日期: {target_date}")
        self._current_date = target_date
        
        # 加载新日期的数据
        month_data = self._load_month_data(target_date)
        date_str = target_date.strftime('%Y-%m-%d')
        
        if date_str not in month_data:
            _logger.info(f"创建新的日期数据: {date_str}")
            month_data[date_str] = {
                'work_time': 0,
                'relax_time': 0,
                'segments': []
            }
            # 保存新创建的数据
            if not self._is_file_operations_disabled:
                self._save_month_data(target_date, month_data)
                
        self._current_date_data = month_data[date_str]
        return True
    
    def _save_month_data(self, target_date: date, data_month: Dict):
        """保存月度数据"""
        if self._is_file_operations_disabled:
            _logger.debug("文件操作已禁用，跳过数据保存")
            return
            
        filename = self._get_date_filename(target_date)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_month, f, ensure_ascii=False, indent=2)
        _logger.debug(f"保存月度数据到文件: {filename}")
    
    def save_current_state(self, work_time: int, relax_time: int):
        """
        保存当前状态
        Args:
            work_time: 当前工作时间（秒）
            relax_time: 当前休息时间（秒）
        """
        if self._is_file_operations_disabled:
            _logger.debug("文件操作已禁用，跳过状态保存")
            return
            
        # 确保在正确的日期下操作
        self.change_work_date(get_work_date())
        
        # 更新今日数据
        self._current_date_data['work_time'] = work_time
        self._current_date_data['relax_time'] = relax_time
        
        # 更新月度数据文件
        month_data = self._load_month_data(self._current_date)
        date_str = self._current_date.strftime('%Y-%m-%d')
        month_data[date_str] = self._current_date_data
        self._save_month_data(self._current_date, month_data)
        _logger.debug(f"保存当前状态 - 日期: {date_str}, 工作时间: {work_time}秒, 休息时间: {relax_time}秒")
    
    def add_time_segment(self, start_time: datetime, end_time: datetime, 
                        work_time: int, relax_time: int, is_work: bool, elapsed_time: int):
        """
        添加一个时间段的数据
        Args:
            start_time: 开始时间
            end_time: 结束时间
            work_time: 工作时间（秒）
            relax_time: 休息时间（秒）
            is_work: 是否是工作时间段
            elapsed_time: 当前计时器的增量时间（秒）
        """
        if self._is_file_operations_disabled:
            _logger.debug("文件操作已禁用，跳过添加时间段")
            return
            
        # 使用结束时间来决定数据属于哪一天
        target_date = get_work_date(end_time)
        
        # 切换到目标日期
        self.change_work_date(target_date)
        
        segment = {
            'start': start_time.strftime('%H:%M:%S'),
            'end': end_time.strftime('%H:%M:%S'),
            'work_time': work_time,
            'relax_time': relax_time,
            'type': 'work' if is_work else 'relax',
            'elapsed_time': elapsed_time
        }
        self._current_date_data['segments'].append(segment)
        
        # 保存数据
        month_data = self._load_month_data(self._current_date)
        date_str = self._current_date.strftime('%Y-%m-%d')
        month_data[date_str] = self._current_date_data
        self._save_month_data(self._current_date, month_data)
        
        _logger.info(
            f"添加时间段 - 日期: {date_str}, "
            f"类型: {'工作' if is_work else '休息'}, "
            f"开始: {segment['start']}, "
            f"结束: {segment['end']}, "
            f"工作时间: {work_time}秒, "
            f"休息时间: {relax_time}秒, "
            f"实际经过时间: {segment['elapsed_time']}秒"
        )
    
    def get_day_stats(self, target_date: Optional[date] = None) -> Dict:
        """
        获取指定日期的统计数据
        Args:
            target_date: 目标日期，默认为今天
        Returns:
            包含工作和休息时间的字典
        """
        if target_date is None:
            target_date = get_work_date()
            
        # 如果是查询当前日期的数据，直接返回
        if target_date == self._current_date:
            return {
                'work_time': self._current_date_data['work_time'],
                'relax_time': self._current_date_data['relax_time'],
                'segments': self._current_date_data.get('segments', [])
            }
            
        # 否则从文件加载数据
        month_data = self._load_month_data(target_date)
        date_str = target_date.strftime('%Y-%m-%d')
        
        if date_str in month_data:
            return {
                'work_time': month_data[date_str]['work_time'],
                'relax_time': month_data[date_str]['relax_time'],
                'segments': month_data[date_str].get('segments', [])
            }
        return {'work_time': 0, 'relax_time': 0, 'segments': []}
    
    def get_month_stats(self, year: int, month: int) -> List[Dict]:
        """
        获取指定月份的统计数据
        Args:
            year: 年份
            month: 月份
        Returns:
            月度统计数据列表
        """
        target_date = date(year, month, 1)
        month_data = self._load_month_data(target_date)
        
        stats = []
        for date_str, data in month_data.items():
            stats.append({
                'date': date_str,
                'work_time': data['work_time'],
                'relax_time': data['relax_time'],
                'segments': data.get('segments', [])
            })
        
        return sorted(stats, key=lambda x: x['date'])
    
    def get_recent_days_stats(self, days: int = 7) -> List[Dict]:
        """
        获取最近几天的统计数据
        Args:
            days: 天数
        Returns:
            最近几天的统计数据列表
        """
        today = get_work_date()
        stats = []
        
        for i in range(days):
            target_date = today.fromordinal(today.toordinal() - i)
            day_stats = self.get_day_stats(target_date)
            day_stats['date'] = target_date.strftime('%Y-%m-%d')
            stats.append(day_stats)
        
        return list(reversed(stats))  # 按日期升序返回

