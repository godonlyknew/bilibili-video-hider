"""
B站视频日期解析模块
处理B站视频的发布日期解析和筛选
"""

import re
from datetime import datetime
from typing import Optional, List


class BilibiliDateParser:
    """日期解析器"""
    
    def __init__(self):
        self.date_patterns = [
            # 2024-06-20 23:46
            r'(\d{4})-(\d{1,2})-(\d{1,2})\s*(\d{1,2}):(\d{2})',
            # 2024年06月20日 23:46
            r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{2})',
            # 2024/06/20
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            # 发布于 2024年06月20日
            r'发布于\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        ]
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            
        Returns:
            datetime对象或None
        """
        if not date_str:
            return None
        
        for pattern in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 5:
                        year, month, day, hour, minute = map(int, groups)
                        return datetime(year, month, day, hour, minute)
                    elif len(groups) == 3:
                        year, month, day = map(int, groups)
                        return datetime(year, month, day)
                except ValueError:
                    continue
        
        return None
    
    def filter_by_year(self, videos: List[dict], target_year: int) -> List[dict]:
        """
        按年份筛选视频
        
        Args:
            videos: 视频列表
            target_year: 目标年份
            
        Returns:
            筛选后的视频列表
        """
        filtered_videos = []
        for video in videos:
            date_obj = self.parse_date(video.get('date', ''))
            if date_obj and date_obj.year == target_year:
                filtered_videos.append(video)
        return filtered_videos
    
    def filter_by_date_range(self, videos: List[dict], start_date: datetime, end_date: datetime) -> List[dict]:
        """按日期范围筛选"""
        filtered_videos = []
        for video in videos:
            date_obj = self.parse_date(video.get('date', ''))
            if date_obj and start_date <= date_obj <= end_date:
                filtered_videos.append(video)
        return filtered_videos
    
    def get_available_years(self, videos: List[dict]) -> List[int]:
        """获取视频中可用的年份列表"""
        years = set()
        for video in videos:
            date_obj = self.parse_date(video.get('date', ''))
            if date_obj:
                years.add(date_obj.year)
        return sorted(list(years))
    
    def format_date(self, date_obj: datetime) -> str:
        """格式化日期显示"""
        return date_obj.strftime("%Y年%m月%d日 %H:%M")
