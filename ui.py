from colorama import Fore, Style


class BilibiliUI:
    def print_banner(self):
        print(f"\n{Fore.CYAN}{'=' * 50}")
        print(f"{Fore.YELLOW}  B站视频批量隐藏工具 v1.0")
        print(f"{Fore.CYAN}{'=' * 50}")

    def show_menu(self):
        print(f"\n{Fore.GREEN}请选择操作:")
        print(f"{Fore.WHITE}  1. 按年份筛选并隐藏")
        print(f"{Fore.WHITE}  2. 手动选择视频隐藏")
        print(f"{Fore.WHITE}  3. 仅查看视频列表")
        print(f"{Fore.WHITE}  4. 退出程序")

    def get_choice(self):
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}请输入选项 (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    return choice
                print(f"{Fore.RED}无效，请输入1-4")
            except KeyboardInterrupt:
                raise

    def confirm_action(self, videos):
        print(f"\n{Fore.RED}⚠️  将隐藏以下 {len(videos)} 个视频:")
        for v in videos[:5]:
            print(f"  - {v['title'][:40]}")
        if len(videos) > 5:
            print(f"  ... 等共{len(videos)}个")

        confirm = input(f"\n{Fore.YELLOW}确认? (yes/no): ").strip().lower()
        return confirm == 'yes'