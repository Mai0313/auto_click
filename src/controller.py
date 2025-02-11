import asyncio
import secrets
import datetime

import pytz
import logfire
from adbutils import AdbDevice
from pydantic import Field, computed_field
import pyautogui
from playwright.async_api import Page

from .compare import ImageComparison
from .screenshot import Screenshot, ShiftPosition, ScreenshotManager
from .types.config import ConfigModel

# from .types.database import DatabaseConfig
from .utils.get_serial import ADBDeviceManager
from .types.output_models import FoundPosition
from .notifications.discord_notify import DiscordNotify


class RemoteController(ConfigModel):
    found_result: FoundPosition = Field(default_factory=FoundPosition)
    screenshot_manager: ScreenshotManager = Field(default_factory=ScreenshotManager)
    notified_count: int = Field(
        default=0, title="Notified", description="Whether the notification has been sent"
    )

    @computed_field
    @property
    def target_serial(self) -> str:
        adb_manager = ADBDeviceManager(host="127.0.0.1", ports=self.serials, target=self.target)
        apps = adb_manager.get_correct_serial()
        return apps.serial

    @computed_field
    @property
    def determine_if_change_needed(self) -> bool:
        current_hour = datetime.datetime.now(pytz.timezone("Asia/Taipei")).hour
        return (22 <= current_hour < 24) or (0 <= current_hour < 1)

    async def get_screenshot(self) -> Screenshot:
        if self.target.startswith("http"):
            screenshot = await self.screenshot_manager.from_browser(url=self.target)
            return screenshot
        if self.target.startswith("com"):
            screenshot = await self.screenshot_manager.from_adb(
                url=self.target, serial=self.target_serial
            )
            return screenshot
        # 返回 screenshot 和 shift_position，而不是 device
        screenshot = await self.screenshot_manager.from_window(window_title=self.target)
        return screenshot

    async def click_button(self, device_details: Screenshot) -> None:
        if self.found_result.button_x and self.found_result.button_y:
            if isinstance(device_details.device, Page):
                await device_details.device.mouse.click(
                    x=self.found_result.button_x, y=self.found_result.button_y
                )
            elif isinstance(device_details.device, AdbDevice):
                device_details.device.click(
                    x=self.found_result.button_x, y=self.found_result.button_y
                )
            elif isinstance(device_details.device, ShiftPosition):
                await self.found_result.calibrate(
                    shift_x=device_details.device.shift_x, shift_y=device_details.device.shift_y
                )
                pyautogui.moveTo(x=self.found_result.button_x, y=self.found_result.button_y)
                pyautogui.click()
            logfire.info(
                f"Found {self.found_result.found_button_name_cn}",
                button_x=self.found_result.button_x,
                button_y=self.found_result.button_y,
                button_name_en=self.found_result.found_button_name_en,
                button_name_cn=self.found_result.found_button_name_cn,
            )

    async def switch_game(self, device_details: Screenshot) -> None:
        if self.determine_if_change_needed:
            return
        if not isinstance(device_details.device, AdbDevice):
            return
        if self.notified_count == 0:
            logfire.warn("Switching Game!!")
            device_details.device.click(x=1600, y=630)
            await asyncio.sleep(5)
            device_details.device.click(x=1600, y=830)
            await asyncio.sleep(5)
            device_details.device.click(x=1600, y=930)
            await asyncio.sleep(5)

            # 也可以透過下面方式來 click
            # device_details.device.shell("input tap 1600 630")

            logfire.info("Game has been switched.")
            notify = DiscordNotify(
                title="老闆!! 我已經幫您打完王朝了 目前已切換至五對五",
                description="王朝已完成",
                target_image=device_details.screenshot,
            )
            self.notified_count += 1
        else:
            logfire.info("Game has been completed.")
            notify = DiscordNotify(
                title="老闆!! 我已經幫您打完王朝/五對五了",
                description="五對五已完成",
                target_image=device_details.screenshot,
            )
        await notify.send_notify()

    async def run(self) -> None:
        try:
            device_details = await self.get_screenshot()
            for config_dict in self.image_list:
                image_compare = ImageComparison(
                    image_cfg=config_dict,
                    screenshot=device_details.screenshot,
                    device=device_details.device,
                )

                self.found_result = await image_compare.find(
                    vertical_align=config_dict.vertical, horizontal_align=config_dict.horizontal
                )
                if self.auto_click and config_dict.click_this:
                    await self.click_button(device_details=device_details)

                    if self.found_result.found_button_name_en == "confirm":
                        if self.notified_count == 1:
                            exit()
                        await self.switch_game(device_details=device_details)

                    await asyncio.sleep(config_dict.delay_after_click)

        except Exception as e:
            notify = DiscordNotify(
                title="尊敬的老闆, 發生錯誤!!",
                description=f"採棉花的過程中發生錯誤，請您檢查一下 {e!s}",
                target_image=None,
            )
            await notify.send_notify()
            _random_interval = secrets.randbelow(self.random_interval)
            logfire.error(
                f"Error Occurred, Retrying in {_random_interval} seconds", _exc_info=True
            )
            await asyncio.sleep(_random_interval)
