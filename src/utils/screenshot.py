import io

from PIL import Image
from adbutils import adb
from pydantic import BaseModel, ConfigDict
from adbutils._device import AdbDevice
from playwright_stealth import stealth_sync
from playwright.async_api import Page as APage
from playwright.async_api import async_playwright


class Screenshot(BaseModel):
    """Represents a screenshot captured from a device.

    Attributes:
        screenshot (Image.Image): The screenshot image data.
        device (AdbDevice | APage): The device from which the screenshot was captured.

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    screenshot: Image.Image
    device: AdbDevice | APage


class ScreenshotManager(BaseModel):
    async def from_adb(self, serial: str) -> Screenshot:
        """Capture a screenshot from an Android device using ADB.

        Args:
            serial (str): The serial number of the Android device.

        Returns:
            Screenshot: An instance of the Screenshot class containing the screenshot and device information.

        """
        # Reuse existing connection if possible
        try:
            device = adb.device(serial=serial)
            screenshot = device.screenshot()
            return Screenshot(screenshot=screenshot, device=device)
        except Exception:
            # If we fail to get the device directly, try to connect first
            adb.connect(addr=serial, timeout=3.0)
            device = adb.device(serial=serial)
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
            screenshot_bytes = await page.screenshot()
            screenshot = Image.open(io.BytesIO(screenshot_bytes))
            return Screenshot(screenshot=screenshot, device=page)
