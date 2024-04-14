import time
from typing import Optional

from PIL import ImageGrab
from pydantic import Field, BaseModel
import pygetwindow as gw
from playwright.sync_api import Browser, sync_playwright
from pygetwindow._pygetwindow_win import Win32Window


class GetScreen(BaseModel):
    @classmethod
    def from_exist_window(self, window_title: str):
        try:
            window = gw.getWindowsWithTitle(window_title)[0]  # type: Win32Window
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.1)
            x, y = window.topleft
            width, height = window.size
            bbox = (x, y, x + width, y + height)
            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot, x, y
        except Exception:
            return None, None, None

    @classmethod
    def from_new_window(cls, target_url: str):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                java_script_enabled=True,
                accept_downloads=False,
                has_touch=False,
                is_mobile=False,
                locale="zh-TW",
                permissions=[],
                geolocation=None,
                color_scheme="light",
                timezone_id="Asia/Shanghai",
            )
            page = context.new_page()
            page.goto(target_url)
            screenshot = page.screenshot(path="./data/logs/screenshot.png")
            return screenshot, page, browser
