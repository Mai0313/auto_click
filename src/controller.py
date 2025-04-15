import asyncio
import secrets
import datetime

import pytz
import logfire
from adbutils import AdbDevice, adb
from pydantic import Field, model_validator
from adbutils.errors import AdbError
from playwright.async_api import Page

from .compare import ImageComparison
from .screenshot import Screenshot, ScreenshotManager
from .types.config import ConfigModel
from .types.output import FoundPosition
from .utils.discord_notify import DiscordNotify


class RemoteController(ConfigModel):
    found_result: FoundPosition = Field(default_factory=FoundPosition)
    screenshot_manager: ScreenshotManager = Field(default_factory=ScreenshotManager)
    notified_count: int = Field(
        default=0,
        title="Notified",
        description="Whether the notification has been sent",
        frozen=False,
        deprecated=False,
    )

    @model_validator(mode="after")
    def _connect2adb(self) -> "RemoteController":
        adb.connect(addr=self.serial, timeout=3.0)
        device = adb.device(serial=self.serial)
        running_app = device.app_current()
        if running_app.package != self.target:
            raise AdbError("No devices running the target app were found.")
        return self

    async def get_screenshot(self) -> Screenshot:
        if self.target.startswith("http"):
            screenshot = await self.screenshot_manager.from_browser(url=self.target)
        else:
            screenshot = await self.screenshot_manager.from_adb(serial=self.serial)
        return screenshot

    async def click_button(self, device_details: Screenshot) -> None:
        if self.found_result.button_x and self.found_result.button_y:
            if isinstance(device_details.device, Page):
                await device_details.device.mouse.click(
                    x=self.found_result.button_x, y=self.found_result.button_y
                )
            else:
                device_details.device.click(
                    x=self.found_result.button_x, y=self.found_result.button_y
                )

    async def switch_game(self, device_details: Screenshot) -> None:
        current_hour = datetime.datetime.now(pytz.timezone("Asia/Taipei")).hour
        if (21 <= current_hour < 24) or (0 <= current_hour < 1):
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

            notify = DiscordNotify(
                title="老闆!! 我已經幫您打完王朝了 目前已切換至五對五",
                description="王朝已完成",
                target_image=device_details.screenshot,
            )
            self.notified_count += 1
            logfire.info("Game has been switched.")
        else:
            notify = DiscordNotify(
                title="老闆!! 我已經幫您打完王朝/五對五了",
                description="五對五已完成",
                target_image=device_details.screenshot,
            )
            self.notified_count += 1
            logfire.info("The task has been completed.")
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

                    if self.found_result.name_en == "confirm":
                        await self.switch_game(device_details=device_details)

                    await asyncio.sleep(config_dict.delay_after_click)

        except AdbError:
            notify = DiscordNotify(
                title="尊敬的老闆, 發生錯誤!!",
                description="請檢查一下您的模擬器是否有開啟",
                target_image=None,
            )
            await notify.send_notify()
            logfire.error("Error Occurred, Please check your emulator", _exc_info=True)

        except Exception as e:
            notify = DiscordNotify(
                title="尊敬的老闆, 發生錯誤!!",
                description=f"採棉花的過程中發生錯誤，請您檢查一下 {e!s}",
                target_image=None,
            )
            await notify.send_notify()
            interval = secrets.randbelow(5)
            logfire.error(f"Error Occurred, Retrying in {interval} seconds", _exc_info=True)
            await asyncio.sleep(interval)

    async def start(self) -> None:
        while True:
            await self.run()
            if self.notified_count > 1:
                break
