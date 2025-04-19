import asyncio
import secrets
import datetime

import pytz
import logfire
from adbutils import AdbDevice, adb
from pydantic import Field, BaseModel, model_validator
from adbutils.errors import AdbError
from playwright.async_api import Page

from .utils.config import ImageModel
from .utils.compare import ImageComparison
from .utils.discord import DiscordNotify
from .utils.screenshot import Screenshot, ScreenshotManager


class RemoteController(BaseModel):
    target: str = Field(
        ...,
        description="This field can be either a window title or a URL or cdp url.",
        frozen=True,
        deprecated=False,
    )
    serial: str = Field(
        default="127.0.0.1:16384",
        description="The serial number of the device.",
        examples=["127.0.0.1:16384", "127.0.0.1:16416", "127.0.0.1:16448"],
        frozen=False,
        deprecated=False,
    )
    image_list: list[ImageModel] = Field(
        ...,
        description="The list of images to compare, it should contain path and name.",
        frozen=True,
        deprecated=False,
    )
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

    async def click_button(self, button_x: int, button_y: int, device_details: Screenshot) -> None:
        if button_x and button_y:
            if isinstance(device_details.device, Page):
                await device_details.device.mouse.click(x=button_x, y=button_y)
            else:
                device_details.device.click(x=button_x, y=button_y)

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

                found_result = await image_compare.find()
                if found_result is not None and config_dict.click_this:
                    await self.click_button(
                        button_x=found_result.button_x,
                        button_y=found_result.button_y,
                        device_details=device_details,
                    )

                    if found_result.name_en == "confirm":
                        await self.switch_game(device_details=device_details)

                    await asyncio.sleep(config_dict.delay_after_click)

        except AdbError:
            notify = DiscordNotify(
                title="尊敬的老闆, 發生錯誤!!",
                description="請檢查一下您的模擬器是否有開啟",
                target_image=None,
            )
            await notify.send_notify()
            interval = secrets.randbelow(5)
            logfire.error("Error Occurred, Please check your emulator", _exc_info=True)
            await asyncio.sleep(interval)

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
