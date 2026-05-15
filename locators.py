"""
B站页面元素定位器定义
"""

class Locators:
    """页面元素定位器"""
    
    # 视频列表相关 - 匹配 .article-card
    VIDEO_ITEM_SELECTORS = [
        ".article-card",
        "[class*='article-card']"
    ]
    
    VIDEO_TITLE_SELECTORS = [
        ".name.ellipsis",
        ".meta-title .name",
        ".name",
        ".meta-title a"
    ]
    
    VIDEO_DATE_SELECTORS = [
        ".date",
        ".pubdate .date",
        "[class*='date']"
    ]
    
    VIDEO_LINK_SELECTORS = [
        ".cover-wrp a",
        "a[href*='bilibili.com/video']"
    ]
    
    # 操作按钮相关
    ACTION_BUTTON_SELECTORS = [
        ".more-btn",
        "[class*='more']"
    ]
    
    # 删除相关
    DELETE_BUTTON_SELECTORS = [
        "[class*='delete']",
        "[class*='删除']"
    ]
    
    DELETE_CONFIRM_BUTTON = "//button[contains(text(), '删除')]"
    
    # 分页相关
    NEXT_PAGE_BUTTON = ".bcc-pagination-next"
    PAGE_NUMBER_SELECTOR = ".bcc-pagination-item a"
    
    # 隐私设置 - 点击more-btn后的下拉菜单
    MORE_MENU_CONTAINER = ".select-box"
    MORE_MENU_ITEM = "a.left.select-item"  # 下拉菜单项
    PRIVACY_BUTTON_IN_MENU = "//a[contains(@class, 'select-item')]//span[contains(text(), '可见范围')]"
    PUBLIC_BUTTON_IN_MENU = "//span[contains(text(), '设为公开')]"
    
    # 可见范围弹框
    VISIBILITY_DIALOG = "div.cc-article-only-self-dialog.bcc-dialog__wrap"
    VISIBILITY_DIALOG_INNER = "div.bcc-dialog"
    RADIO_PRIVATE = "input[type='radio'][value='1']"  # 仅自己可见
    RADIO_PUBLIC = "input[type='radio'][value='0']"    # 公开可见
    DIALOG_CONFIRM_BUTTON = "button.bcc-button.cc-aosd-btn.bcc-button--primary"
    
    # 登录相关
    LOGIN_BUTTON = ".login-btn"
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    
    # 通用元素
    LOADING_SPINNER = ".loading"
    TOAST_MESSAGE = ".toast"
    
    # 滚动相关 - 分页模式下不需要
    SCROLL_CONTAINER_SELECTORS = [
        ".article-list_wrap",
        ".article-list"
    ]
    
    # 隐私设置选项
    PRIVACY_OPTIONS_SELECTORS = [
        "[class*='privacy']",
        "[class*='权限']",
        "[class*='visible']"
    ]
    
    PRIVATE_OPTION_TEXT = "私密"
    PUBLIC_OPTION_TEXT = "公开"
