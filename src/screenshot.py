import asyncio

from PIL import ImageGrab
from adbutils import adb
from pydantic import BaseModel
from pygetwindow import Win32Window, getWindowsWithTitle
from playwright.async_api import async_playwright

from .types.output_models import Screenshot, ShiftPosition


class GetScreen(BaseModel):
    """A class for capturing screenshots from different sources.

    Attributes:
        screenshot (Screenshot): The screenshot object.

    Methods:
        from_exist_window: Capture a screenshot from an existing window.
        from_adb_device: Create a screenshot from an Android device using ADB.
        from_remote_window: Create a screenshot of a remote window using Playwright.
    """

    @classmethod
    async def from_exist_window(cls, window_title: str) -> Screenshot:
        """Capture a screenshot from an existing window.

        Args:
            window_title (str): The title of the window to capture.

        Returns:
            Screenshot: An object containing the captured screenshot and the shift position.

        """
        window: Win32Window = getWindowsWithTitle(window_title)[0]
        if window.isMinimized:
            window.restore()
        window.activate()
        await asyncio.sleep(1)
        shift_x, shift_y = window.topleft
        width, height = window.size
        bbox = (shift_x, shift_y, shift_x + width, shift_y + height)
        screenshot = ImageGrab.grab(bbox=bbox)
        # For this method, there is always a shift position
        shift_position = ShiftPosition(shift_x=shift_x, shift_y=shift_y)
        return Screenshot(screenshot=screenshot, device=shift_position)

    @classmethod
    async def from_adb_device(cls, url: str, serial: str) -> Screenshot:
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
            # TODO: add log here.
            raise Exception("The current app is not the specified URL")
        screenshot = device.screenshot()
        return Screenshot(screenshot=screenshot, device=device)

    @classmethod
    async def from_remote_window(cls, url: str) -> Screenshot:
        """Asynchronously captures a screenshot from a remote window using the provided URL.

        Args:
            url (str): The URL of the remote window to capture the screenshot from.

        Returns:
            Screenshot: An instance of the Screenshot class containing the captured screenshot and the device (page) used.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
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
            page = await context.new_page()
            await page.goto(url)
            screenshot = await page.screenshot()
            return Screenshot(screenshot=screenshot, device=page)
