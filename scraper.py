"""
B站视频数据提取模块
从B站创作者中心提取视频数据
"""

import json
import os
import platform
import re
import time
from datetime import datetime
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators import Locators


class VideoCache:
    """视频数据缓存管理器"""
    
    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    CACHE_FILE = os.path.join(CACHE_DIR, "videos_cache.json")
    
    @classmethod
    def _ensure_cache_dir(cls) -> None:
        """确保缓存目录存在"""
        if not os.path.exists(cls.CACHE_DIR):
            os.makedirs(cls.CACHE_DIR)
    
    @classmethod
    def save_videos(cls, videos: List[Dict]) -> bool:
        """保存视频数据到缓存"""
        try:
            cls._ensure_cache_dir()
            
            # 准备可序列化的数据（不含 element 对象）
            cacheable_videos = []
            for video in videos:
                cacheable = {
                    'bvid': video.get('bvid', ''),
                    'title': video.get('title', ''),
                    'date': video.get('date', ''),
                    'url': video.get('url', ''),
                    'page': video.get('page', 1),  # 保存视频所在页码
                    'cached_at': datetime.now().isoformat()
                }
                cacheable_videos.append(cacheable)
            
            cache_data = {
                'version': 1,
                'cached_at': datetime.now().isoformat(),
                'count': len(cacheable_videos),
                'videos': cacheable_videos
            }
            
            with open(cls.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存缓存失败: {e}")
            return False
    
    @classmethod
    def load_videos(cls) -> Optional[List[Dict]]:
        """从缓存加载视频数据"""
        try:
            if not os.path.exists(cls.CACHE_FILE):
                return None
            
            with open(cls.CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            videos = cache_data.get('videos', [])
            
            # 还原为标准视频格式（不含 element）
            for video in videos:
                video['has_action_button'] = False
                video['element_index'] = -1
                video['element'] = None
                video['page'] = video.get('page', 1)  # 确保 page 字段存在
            
            return videos
        except Exception as e:
            print(f"加载缓存失败: {e}")
            return None
    
    @classmethod
    def clear_cache(cls) -> bool:
        """清除缓存"""
        try:
            if os.path.exists(cls.CACHE_FILE):
                os.remove(cls.CACHE_FILE)
                print("缓存已清除")
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False
    
    @classmethod
    def get_cache_info(cls) -> Optional[Dict]:
        """获取缓存信息"""
        try:
            if not os.path.exists(cls.CACHE_FILE):
                return None
            
            with open(cls.CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            return {
                'count': cache_data.get('count', 0),
                'cached_at': cache_data.get('cached_at', '未知')
            }
        except Exception:
            return None


class BilibiliScraper:
    """B站视频数据提取器"""
    
    def __init__(self, headless: bool = False):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.base_url = "https://member.bilibili.com/platform/upload-manager/article"
    
    def setup_driver(self, force_new: bool = False) -> None:
        """设置WebDriver
        
        Args:
            force_new: 强制启动新的Chrome浏览器
        """
        if not force_new and self._try_connect_existing_chrome():
            return
        
        print("启动新的Chrome浏览器...")
        self._launch_new_chrome()
    
    def _try_connect_existing_chrome(self) -> bool:
        """尝试连接到现有的Chrome会话"""
        try:
            import os
            user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
            
            if not os.path.exists(user_data_dir):
                return False
            
            lock_file = os.path.join(user_data_dir, "SingletonLock")
            if not os.path.exists(lock_file):
                return False
            
            print("检测到现有Chrome会话，尝试连接...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 10)
                print("成功连接到现有Chrome会话")
                self.driver.current_url
                print("Chrome会话连接正常")
                return True
            except Exception as e:
                print(f"连接现有Chrome会话失败: {e}")
                return False
                
        except Exception as e:
            print(f"检测现有Chrome会话时出错: {e}")
            return False
    
    def _launch_new_chrome(self) -> None:
        """启动新的Chrome浏览器"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        import os
        user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        system = platform.system()
        if system == "Windows":
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        elif system == "Darwin":
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        else:
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("ChromeDriver启动成功")
        except Exception as e:
            print(f"系统ChromeDriver启动失败: {e}")
            raise e
        
        self.wait = WebDriverWait(self.driver, 10)
    
    def check_login(self) -> bool:
        """检查登录状态"""
        try:
            self.driver.get(self.base_url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            if "login" in current_url.lower() or "passport" in current_url.lower():
                print("检测到需要登录，请在浏览器中手动完成登录...")
                input("登录完成后，按回车键继续...")
                
                self.driver.get(self.base_url)
                time.sleep(3)
                current_url = self.driver.current_url
                if "login" in current_url.lower() or "passport" in current_url.lower():
                    print("登录验证失败，请重新尝试")
                    return False
                else:
                    print("登录成功")
            
            return True
            
        except Exception as e:
            print(f"登录检查失败: {e}")
            return False
    
    def extract_all_videos(self, use_cache: bool = True, save_cache: bool = True) -> List[Dict]:
        """提取所有视频数据（处理分页）
        
        Args:
            use_cache: 是否优先使用缓存
            save_cache: 是否保存新抓取的缓存
        """
        # 尝试从缓存加载
        if use_cache:
            cached_videos = VideoCache.load_videos()
            if cached_videos:
                return cached_videos
        
        all_videos = []
        
        if not self.check_login():
            print("登录失败")
            return all_videos
        
        page = 1
        while True:            
            # 等待视频卡片加载
            time.sleep(2)
            
            # 提取当前页视频（传入页码）
            videos = self._extract_page_videos(page)
            
            all_videos.extend(videos)
            
            # 检查是否有下一页
            next_btn = self._get_next_page_button()
            if not next_btn:
                break
            
            page += 1
            self._click_next_page()
            time.sleep(2)
        
        # 保存缓存
        if save_cache and all_videos:
            VideoCache.save_videos(all_videos)
            print(f"提取完成：{len(all_videos)} 个视频")
        
        return all_videos
    
    def _extract_page_videos(self, page: int = 1) -> List[Dict]:
        """提取当前页的视频数据"""
        videos = []
        
        video_elements = self._find_video_elements()
        if not video_elements:
            return videos
        
        for i, element in enumerate(video_elements):
            try:
                video_data = self._extract_video_data(element, i, page)
                if video_data:
                    videos.append(video_data)
            except Exception as e:
                continue
        
        return videos
    
    def _find_video_elements(self) -> List:
        """查找视频元素"""
        for selector in Locators.VIDEO_ITEM_SELECTORS:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements
            except Exception:
                continue
        return []
    
    def _extract_video_data(self, element, index: int, page: int = 1) -> Optional[Dict]:
        """提取单个视频的数据"""
        try:
            # 提取标题
            title = "无标题"
            for selector in Locators.VIDEO_TITLE_SELECTORS:
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip() or title_element.get_attribute('textContent').strip()
                    if title:
                        break
                except NoSuchElementException:
                    continue
            
            # 提取日期
            date = ""
            for selector in Locators.VIDEO_DATE_SELECTORS:
                try:
                    date_element = element.find_element(By.CSS_SELECTOR, selector)
                    date = date_element.text.strip()
                    if date:
                        break
                except NoSuchElementException:
                    continue
            
            # 提取视频链接
            url = ""
            for selector in Locators.VIDEO_LINK_SELECTORS:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, selector)
                    href = link_element.get_attribute('href') or ""
                    if href and 'bilibili.com/video' in href:
                        url = href
                        break
                except NoSuchElementException:
                    continue
            
            # 提取BV号
            bvid = ""
            if url:
                match = re.search(r'BV[\w]+', url)
                if match:
                    bvid = match.group(0)
            
            # 检查是否有操作按钮
            has_action_button = False
            for selector in Locators.ACTION_BUTTON_SELECTORS:
                try:
                    action_btn = element.find_element(By.CSS_SELECTOR, selector)
                    if action_btn.is_displayed():
                        has_action_button = True
                        break
                except NoSuchElementException:
                    continue
            
            return {
                'bvid': bvid,
                'title': title,
                'date': date,
                'url': url,
                'has_action_button': has_action_button,
                'element_index': index,
                'page': page,  # 记录视频所在页码
                'element': element
            }
            
        except Exception as e:
            print(f"提取视频数据时发生错误: {e}")
            return None
    
    def _get_next_page_button(self):
        """获取下一页按钮"""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, Locators.NEXT_PAGE_BUTTON)
        except NoSuchElementException:
            return None
    
    def _click_next_page(self) -> bool:
        """点击下一页"""
        try:
            next_btn = self.driver.find_element(By.CSS_SELECTOR, Locators.NEXT_PAGE_BUTTON)
            if next_btn.is_enabled() and next_btn.is_displayed():
                next_btn.click()
                print("已点击下一页")
                return True
        except Exception as e:
            print(f"点击下一页失败: {e}")
        return False
    
    def _go_to_page(self, target_page: int) -> bool:
        """跳转到指定页码"""
        if target_page <= 1:
            return True
        
        print(f"正在跳转到第 {target_page} 页...")
        try:
            time.sleep(1)
            
            # 方法1: 直接使用页码跳转输入框（最快）
            try:
                page_input = self.driver.find_element(By.CSS_SELECTOR, ".bcc-pagination-elevator input")
                page_input.clear()
                page_input.send_keys(str(target_page))
                time.sleep(0.3)
                page_input.send_keys(Keys.ENTER)
                time.sleep(2)
                print(f"已通过输入框跳转到第 {target_page} 页")
                return True
            except:
                pass
            
            # 方法2: 点击页码数字（如果可见）
            try:
                page_link = self.driver.find_element(By.XPATH, f"//li[contains(@class,'bcc-pagination-item')]//a[text()='{target_page}']")
                page_link.click()
                time.sleep(2)
                print(f"已点击页码跳转到第 {target_page} 页")
                return True
            except:
                pass
            
            # 方法3: 从第1页开始逐页跳转（最后备选）
            print("正在逐页跳转...")
            # 先回到第一页
            try:
                first_page = self.driver.find_element(By.XPATH, "//li[contains(@class,'bcc-pagination-item')]//a[text()='1']")
                first_page.click()
                time.sleep(2)
            except:
                pass
            
            for page in range(1, target_page):
                next_btn = self.driver.find_element(By.CSS_SELECTOR, Locators.NEXT_PAGE_BUTTON)
                if next_btn.is_enabled() and next_btn.is_displayed():
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(1.5)
                else:
                    print(f"无法跳转到第 {page + 1} 页")
                    return False
            print(f"已跳转到第 {target_page} 页")
            return True
        except Exception as e:
            print(f"跳转页面失败: {e}")
            return False
    
    def _find_video_card_on_current_page(self, title: str) -> Optional:
        """在当前页查找视频卡片（不翻页）"""
        time.sleep(1.5)  # 等待页面加载
        
        # 尝试多个视频卡片选择器
        video_cards = []
        for selector in Locators.VIDEO_ITEM_SELECTORS:
            try:
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    video_cards = cards
                    break
            except:
                continue
        
        if not video_cards:
            print(f"  ❌ 未找到视频卡片")
            return None
        
        # 尝试多个标题选择器
        for card in video_cards:
            for title_selector in Locators.VIDEO_TITLE_SELECTORS:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, title_selector)
                    card_title = title_elem.text.strip() or title_elem.get_attribute('textContent').strip()
                    if title in card_title or card_title in title:
                        print(f"  ✓ 找到视频: '{card_title}'")
                        return card
                except:
                    continue
        
        # 没找到，打印前几个标题帮助调试
        print(f"  ❌ 未找到 '{title}'，当前页视频列表:")
        for i, card in enumerate(video_cards[:5]):
            for title_selector in Locators.VIDEO_TITLE_SELECTORS:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, title_selector)
                    card_title = title_elem.text.strip() or title_elem.get_attribute('textContent').strip()
                    print(f"    {i+1}. {card_title}")
                    break
                except:
                    continue
        
        return None
    
    def _check_video_cache(self) -> bool:
        """检查视频缓存是否有效，返回True表示有效，False表示需要重新提取"""
        cached_videos = VideoCache.load_videos()
        if not cached_videos:
            return False
        
        cached_count = len(cached_videos)
        
        # 从页码栏提取全部视频总数
        total_on_page = 0
        try:
            pagination_text = self.driver.find_element(By.CSS_SELECTOR, ".bcc-pagination-total").text
            # 解析 "共6页 / 58个，"
            import re
            match = re.search(r'共\d+页\s*/\s*(\d+)个', pagination_text)
            if match:
                total_on_page = int(match.group(1))
            else:
                # 备用解析方式
                match = re.search(r'(\d+)个', pagination_text)
                if match:
                    total_on_page = int(match.group(1))
        except Exception:
            pass
        
        if total_on_page > 0 and cached_count != total_on_page:
            print(f"⚠️ 缓存失效：缓存 {cached_count} 个，页面 {total_on_page} 个，请重新提取稿件！")
            return False
        
        return True
    
    def _click_visibility_option(self, is_private: bool) -> bool:
        """点击可见范围菜单并设置隐私选项

        Args:
            is_private: True=私密, False=公开
        """
        radio_value = '1' if is_private else '0'

        # 点击"可见范围"菜单项
        try:
            visibility_items = self.driver.find_elements(By.CSS_SELECTOR, Locators.MORE_MENU_ITEM)
            for item in visibility_items:
                if "可见范围" in item.text.strip():
                    self.driver.execute_script("arguments[0].click();", item)
                    break
            else:
                visibility_btn = self.driver.find_element(By.XPATH, Locators.PRIVACY_BUTTON_IN_MENU)
                self.driver.execute_script("arguments[0].click();", visibility_btn)
            time.sleep(1)
        except NoSuchElementException:
            print("未找到可见范围按钮")
            self.driver.find_element(By.CSS_SELECTOR, "body").click()
            return False

        # 在弹框中选择私密/公开
        try:
            time.sleep(0.5)
            dialog = self.driver.find_element(By.CSS_SELECTOR, Locators.VISIBILITY_DIALOG)

            radio = dialog.find_element(By.CSS_SELECTOR, f"input[type='radio'][value='{radio_value}']")
            self.driver.execute_script("arguments[0].click();", radio)
            time.sleep(0.3)

            confirm_btn = dialog.find_element(By.CSS_SELECTOR, Locators.DIALOG_CONFIRM_BUTTON)
            self.driver.execute_script("arguments[0].click();", confirm_btn)
            time.sleep(1)
            return True
        except NoSuchElementException as e:
            print(f"未找到选项: {e}")
            try:
                self.driver.find_element(By.XPATH, "//button[contains(text(), '取消')]").click()
            except:
                pass
            return False

    def _open_visibility_menu(self, video_card) -> bool:
        """打开视频卡片的可见范围下拉菜单

        Args:
            video_card: 视频卡片元素
        Returns:
            是否成功打开菜单
        """
        # 滚动到元素可见
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", video_card)
        time.sleep(0.5)

        # 找到more-btn并hover
        more_btn = video_card.find_element(By.CSS_SELECTOR, "a.more-btn")
        ActionChains(self.driver).move_to_element(more_btn).perform()
        time.sleep(1)
        return True

    def set_video_private(self, video_element) -> bool:
        """设置视频为私密"""
        try:
            self._open_visibility_menu(video_element)
            return self._click_visibility_option(is_private=True)
        except Exception as e:
            print(f"设置私密失败: {e}")
            return False
    
    def set_video_public(self, video_element) -> bool:
        """设置视频为公开"""
        try:
            self._open_visibility_menu(video_element)
            return self._click_visibility_option(is_private=False)
        except Exception as e:
            print(f"设置公开失败: {e}")
            return False
    
    def _ensure_on_video_page(self) -> bool:
        """确保在视频列表页面"""
        if "upload-manager" not in self.driver.current_url:
            print("正在跳转到视频列表页面...")
            self.driver.get(self.base_url)
            time.sleep(3)
        return True

    def _get_video_page_from_cache(self, title: str) -> int:
        """从缓存获取视频所在页码

        Args:
            title: 视频标题
        Returns:
            页码，默认为1
        """
        cached_videos = VideoCache.load_videos()
        if not cached_videos:
            return 1

        for video in cached_videos:
            video_title = video.get('title', '')
            if title in video_title or video_title in title:
                page = video.get('page', 1)
                print(f"从缓存获取: 视频在第 {page} 页")
                return page
        return 1

    def set_video_private_by_title(self, title: str) -> bool:
        """根据标题设置视频为私密"""
        try:
            self._ensure_on_video_page()

            # 检查缓存是否有效
            cached_videos = VideoCache.load_videos()
            if cached_videos and not self._check_video_cache():
                print("❌ 缓存失效，无法设置私密，请先重新提取稿件！")
                return False

            # 跳转到视频所在页码
            video_page = self._get_video_page_from_cache(title)
            if video_page > 1:
                self._go_to_page(video_page)

            # 在当前页查找视频卡片
            print(f"正在第 {video_page} 页查找视频: {title}")
            video_card = self._find_video_card_on_current_page(title)
            if not video_card:
                return False

            # 打开菜单并设置私密
            self._open_visibility_menu(video_card)
            return self._click_visibility_option(is_private=True)

        except Exception as e:
            print(f"设置私密失败: {e}")
            return False
    
    def set_video_public_by_title(self, title: str) -> bool:
        """根据标题设置视频为公开"""
        try:
            self._ensure_on_video_page()

            # 检查缓存是否有效
            cached_videos = VideoCache.load_videos()
            if cached_videos and not self._check_video_cache():
                print("❌ 缓存失效，无法设置公开，请先重新提取稿件！")
                return False

            # 跳转到视频所在页码
            video_page = self._get_video_page_from_cache(title)
            if video_page > 1:
                self._go_to_page(video_page)

            # 在当前页查找视频卡片
            print(f"正在第 {video_page} 页查找视频: {title}")
            video_card = self._find_video_card_on_current_page(title)
            if not video_card:
                return False

            # 打开菜单并设置公开
            self._open_visibility_menu(video_card)
            return self._click_visibility_option(is_private=False)

        except Exception as e:
            print(f"设置公开失败: {e}")
            return False
    
    def close(self) -> None:
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.wait = None
