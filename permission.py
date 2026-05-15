import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from locators import BilibiliLocators
from logger import logger


class BilibiliPermission:
    """B站视频权限修改器"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.locators = BilibiliLocators()

    def hide_videos(self, videos_to_hide):
        """批量隐藏视频"""
        success_count = 0
        fail_count = 0

        for i, video in enumerate(videos_to_hide, 1):
            try:
                logger.info(f"正在处理第 {i}/{len(videos_to_hide)} 个视频: {video['title']}")

                if self._hide_single_video(video):
                    success_count += 1
                else:
                    fail_count += 1

                # 操作间隔，避免触发反爬机制
                if i < len(videos_to_hide):
                    time.sleep(3)

            except Exception as e:
                logger.error(f"隐藏视频失败 {video['title']}: {e}")
                fail_count += 1

        logger.info(f"批量隐藏完成: 成功 {success_count} 个, 失败 {fail_count} 个")
        return success_count, fail_count

    def _hide_single_video(self, video):
        """隐藏单个视频"""
        try:
            # 1. 导航到视频编辑页面
            self.driver.get(video['url'])
            time.sleep(2)

            # 2. 点击更多操作按钮
            try:
                more_btn = self.wait.until(
                    EC.element_to_be_clickable(self.locators.MORE_BUTTON)
                )
                more_btn.click()
                time.sleep(1)
            except TimeoutException:
                logger.error(f"找不到更多操作按钮: {video['title']}")
                return False

            # 3. 点击权限设置
            try:
                permission_btn = self.wait.until(
                    EC.element_to_be_clickable(self.locators.EDIT_PERMISSION_BTN)
                )
                permission_btn.click()
                time.sleep(1)
            except TimeoutException:
                logger.error(f"找不到权限设置按钮: {video['title']}")
                return False

            # 4. 等待权限弹窗出现
            try:
                self.wait.until(
                    EC.presence_of_element_locked(self.locators.PERMISSION_DIALOG)
                )
            except TimeoutException:
                logger.error(f"权限弹窗未出现: {video['title']}")
                return False

            # 5. 选择"仅我可见"
            try:
                private_radio = self.wait.until(
                    EC.element_to_be_clickable(self.locators.PRIVATE_RADIO)
                )
                private_radio.click()
                time.sleep(0.5)
            except TimeoutException:
                logger.error(f"找不到'仅我可见'选项: {video['title']}")
                return False

            # 6. 点击确认按钮
            try:
                confirm_btn = self.wait.until(
                    EC.element_to_be_clickable(self.locators.CONFIRM_BUTTON)
                )
                confirm_btn.click()
                time.sleep(2)

                logger.info(f"成功隐藏视频: {video['title']}")
                return True

            except TimeoutException:
                logger.error(f"找不到确认按钮: {video['title']}")
                return False

        except Exception as e:
            logger.error(f"隐藏视频时出错 {video['title']}: {e}")
            return False