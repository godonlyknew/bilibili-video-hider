# B站稿件批量可见管理工具

一个基于Python Selenium的B站稿件批量可见管理工具，可以帮助您快速将视频设为私密或公开，支持按年份筛选。

## 安装要求

- Python 3.7+
- 已安装 Chrome 浏览器
- 网络连接

## 快速开始

1) 克隆或下载项目到本地

2) 可选：创建并激活虚拟环境（推荐）

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3) 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动程序

```bash
python main.py
# 或使用启动脚本
python run.py
```

### 命令行选项

```bash
# 不使用缓存，强制重新抓取视频列表
python run.py --no-cache

# 清除缓存后退出
python run.py --clear-cache
```

### 操作流程

1. **启动程序**: 运行后会自动打开Chrome浏览器
2. **登录账号**: 如果未登录，请在浏览器中手动登录B站创作者平台
3. **选择模式**: 程序提供多种操作模式：
   - 查看视频列表
   - 刷新视频列表（清除缓存重新抓取）
   - 按年份筛选设为私密
   - 按年份筛选设为公开
   - 手动选择设为私密
   - 手动选择设为公开
   - 退出程序

## 缓存说明

程序会自动将视频列表保存到本地文件（`cache/videos_cache.json`），下次运行时可直接加载，无需重新从网页抓取。

### 管理缓存

- **使用缓存**: 默认行为，直接加载本地缓存
- **刷新缓存**: 在程序中选择"刷新视频列表"，或使用 `python run.py --no-cache`
- **清除缓存**: 使用 `python run.py --clear-cache`

### 缓存数据

缓存文件包含以下信息：
- BV号
- 视频标题
- 发布日期
- 视频链接

注意：缓存仅存储视频列表信息，不包含操作按钮。执行操作时仍需要浏览器连接。

## 文件结构

```
B站视频管理/
├── main.py              # 主程序入口
├── run.py               # 启动脚本（支持命令行参数）
├── scraper.py           # 数据提取模块（含缓存管理）
├── date_parser.py       # 日期解析模块
├── locators.py         # 页面元素定位器
├── ui.py                # 用户界面模块
├── logger.py            # 日志记录模块
├── requirements.txt     # 依赖包列表
├── cache/               # 视频缓存目录（自动创建）
│   └── videos_cache.json
├── chrome_user_data/    # Chrome用户数据（自动创建）
├── logs/                # 日志文件目录（自动创建）
└── README.md
```

## 注意事项

1. **登录要求**: 需要登录B站创作者平台
2. **网络稳定**: 操作过程中请保持网络连接稳定
3. **浏览器窗口**: 请不要关闭自动打开的浏览器窗口
4. **操作间隔**: 程序设置了操作间隔，避免操作过快
5. **页面变化**: 如果B站页面结构发生变化，可能需要更新定位器

## 常见问题

### Q: 程序启动时提示ChromeDriver错误？
A: 程序会自动使用已安装的Chrome浏览器，如有问题请确认Chrome已正确安装。

## 技术实现

- **Selenium WebDriver**: 浏览器自动化
- **Chrome DevTools**: 页面元素定位和交互
- **Python 3.7+**: 主要编程语言
- **JSON**: 缓存数据存储

## 免责声明

本工具仅供学习和个人使用，请遵守B站的使用条款。使用本工具产生的任何后果由用户自行承担。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 许可证

MIT License
