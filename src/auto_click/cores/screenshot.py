import asyncio

from PIL import Image, ImageGrab
from adbutils import adb
from pydantic import BaseModel, ConfigDict
from pygetwindow import Win32Window, getWindowsWithTitle
from adbutils._device import AdbDevice
from playwright_stealth import Stealth
from playwright.async_api import Page, Browser, Playwright, BrowserContext, async_playwright


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
        device (Union[AdbDevice, Page, ShiftPosition]): The device from which the screenshot was captured.

    Methods:
        save: Save the screenshot to a specified path.
        calibrate: Adjust the button center coordinates based on the device
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    screenshot: bytes | Image.Image
    device: AdbDevice | Page | ShiftPosition


class ScreenshotManager(BaseModel):
    """Manager for capturing screenshots from different sources.

    Attributes:
        _playwright (Playwright | None): Cached Playwright instance.
        _browser (Browser | None): Cached browser instance for reuse.
        _context (BrowserContext | None): Cached browser context for reuse.
        _browser_page (Page | None): Cached browser page instance for reuse.
        _adb_device (AdbDevice | None): Cached ADB device instance for reuse.
        _adb_serial (str | None): Cached serial number for ADB device.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    _playwright: Playwright | None = None
    _browser: Browser | None = None
    _context: BrowserContext | None = None
    _browser_page: Page | None = None
    _adb_device: AdbDevice | None = None
    _adb_serial: str | None = None

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
            It waits for 0.1 second after activating the window to ensure it is ready for capture.
        """
        window: Win32Window = getWindowsWithTitle(window_title)[0]
        if window.isMinimized:
            window.restore()
        window.activate()
        await asyncio.sleep(0.1)
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

        Notes:
            ADB device instance is cached and reused across calls for better performance.
        """
        # Reuse existing ADB connection if serial matches
        if self._adb_device is None or self._adb_serial != serial:
            adb.connect(serial)
            self._adb_device = adb.device(serial=serial)
            self._adb_serial = serial

        running_app = self._adb_device.app_current()
        if running_app.package != url:
            raise Exception("The current app is not the specified URL")
        screenshot = self._adb_device.screenshot()
        return Screenshot(screenshot=screenshot, device=self._adb_device)

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
            - Browser instance is reused across calls for better performance.
        """
        # Initialize browser on first call
        if self._browser_page is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                channel="chrome",
                headless=True,
                # 反反爬蟲
                args=[
                    "--disable-blink-features=AutomationControlled",  # 移除部份自動化標記
                    "--disable-infobars",  # 移除「Chrome正被自動化測試軟體控制」等提示
                    "--disable-dev-shm-usage",
                ],
            )
            self._context = await self._browser.new_context(
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
            stealth = Stealth(init_scripts_only=True)
            await stealth.apply_stealth_async(self._context)
            self._browser_page = await self._context.new_page()

        # Navigate to URL and take screenshot
        await self._browser_page.goto(url)
        screenshot = await self._browser_page.screenshot()
        return Screenshot(screenshot=screenshot, device=self._browser_page)

    async def cleanup(self) -> None:
        """Cleanup browser and ADB resources.

        Should be called when the ScreenshotManager is no longer needed.
        """
        # Cleanup browser resources
        if self._browser_page is not None:
            await self._browser_page.close()
            self._browser_page = None
        if self._context is not None:
            await self._context.close()
            self._context = None
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

        # Cleanup ADB resources
        if self._adb_device is not None:
            self._adb_device = None
            self._adb_serial = None
