import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style

from scraper import BilibiliScraper
from permission import BilibiliPermission
from ui import BilibiliUI
from logger import logger

# 初始化colorama
init(autoreset=True)


class BilibiliVideoHider:
    def __init__(self):
        self.driver = None
        self.scraper = None
        self.permission = None
        self.ui = BilibiliUI()
        self.videos = []

    def setup_driver(self):
        """和小红书工具一样的启动方式"""
        try:
            print(f"{Fore.CYAN}正在启动浏览器...")

            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # 不自动关闭浏览器 (和小红书工具一样)
            chrome_options.add_experimental_option("detach", True)

            # 方法1: 先尝试用本地chromedriver (如果你手动下载了)
            if os.path.exists('chromedriver.exe'):
                print(f"{Fore.GREEN}使用本地ChromeDriver...")
                service = Service('chromedriver.exe')
            else:
                # 方法2: 使用webdriver_manager (和小红书工具完全一样)
                print(f"{Fore.GREEN}自动下载ChromeDriver...")
                service = Service(ChromeDriverManager().install())

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.maximize_window()

            print(f"{Fore.GREEN}浏览器启动成功!")
            logger.info("浏览器驱动初始化成功")
            return True

        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {e}")
            print(f"{Fore.RED}启动失败: {e}")
            print(f"{Fore.YELLOW}解决方法:")
            print(f"{Fore.WHITE}1. 确保Chrome浏览器已安装")
            print(f"{Fore.WHITE}2. 手动下载chromedriver.exe放到程序目录")
            print(f"{Fore.CYAN}   下载地址: https://chromedriver.chromium.org/")
            print(f"{Fore.WHITE}3. 检查Chrome版本和chromedriver版本是否匹配")
            return False

    def login(self):
        """登录B站 - 和小红书工具一样的逻辑"""
        try:
            print(f"\n{Fore.CYAN}打开登录页面...")
            self.driver.get("https://passport.bilibili.com/login")

            print(f"{Fore.YELLOW}请在浏览器中登录B站")
            print(f"{Fore.GREEN}登录成功后按回车键继续...")
            input()

            # 转到创作中心
            print(f"{Fore.CYAN}转到创作中心...")
            self.driver.get("https://member.bilibili.com/platform/content/video")
            time.sleep(3)

            # 检查登录状态
            if "login" not in self.driver.current_url.lower():
                print(f"{Fore.GREEN}登录成功!")
                logger.info("登录成功")
                return True
            else:
                print(f"{Fore.RED}登录失败，请重试")
                logger.error("登录失败")
                return False

        except Exception as e:
            logger.error(f"登录出错: {e}")
            print(f"{Fore.RED}登录出错: {e}")
            return False

    def run(self):
        """主流程 - 和小红书工具完全一样的结构"""
        self.ui.print_banner()

        # 启动浏览器
        if not self.setup_driver():
            return

        # 登录
        if not self.login():
            self.driver.quit()
            return

        # 初始化其他模块
        self.scraper = BilibiliScraper(self.driver)
        self.permission = BilibiliPermission(self.driver)

        # 主循环
        while True:
            try:
                self.ui.show_menu()
                choice = self.ui.get_choice()

                if choice == '1':
                    self.mode_filter_by_year()
                elif choice == '2':
                    self.mode_manual_select()
                elif choice == '3':
                    self.mode_view_only()
                elif choice == '4':
                    self.quit()
                    break

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}操作已取消")
                break
            except Exception as e:
                logger.error(f"运行错误: {e}")
                print(f"{Fore.RED}错误: {e}")

    def load_videos(self):
        """加载视频列表"""
        if not self.videos:
            print(f"\n{Fore.CYAN}正在获取视频列表...")
            self.videos = self.scraper.get_video_list()

            if self.videos:
                print(f"{Fore.GREEN}找到 {len(self.videos)} 个视频")
            else:
                print(f"{Fore.RED}未找到视频")

        return self.videos

    def mode_filter_by_year(self):
        """按年份筛选模式"""
        videos = self.load_videos()
        if not videos:
            return

        # 统计年份
        years = {}
        for v in videos:
            year = v.get('year', '未知')
            years[year] = years.get(year, 0) + 1

        # 显示年份统计
        print(f"\n{Fore.CYAN}年份统计:")
        for year, count in sorted(years.items()):
            print(f"{Fore.WHITE}  {year}年: {count}个视频")

        # 选择年份
        try:
            year_choice = input(f"\n{Fore.YELLOW}输入要隐藏的年份 (如2024): ").strip()
            if not year_choice.isdigit():
                print(f"{Fore.RED}无效的年份")
                return

            year_choice = int(year_choice)
            target_videos = [v for v in videos if v.get('year') == year_choice]

            if not target_videos:
                print(f"{Fore.RED}没有{year_choice}年的视频")
                return

            # 显示并确认
            print(f"\n{Fore.GREEN}找到 {len(target_videos)} 个{year_choice}年的视频:")
            for i, v in enumerate(target_videos, 1):
                print(f"{Fore.WHITE}  [{i}] {v['title']}")

            if self.ui.confirm_action(target_videos):
                self.permission.hide_videos(target_videos)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}已取消")

    def mode_manual_select(self):
        """手动选择模式"""
        videos = self.load_videos()
        if not videos:
            return

        # 显示所有视频
        print(f"\n{Fore.CYAN}全部视频 ({len(videos)}个):")
        for i, v in enumerate(videos, 1):
            print(f"{Fore.WHITE}  [{i}] {v['title'][:50]} - {v.get('published_date', '未知')}")

        # 获取选择
        print(f"\n{Fore.YELLOW}选择方式: 1,3,5 或 1-5 或 all")
        try:
            choice = input(f"{Fore.CYAN}请选择: ").strip().lower()

            if choice == 'all':
                selected = videos
            else:
                # 解析选择
                indices = set()
                parts = choice.split(',')
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        indices.update(range(start - 1, end))
                    else:
                        indices.add(int(part) - 1)

                selected = [videos[i] for i in sorted(indices) if 0 <= i < len(videos)]

            if selected and self.ui.confirm_action(selected):
                self.permission.hide_videos(selected)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}已取消")

    def mode_view_only(self):
        """仅查看模式"""
        videos = self.load_videos()
        if videos:
            print(f"\n{Fore.CYAN}视频列表:")
            for i, v in enumerate(videos, 1):
                print(f"{Fore.WHITE}  [{i}] {v['title']}")
                print(f"{Fore.CYAN}      日期: {v.get('published_date', '未知')} | BV号: {v.get('bv', '未知')}")

    def quit(self):
        """退出"""
        print(f"\n{Fore.CYAN}正在关闭浏览器...")
        if self.driver:
            self.driver.quit()
        print(f"{Fore.GREEN}已退出，再见!")

