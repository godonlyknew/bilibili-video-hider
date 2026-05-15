"""
B站视频批量管理工具 - 主程序

支持批量将视频设为私密/公开，按年份筛选等操作。

作者: Bilibili Manager Team
版本: 1.1.0
"""

__version__ = "1.1.0"
__author__ = "Bilibili Manager Team"
__license__ = "MIT"

import sys
import os
import time
from typing import List, Dict, Optional

from scraper import BilibiliScraper, VideoCache
from date_parser import BilibiliDateParser
from ui import BilibiliUI


class BilibiliVideoManager:
    """B站视频管理器主类"""
    
    def __init__(self):
        """初始化主程序"""
        self.ui = BilibiliUI()
        self.scraper: Optional[BilibiliScraper] = None
        self.date_parser = BilibiliDateParser()
        self.videos_cache: Optional[List[Dict]] = None
    
    def run(self) -> None:
        """运行主程序"""
        try:
            self.ui.print_header()
            print("程序启动")
            
            while True:
                mode = self.ui.get_operation_mode()
                
                if mode == 'exit':
                    self.ui.print_info("程序退出")
                    break
                elif mode == 'view':
                    self._view_videos_mode()
                elif mode == 'refresh':
                    self._refresh_videos_mode()
                elif mode == 'year_private':
                    self._year_filter_mode('private')
                elif mode == 'manual_private':
                    self._manual_select_mode('private')
                elif mode == 'year_public':
                    self._year_filter_mode('public')
                elif mode == 'manual_public':
                    self._manual_select_mode('public')
                
                if mode != 'exit':
                    self.ui.wait_for_enter()
                    self.ui.print_header()
                    
        except KeyboardInterrupt:
            self.ui.print_warning("程序被用户中断")
        except Exception as e:
            self.ui.print_error(f"程序运行出错: {e}")
        finally:
            self._cleanup()
    
    def _view_videos_mode(self) -> None:
        """查看视频列表模式"""
        videos = self._extract_videos()
        if videos:
            self.ui.display_videos_summary(videos, "所有视频")
            
            # 显示年份统计
            available_years = self.date_parser.get_available_years(videos)
            if available_years:
                self.ui.print_info("年份统计:")
                for year in available_years:
                    year_videos = self.date_parser.filter_by_year(videos, year)
                    self.ui.print_info(f"  {year}年: {len(year_videos)} 条")
        else:
            self.ui.print_error("没有找到视频")
    
    def _refresh_videos_mode(self) -> None:
        """刷新视频列表模式"""
        self.ui.print_info("正在刷新视频列表...")
        self.videos_cache = None
        VideoCache.clear_cache()
        
        videos = self._extract_videos()
        if videos:
            self.ui.print_success(f"刷新完成，共提取 {len(videos)} 条视频")
            self.ui.display_videos_summary(videos, "刷新后的视频")
            
            available_years = self.date_parser.get_available_years(videos)
            if available_years:
                self.ui.print_info("年份统计:")
                for year in available_years:
                    year_videos = self.date_parser.filter_by_year(videos, year)
                    self.ui.print_info(f"  {year}年: {len(year_videos)} 条")
        else:
            self.ui.print_error("刷新后没有找到视频")
    
    def _year_filter_mode(self, operation: str = 'private') -> None:
        """按年份筛选模式"""
        videos = self._extract_videos()
        if not videos:
            self.ui.print_error("没有找到视频")
            return
        
        available_years = self.date_parser.get_available_years(videos)
        if not available_years:
            self.ui.print_error("没有找到有效的日期信息")
            return
        
        selected_year = self.ui.select_year(available_years)
        if not selected_year:
            return
        
        filtered_videos = self.date_parser.filter_by_year(videos, selected_year)
        if not filtered_videos:
            self.ui.print_info(f"{selected_year}年没有视频")
            return
        
        operation_text = "设为私密" if operation == 'private' else "设为公开"
        self.ui.print_info(f"找到 {selected_year}年的视频 {len(filtered_videos)} 条")
        self.ui.display_videos_summary(filtered_videos, f"{selected_year}年的视频")
        
        if self.ui.confirm_batch_operation(filtered_videos, operation):
            self._execute_operation(filtered_videos, operation)
    
    def _manual_select_mode(self, operation: str = 'private') -> None:
        """手动选择模式"""
        videos = self._extract_videos()
        if not videos:
            self.ui.print_error("没有找到视频")
            return
        
        selected_videos = self.ui.select_videos_manually(videos)
        if not selected_videos:
            self.ui.print_info("没有选择任何视频")
            return
        
        operation_text = "设为私密" if operation == 'private' else "设为公开"
        self.ui.print_info(f"已选择 {len(selected_videos)} 条视频进行{operation_text}")
        
        if self.ui.confirm_batch_operation(selected_videos, operation):
            self._execute_operation(selected_videos, operation)
    
    def _extract_videos(self, force_refresh: bool = False) -> List[Dict]:
        """提取视频数据
        
        Args:
            force_refresh: 是否强制刷新（忽略内存缓存）
        """
        try:
            # 检查文件缓存
            if not force_refresh:
                cached_info = VideoCache.get_cache_info()
                if cached_info:
                    self.ui.print_info(f"发现本地缓存: {cached_info['count']} 条视频 (缓存时间: {cached_info['cached_at']})")
            
            # 检查内存缓存
            if not force_refresh and self.videos_cache is not None:
                self.ui.print_info(f"使用内存缓存的视频数据，共 {len(self.videos_cache)} 条")
                return self.videos_cache
            
            # 检查是否有可用缓存文件
            if not force_refresh:
                cached_videos = VideoCache.load_videos()
                if cached_videos:
                    self.videos_cache = cached_videos
                    self.ui.print_success(f"从缓存加载 {len(cached_videos)} 条视频")
                    return cached_videos
            
            # 需要重新抓取
            if self.scraper and self.scraper.driver:
                try:
                    self.scraper.driver.current_url
                    self.ui.print_info("检测到现有Chrome会话，复用现有连接...")
                except:
                    self.ui.print_warning("现有Chrome会话无效")
                    self.scraper = None
            
            if not self.scraper:
                self.ui.print_info("正在启动浏览器...")
                self.scraper = BilibiliScraper(headless=False)
                self.scraper.setup_driver()
            
            # 使用新的分页提取方法（会自动保存缓存）
            videos = self.scraper.extract_all_videos()
            
            if videos:
                self.ui.print_success(f"成功提取 {len(videos)} 条视频")
                self.videos_cache = videos
            else:
                self.ui.print_error("没有提取到视频")
            
            return videos
                
        except Exception as e:
            self.ui.print_error(f"提取视频失败: {e}")
            return []
    
    def _execute_operation(self, videos: List[Dict], operation: str = 'private') -> None:
        """执行操作（设为私密/公开）"""
        if not self.scraper or not self.scraper.driver:
            self.ui.print_error("浏览器连接已断开，请重新提取视频")
            return
        
        try:
            total = len(videos)
            success = 0
            failed = 0
            
            self.ui.print_info(f"处理 {total} 个视频...")
            
            for i, video in enumerate(videos, 1):
                title = video.get('title', '未知')
                short_title = title[:30]
                
                try:
                    # 使用标题直接查找并操作
                    if operation == 'private':
                        result = self.scraper.set_video_private_by_title(title)
                    else:
                        result = self.scraper.set_video_public_by_title(title)
                    
                    if result:
                        success += 1
                        self.ui.print_success(f"[{i}/{total}] {short_title}")
                    else:
                        failed += 1
                        self.ui.print_error(f"[{i}/{total}] {short_title}")
                    
                    time.sleep(1)  # 避免操作过快
                    
                except Exception as e:
                    failed += 1
                    self.ui.print_error(f"[{i}/{total}] {short_title} - {e}")
            
            results = {'total': total, 'success': success, 'failed': failed}
            self.ui.display_operation_results(results)
            
        except Exception as e:
            self.ui.print_error(f"执行操作失败: {e}")
    
    def _cleanup(self) -> None:
        """清理资源"""
        try:
            if self.scraper:
                # 不自动关闭浏览器，保持复用
                pass
        except Exception as e:
            print(f"清理资源时发生错误: {e}")


def main():
    """主函数"""
    try:
        if sys.version_info < (3, 7):
            print("错误: 需要Python 3.7或更高版本")
            sys.exit(1)
        
        hider = BilibiliVideoManager()
        hider.run()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
