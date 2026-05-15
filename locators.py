from selenium.webdriver.common.by import By


class BilibiliLocators:
    """B站创作中心页面元素定位器"""

    # 登录页面
    LOGIN_BUTTON = (By.CLASS_NAME, "login-btn")

    # 内容管理页面
    VIDEO_LIST_CONTAINER = (By.CLASS_NAME, "video-list-container")
    VIDEO_ITEMS = (By.CLASS_NAME, "video-item")

    # 视频信息
    VIDEO_TITLE = (By.CLASS_NAME, "video-title")
    VIDEO_DATE = (By.CLASS_NAME, "video-date")
    VIDEO_LINK = (By.CLASS_NAME, "video-link")

    # 操作按钮
    MORE_BUTTON = (By.CLASS_NAME, "more-btn")
    EDIT_PERMISSION_BTN = (By.XPATH, "//li[contains(text(), '权限设置')]")

    # 权限设置弹窗
    PERMISSION_DIALOG = (By.CLASS_NAME, "permission-dialog")
    PRIVATE_RADIO = (By.XPATH, "//label[contains(text(), '仅我可见')]")
    CONFIRM_BUTTON = (By.CLASS_NAME, "confirm-btn")

    # 加载更多
    LOAD_MORE_BUTTON = (By.CLASS_NAME, "load-more")

    # 分页
    NEXT_PAGE_BUTTON = (By.CLASS_NAME, "next-page")