from playwright.sync_api import sync_playwright
import time

from conf.logging_config import logger
from tests.utils.page_utils import get_top_frame_content


class HomePage:
    def __init__(self, page):
        self.page = page

    def navigate_to_page(self, target: str):
        """
        在 topFrame 中点击指定名称的链接。

        :param target: 要点击的链接的名称或文本内容。
        """
        try:
            # 等待页面加载稳定
            self.page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)  # 增加一个短暂的等待，确保框架内容已渲染

            logger.info(f"尝试在 topFrame 中点击链接: '{target}'")

            # 使用传入的 target 参数来定位并点击链接
            get_top_frame_content(self.page).get_by_role("link", name=target).click()

            logger.info(f"成功点击链接: '{target}'")

        except Exception as e:
            logger.error(f"点击链接 '{target}' 时发生错误: {e}")
            raise