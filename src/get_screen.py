import time

from PIL import ImageGrab
import logfire
from adbutils import adb
from pydantic import BaseModel
import pygetwindow as gw
from pygetwindow import Win32Window  # noqa: F401 for type hinting
from playwright.sync_api import sync_playwright

from .types.output_models import Screenshot, ShiftPosition


class GetScreen(BaseModel):
    @classmethod
    def from_exist_window(cls, window_title: str) -> Screenshot:
        """Capture a screenshot from an existing window.

        Args:
            window_title (str): The title of the window to capture.

        Returns:
            Screenshot: An object containing the captured screenshot and the shift position.

        """
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
        logfire.info("Screenshot taken", window_title=window_title)
        return Screenshot(screenshot=screenshot, device=shift_position)

    @classmethod
    def from_adb_device(cls, url: str, serial: str) -> Screenshot:
        """Create a Screenshot object from an Android device using ADB.

        Args:
            url (str): The URL of the app to be opened on the device.
            serial (str): The serial number of the Android device.

        Returns:
            Screenshot: An object containing the screenshot and device information.

        Raises:
            Exception: If the current app on the device is not the specified URL.

        """
        # os.system(f".\\binaries\\adb.exe connect {serial}")
        # commands = ["./binaries/adb.exe", "connect", serial]
        # command_executor = CommandExecutor(commands=commands)
        # command_executor.run()
        adb.connect(serial)
        device = adb.device(serial=serial)
        running_app = device.app_current()
        if running_app.package != url:
            logfire.error(
                "The current app is not the specified URL",
                serial=device.serial,
                app=running_app.package,
                _exc_info=True,
            )
            raise Exception("The current app is not the specified URL")
        screenshot = device.screenshot()
        logfire.info("Screenshot taken", serial=device.serial, game=running_app.package)
        return Screenshot(screenshot=screenshot, device=device)

    @classmethod
    def from_remote_window(cls, url: str) -> Screenshot:
        """Create a screenshot of a remote window using Playwright.

        Args:
            url (str): The URL of the remote window.

        Returns:
            Screenshot: An object containing the screenshot and the page.

        """
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
            page.goto(url)
            screenshot = page.screenshot()
            logfire.info("Screenshot taken", url=url)
            return Screenshot(screenshot=screenshot, device=page)
