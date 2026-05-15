"""
B站视频用户交互界面模块
"""

import os
import sys
from typing import List, Dict, Optional
from colorama import init, Fore, Style

init(autoreset=True)


class BilibiliUI:
    """B站用户界面管理器"""
    
    def __init__(self):
        pass
    
    def clear_screen(self) -> None:
        """清屏"""
        # 暂时禁用清屏，避免在某些环境下丢失输出
        pass
        # os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self) -> None:
        """打印程序头部"""
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}           B站视频批量管理工具")
        print(f"{Fore.CYAN}{'='*60}")
        print()
    
    def print_success(self, message: str) -> None:
        """打印成功消息"""
        print(f"{Fore.GREEN}[OK] {message}")
    
    def print_error(self, message: str) -> None:
        """打印错误消息"""
        print(f"{Fore.RED}[ERROR] {message}")
    
    def print_warning(self, message: str) -> None:
        """打印警告消息"""
        print(f"{Fore.YELLOW}[WARN] {message}")
    
    def print_info(self, message: str) -> None:
        """打印信息消息"""
        print(f"{Fore.BLUE}[INFO] {message}")
    
    def get_user_confirmation(self, message: str, default: bool = False) -> bool:
        """获取用户确认"""
        suffix = " [Y/n]" if default else " [y/N]"
        response = input(f"{Fore.YELLOW}{message}{suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', '是', '确认']
    
    def select_year(self, available_years: List[int]) -> Optional[int]:
        """选择年份"""
        if not available_years:
            self.print_error("没有可用的年份")
            return None
        
        print(f"\n{Fore.CYAN}可用年份:")
        for i, year in enumerate(available_years, 1):
            print(f"{Fore.WHITE}  {i}. {year}年")
        
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}请选择年份 (输入数字): ").strip()
                if not choice:
                    return None
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_years):
                    return available_years[choice_idx]
                else:
                    self.print_error("无效的选择，请重新输入")
            except ValueError:
                self.print_error("请输入有效的数字")
    
    def select_videos_manually(self, videos: List[Dict]) -> List[Dict]:
        """手动选择视频"""
        if not videos:
            return []
        
        print(f"\n{Fore.CYAN}视频列表:")
        for i, video in enumerate(videos, 1):
            title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
            date = video['date'] or "未知日期"
            print(f"{Fore.WHITE}  {i:2d}. {title} ({date})")
        
        print(f"\n{Fore.YELLOW}选择方式:")
        print(f"{Fore.WHITE}  1. 输入序号 (如: 2 或 1,3,5)")
        print(f"{Fore.WHITE}  2. 输入范围 (如: 1-5)")
        print(f"{Fore.WHITE}  3. 输入 'all' 选择全部")
        print(f"{Fore.WHITE}  4. 输入 'none' 取消选择")
        
        while True:
            choice = input(f"\n{Fore.YELLOW}请选择: ").strip()
            
            if choice.lower() == 'all':
                return videos
            elif choice.lower() == 'none':
                return []
            elif choice.isdigit():
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(videos):
                        return [videos[idx]]
                    else:
                        self.print_error(f"序号 {idx+1} 无效")
                except ValueError:
                    self.print_error("输入格式错误，请重新输入")
            elif ',' in choice:
                try:
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    selected = []
                    for idx in indices:
                        if 0 <= idx < len(videos):
                            selected.append(videos[idx])
                        else:
                            self.print_error(f"序号 {idx+1} 无效")
                    return selected
                except ValueError:
                    self.print_error("输入格式错误，请重新输入")
            elif '-' in choice:
                try:
                    start, end = choice.split('-')
                    start_idx = int(start.strip()) - 1
                    end_idx = int(end.strip()) - 1
                    
                    if 0 <= start_idx <= end_idx < len(videos):
                        return videos[start_idx:end_idx + 1]
                    else:
                        self.print_error("范围无效，请重新输入")
                except ValueError:
                    self.print_error("输入格式错误，请重新输入")
            else:
                self.print_error("输入格式错误，请重新输入")
    
    def display_videos_summary(self, videos: List[Dict], title: str = "视频列表") -> None:
        """显示视频摘要"""
        print(f"\n{Fore.CYAN}{title} ({len(videos)} 条):")
        print(f"{Fore.CYAN}{'-'*50}")
        
        for i, video in enumerate(videos, 1):
            title_text = video['title'][:45] + "..." if len(video['title']) > 45 else video['title']
            date = video['date'] or "未知日期"
            status = "[OK]" if video.get('has_action_button') else "[--]"
            print(f"{Fore.WHITE}{i:2d}. {status} {title_text} ({date})")
        
        print(f"{Fore.CYAN}{'-'*50}")
    
    def confirm_batch_operation(self, videos: List[Dict], operation: str = "private") -> bool:
        """确认批量操作"""
        if operation == "private":
            self.display_videos_summary(videos, "即将设为私密的视频")
            print(f"\n{Fore.YELLOW}警告: 此操作将把上述视频设为私密状态")
            print(f"{Fore.YELLOW}其他用户将无法查看这些视频")
            return self.get_user_confirmation("确认执行设为私密操作吗？", False)
        else:
            self.display_videos_summary(videos, "即将设为公开的视频")
            print(f"\n{Fore.GREEN}提示: 此操作将把上述视频设为公开状态")
            print(f"{Fore.GREEN}操作后，其他用户将可以查看这些视频")
            return self.get_user_confirmation("确认执行设为公开操作吗？", False)
    
    def display_operation_results(self, results: Dict[str, int]) -> None:
        """显示操作结果"""
        print(f"\n{Fore.CYAN}操作结果:")
        print(f"{Fore.CYAN}{'-'*30}")
        print(f"{Fore.WHITE}总计: {results['total']} 条")
        print(f"{Fore.GREEN}成功: {results['success']} 条")
        print(f"{Fore.RED}失败: {results['failed']} 条")
        
        if results['failed'] > 0:
            self.print_warning("部分操作失败，请检查网络连接和页面状态")
        else:
            self.print_success("所有操作已完成")
    
    def get_operation_mode(self) -> str:
        """获取操作模式"""
        print(f"\n{Fore.CYAN}请选择操作模式:")
        print(f"{Fore.WHITE}  1. 按年份筛选并设为私密")
        print(f"{Fore.WHITE}  2. 手动选择视频设为私密")
        print(f"{Fore.WHITE}  3. 按年份筛选并设为公开")
        print(f"{Fore.WHITE}  4. 手动选择视频设为公开")
        print(f"{Fore.WHITE}  5. 仅查看视频列表")
        print(f"{Fore.CYAN}  6. 刷新视频列表")
        print(f"{Fore.WHITE}  7. 退出程序")
        
        while True:
            choice = input(f"\n{Fore.YELLOW}请选择 (1-7): ").strip()
            
            if choice == '1':
                return 'year_private'
            elif choice == '2':
                return 'manual_private'
            elif choice == '3':
                return 'year_public'
            elif choice == '4':
                return 'manual_public'
            elif choice == '5':
                return 'view'
            elif choice == '6':
                return 'refresh'
            elif choice == '7':
                return 'exit'
            else:
                self.print_error("无效的选择，请重新输入")
    
    def wait_for_enter(self, message: str = "按回车键继续...") -> None:
        """等待用户按回车"""
        input(f"\n{Fore.YELLOW}{message}")
