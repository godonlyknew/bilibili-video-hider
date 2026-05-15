#!/usr/bin/env python3
"""
B站视频批量管理工具 - 启动脚本
"""

import sys
import os
import time
import argparse

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from main import BilibiliVideoManager
    
    def main():
        parser = argparse.ArgumentParser(description='B站视频批量管理工具')
        parser.add_argument('--no-cache', action='store_true', 
                           help='不使用缓存，强制重新抓取视频列表')
        parser.add_argument('--clear-cache', action='store_true',
                           help='清除缓存后退出')
        args = parser.parse_args()
        
        from scraper import VideoCache, BilibiliScraper
        
        # 清除缓存模式
        if args.clear_cache:
            VideoCache.clear_cache()
            return
        
        print("正在启动B站视频批量管理工具...")
        print("请确保已安装Chrome浏览器")
        print("=" * 50)
        sys.stdout.flush()
        
        if args.no_cache:
            print("提示: 本次运行将强制刷新，不使用缓存")
        
        manager = BilibiliVideoManager()
        sys.stdout.flush()
        
        # 立即打开浏览器
        print("正在打开浏览器...")
        manager.scraper = BilibiliScraper(headless=False)
        manager.scraper.setup_driver()
        
        # 检查登录
        if not manager.scraper.check_login():
            print("登录失败，无法继续")
            manager._cleanup()
            return
        
        # 确保在视频列表页面
        print("正在加载视频列表页面...")
        manager.scraper.driver.get(manager.scraper.base_url)
        time.sleep(3)
        
        sys.stdout.flush()
        
        # 强制刷新模式 - 先刷新缓存再进入主程序
        if args.no_cache:
            manager._extract_videos(force_refresh=True)
        
        manager.run()
        
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖包:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"程序启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    main()
