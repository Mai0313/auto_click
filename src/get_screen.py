import time

from PIL import ImageGrab
from adbutils import adb
from pydantic import BaseModel
import pygetwindow as gw
from pygetwindow import Win32Window  # noqa: F401 for type hinting
from playwright.sync_api import sync_playwright
from src.types.output_models import DeviceOutput, ShiftPosition


class GetScreen(BaseModel):
    @classmethod
    def from_exist_window(self, window_title: str) -> DeviceOutput:
        """For any window."""
        window = gw.getWindowsWithTitle(window_title)[0]  # type: Win32Window
        if window.isMinimized:
            window.restore()
        window.activate()
        time.sleep(0.1)
        shift_x, shift_y = window.topleft
        width, height = window.size
        bbox = (shift_x, shift_y, shift_x + width, shift_y + height)
        screenshot = ImageGrab.grab(bbox=bbox)
        # For this method, there is always a shift position
        shift_position = ShiftPosition(shift_x=shift_x, shift_y=shift_y)

        screenshot.save("screenshot.png")
        return DeviceOutput(screenshot=screenshot, device=shift_position)

    @classmethod
    def from_adb_device(cls, url: str, serial: str) -> DeviceOutput:
        """For the android device."""
        adb.connect(serial)
        device = adb.device(serial=serial)
        current_app = device.app_current()
        if current_app.package != url:
            # device.app_start(url)
            raise Exception(f"Please make sure you have opened the app: {url}")

        screenshot = device.screenshot()
        return DeviceOutput(screenshot=screenshot, device=device)

    @classmethod
    def from_remote_window(cls, url: str) -> DeviceOutput:
        """For playingwright."""
        with sync_playwright() as p:
            # if "localhost" in url:
            #     browser = p.chromium.connect_over_cdp(url)
            #     contexts = browser.contexts
            #     context = contexts[0]
            #     page = context.pages[0]
            #     screenshot = page.screenshot()
            #     return screenshot, page
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
            page.goto(url)
            screenshot = page.screenshot()
            return DeviceOutput(screenshot=screenshot, device=page)
