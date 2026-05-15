#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os


def check_environment():
    """检查运行环境"""
    print("正在检查环境...")

    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        sys.exit(1)

    # 检查依赖
    try:
        import selenium
        import colorama
        import webdriver_manager
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)

    # 创建日志目录
    if not os.path.exists('logs'):
        os.makedirs('logs')

    print("✓ 环境检查完成")
    return True


def main():
    """主启动函数"""
    print("=" * 50)
    print("   B站视频批量隐藏工具")
    print("=" * 50)

    # 检查环境
    if not check_environment():
        return

    # 导入并运行主程序
    try:
        from main import BilibiliVideoHider
        app = BilibiliVideoHider()
        app.run()
    except KeyboardInterrupt:
        print("\n\n程序已终止")
    except Exception as e:
        print(f"\n程序出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n程序结束")


if __name__ == "__main__":
    main()