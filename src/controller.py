import asyncio
import secrets
import datetime

import pytz
import logfire
from adbutils import AdbDevice
from pydantic import Field, model_validator
import pyautogui
from playwright.sync_api import Page
from playwright.async_api import Page as APage

from .compare import ImageComparison
from .screenshot import GetScreen
from .types.config import ConfigModel
from .types.database import DatabaseConfig
from .utils.get_serial import ADBDeviceManager
from .types.output_models import Screenshot, FoundPosition, ShiftPosition
from .notifications.discord_notify import DiscordNotify


class RemoteController(ConfigModel):
    target_serial: str = Field(default="", description="The serial number of the target device.")
    found_result: FoundPosition = Field(default_factory=FoundPosition)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.now)

    win: int = Field(default=0, title="Win", description="Number of wins")
    lose: int = Field(default=0, title="Lose", description="Number of loses")
    game_switched: bool = Field(
        default=False, title="Game Switched", description="Whether the game has been switched"
    )
    notified_count: int = Field(
        default=0, title="Notified", description="Whether the notification has been sent"
    )

    @model_validator(mode="after")
    def _init_serial(self) -> "RemoteController":
        adb_manager = ADBDeviceManager(host="127.0.0.1", ports=self.serials, target=self.target)
        apps = adb_manager.get_correct_serial()
        self.target_serial = apps.serial
        return self

    async def get_screenshot(self) -> Screenshot:
        if self.target.startswith("http"):
            return await GetScreen.from_remote_window(url=self.target)
        if self.target.startswith("com"):
            return await GetScreen.from_adb_device(url=self.target, serial=self.target_serial)
        # 返回 screenshot 和 shift_position，而不是 device
        return await GetScreen.from_exist_window(window_title=self.target)

    async def click_button(self, device_details: Screenshot) -> None:
        if self.found_result.button_x and self.found_result.button_y:
            if isinstance(device_details.device, Page):
                device_details.device.mouse.click(
                    x=self.found_result.button_x, y=self.found_result.button_y
                )
            elif isinstance(device_details.device, APage):
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
        total_games = self.win + self.lose
        current_hour = datetime.datetime.now(pytz.timezone("Asia/Taipei")).hour
        if 22 <= current_hour < 24:
            return
        if isinstance(device_details.device, AdbDevice):
            if self.game_switched is False:
                logfire.warn("Switching Game!!")
                device_details.device.click(x=1600, y=630)
                await asyncio.sleep(5)
                device_details.device.click(x=1600, y=830)
                await asyncio.sleep(5)
                device_details.device.click(x=1600, y=930)
                await asyncio.sleep(5)
                self.game_switched = True

                logfire.info("Game has been switched.")
                notify = DiscordNotify(
                    title="老闆!! 我已經幫您打完王朝了 目前已切換至五對五",
                    description=f"王朝已完成\n目前勝場: {self.win}\n目前敗場: {self.lose}\n總場數: {total_games}",
                    target_image=device_details.screenshot,
                )
                await notify.send_notify()
                self.notified_count += 1
            else:
                if self.notified_count == 1:
                    logfire.info("Game has been completed.")
                    notify = DiscordNotify(
                        title="老闆!! 我已經幫您打完王朝/五對五了",
                        description=f"五對五已完成\n目前勝場: {self.win}\n目前敗場: {self.lose}\n總場數: {total_games}",
                        target_image=device_details.screenshot,
                    )
                    await notify.send_notify()

    async def start(self) -> None:
        while True:
            try:
                device_details = await self.get_screenshot()
                for config_dict in self.image_list:
                    image_compare = ImageComparison(
                        image_cfg=config_dict,
                        screenshot=device_details.screenshot,
                        device=device_details.device,
                    )

                    self.found_result = await image_compare.find(
                        vertical_align=config_dict.vertical,
                        horizontal_align=config_dict.horizontal,
                    )
                    if self.auto_click and config_dict.click_this:
                        await self.click_button(device_details=device_details)

                        if self.found_result.found_button_name_en == "confirm":
                            await self.switch_game(device_details=device_details)

                        await asyncio.sleep(config_dict.delay_after_click)

            except Exception as e:
                _random_interval = secrets.randbelow(self.random_interval)
                logfire.error(
                    f"Error Occurred, Retrying in {_random_interval} seconds", _exc_info=True
                )
                notify = DiscordNotify(
                    title="尊敬的老闆, 發生錯誤!!",
                    description=f"採棉花的過程中發生錯誤，請您檢查一下 {e!s}",
                    target_image=None,
                )
                await notify.send_notify()
                await asyncio.sleep(_random_interval)
            _random_interval = secrets.randbelow(self.random_interval)
            await asyncio.sleep(_random_interval)
