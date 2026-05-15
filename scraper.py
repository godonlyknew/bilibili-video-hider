import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from locators import BilibiliLocators
from logger import logger


class BilibiliScraper:
    """B站视频数据提取器"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.locators = BilibiliLocators()

    def navigate_to_content_page(self):
        """导航到内容管理页面"""
        try:
            self.driver.get("https://member.bilibili.com/platform/content/video")
            time.sleep(3)
            logger.info("已导航到B站创作中心内容管理页面")
            return True
        except Exception as e:
            logger.error(f"导航到内容管理页面失败: {e}")
            return False

    def get_all_videos(self, max_scroll_attempts=10):
        """获取所有视频信息"""
        videos = []
        scroll_attempts = 0

        while scroll_attempts < max_scroll_attempts:
            try:
                # 查找所有视频项目
                video_elements = self.driver.find_elements(*self.locators.VIDEO_ITEMS)

                for element in video_elements:
                    try:
                        video_info = self._extract_video_info(element)
                        if video_info and video_info not in videos:
                            videos.append(video_info)
                    except Exception as e:
                        logger.error(f"提取视频信息失败: {e}")
                        continue

                # 尝试加载更多
                if not self._load_more_videos():
                    break

                scroll_attempts += 1
                time.sleep(2)

            except Exception as e:
                logger.error(f"获取视频列表失败: {e}")
                break

        logger.info(f"共提取到 {len(videos)} 个视频")
        return videos

    def _extract_video_info(self, element):
        """提取单个视频信息"""
        try:
            # 提取标题
            title_element = element.find_element(*self.locators.VIDEO_TITLE)
            title = title_element.text.strip()

            # 提取日期
            date_element = element.find_element(*self.locators.VIDEO_DATE)
            published_date = date_element.text.strip()

            # 提取链接
            link_element = element.find_element(*self.locators.VIDEO_LINK)
            video_url = link_element.get_attribute('href')

            return {
                'title': title,
                'published_date': published_date,
                'url': video_url,
                'year': self._extract_year(published_date)
            }
        except NoSuchElementException as e:
            logger.error(f"提取视频信息时元素未找到: {e}")
            return None

    def _extract_year(self, date_string):
        """从日期字符串中提取年份"""
        import re
        # 匹配 "2024-01-01" 或 "2024年01月01日" 格式
        year_match = re.search(r'(\d{4})', date_string)
        if year_match:
            return int(year_match.group(1))
        return None

    def _load_more_videos(self):
        """加载更多视频"""
        try:
            # 先尝试点击"加载更多"按钮
            try:
                load_more = self.driver.find_element(*self.locators.LOAD_MORE_BUTTON)
                self.driver.execute_script("arguments[0].click();", load_more)
                time.sleep(2)
                return True
            except NoSuchElementException:
                pass

            # 如果没有加载更多按钮，尝试滚动到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # 检查是否有下一页按钮
            try:
                next_page = self.driver.find_element(*self.locators.NEXT_PAGE_BUTTON)
                if next_page.is_enabled():
                    return True
            except NoSuchElementException:
                return False

            return False

        except Exception as e:
            logger.error(f"加载更多视频失败: {e}")
            return False