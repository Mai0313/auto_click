import asyncio
from pathlib import Path

from PIL import Image, ImageGrab
from adbutils import adb
from pydantic import BaseModel, ConfigDict
from pygetwindow import Win32Window, getWindowsWithTitle
from adbutils._device import AdbDevice
from playwright_stealth import stealth_sync
from playwright.sync_api import Page
from playwright.async_api import Page as APage
from playwright.async_api import async_playwright


class ShiftPosition(BaseModel):
    """Represents a shift in position.

    Attributes:
        shift_x (int): The amount to shift in the x-axis.
        shift_y (int): The amount to shift in the y-axis.
    """

    shift_x: int
    shift_y: int


class Screenshot(BaseModel):
    """Represents a screenshot captured from a device.

    Attributes:
        model_config (ConfigDict): The configuration dictionary for the model.
        screenshot (Union[bytes, Image.Image]): The screenshot image data.
        device (Union[AdbDevice, Page, APage, ShiftPosition]): The device from which the screenshot was captured.

    Methods:
        save: Save the screenshot to a specified path.
        calibrate: Adjust the button center coordinates based on the device
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    screenshot: bytes | Image.Image
    device: AdbDevice | Page | APage | ShiftPosition

    async def save(self, save_path: str) -> str:
        """Asynchronously saves the screenshot to the specified path.

        Args:
            save_path (str): The path where the screenshot will be saved. If the path does not end with ".png", it will be automatically appended.

        Raises:
            TypeError: If the screenshot type is not supported.

        Returns:
            str: The full path where the screenshot was saved.
        """
        output_path = Path(f"{save_path}")
        output_path = output_path.with_suffix(".png")
        if isinstance(self.screenshot, bytes):
            output_path.write_bytes(self.screenshot)
        elif isinstance(self.screenshot, Image.Image):
            self.screenshot.save(output_path)
        else:
            raise TypeError(f"The screenshot type {type(self.screenshot)} is not supported.")
        return output_path.absolute().as_posix()


class ScreenshotManager(BaseModel):
    async def from_window(self, window_title: str) -> Screenshot:
        """Captures a screenshot of the specified window.

        Args:
            window_title (str): The title of the window to capture.

        Returns:
            Screenshot: An object containing the screenshot image and the shift position.

        Raises:
            IndexError: If no window with the specified title is found.

        Notes:
            This method will restore and activate the window if it is minimized.
            It waits for 1 second after activating the window to ensure it is ready for capture.
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

    async def from_adb(self, url: str, serial: str) -> Screenshot:
        """Capture a screenshot from an Android device using ADB.

        Args:
            url (str): The package name of the app to verify.
            serial (str): The serial number of the Android device.

        Returns:
            Screenshot: An instance of the Screenshot class containing the screenshot and device information.

        Raises:
            Exception: If the current app on the device is not the specified URL.
        """
        adb.connect(serial)
        device = adb.device(serial=serial)
        running_app = device.app_current()
        if running_app.package != url:
            raise Exception("The current app is not the specified URL")
        screenshot = device.screenshot()
        return Screenshot(screenshot=screenshot, device=device)

    async def from_browser(self, url: str) -> Screenshot:
        """Takes a screenshot of a webpage from a given URL using an automated browser.

        Args:
            url (str): The URL of the webpage to take a screenshot of.

        Returns:
            Screenshot: An object containing the screenshot and the device (page) used to capture it.

        Raises:
            playwright.async_api.Error: If there is an error during the browser automation process.

        Notes:
            - This function uses Playwright to automate the browser.
            - The browser is launched in headless mode.
            - Various arguments and context options are set to avoid detection by anti-bot mechanisms.
            - The function sets a specific user agent and other browser context options.
            - The function uses a stealth mode to further avoid detection.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel="chrome",
                headless=True,
                # 反反爬蟲
                args=[
                    "--disable-blink-features=AutomationControlled",  # 移除部份自動化標記
                    "--disable-infobars",  # 移除「Chrome正被自動化測試軟體控制」等提示
                    "--disable-dev-shm-usage",
                ],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                java_script_enabled=True,
                accept_downloads=False,
                has_touch=False,
                is_mobile=False,
                locale="en-US",
                permissions=[],
                geolocation=None,
                color_scheme="light",
                timezone_id="Asia/Shanghai",
                viewport={"width": 800, "height": 800},
            )
            # 反反爬蟲
            stealth_sync(context)
            page = await context.new_page()
            await page.goto(url)
            screenshot = await page.screenshot()
            return Screenshot(screenshot=screenshot, device=page)
