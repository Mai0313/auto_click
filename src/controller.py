import json
from typing import Union
import asyncio
from pathlib import Path
import secrets
import datetime

import anyio
import pandas as pd
import logfire
from adbutils import AdbDevice
from pydantic import Field, model_validator
import pyautogui
from sqlalchemy import create_engine
from playwright.sync_api import Page
from playwright.async_api import Page as APage

from .compare import ImageComparison
from .screenshot import GetScreen
from .types.config import ConfigModel
from .types.database import DatabaseConfig
from .utils.get_serial import ADBDeviceManager
from .utils.notification import Notification
from .types.output_models import Screenshot, FoundPosition, ShiftPosition


class RemoteController(ConfigModel):
    target_serial: str = Field(default="", description="The serial number of the target device.")
    found_result: FoundPosition = Field(default_factory=FoundPosition)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.now)

    win: int = Field(default=0, title="Win", description="Number of wins")
    lose: int = Field(default=0, title="Lose", description="Number of loses")
    switch_nums: int = Field(default=0, title="Switch", description="Number of switch games")

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

    async def click_button(self, device: Union[Page, APage, AdbDevice, ShiftPosition]) -> None:
        if self.found_result.button_x and self.found_result.button_y:
            if isinstance(device, Page):
                device.mouse.click(x=self.found_result.button_x, y=self.found_result.button_y)
            elif isinstance(device, APage):
                await device.mouse.click(
                    x=self.found_result.button_x, y=self.found_result.button_y
                )
            elif isinstance(device, AdbDevice):
                device.click(x=self.found_result.button_x, y=self.found_result.button_y)
            elif isinstance(device, ShiftPosition):
                await self.found_result.calibrate(shift_x=device.shift_x, shift_y=device.shift_y)
                pyautogui.moveTo(x=self.found_result.button_x, y=self.found_result.button_y)
                pyautogui.click()
            logfire.info(
                f"Found {self.found_result.found_button_name_cn}",
                button_x=self.found_result.button_x,
                button_y=self.found_result.button_y,
                button_name_en=self.found_result.found_button_name_en,
                button_name_cn=self.found_result.found_button_name_cn,
            )

    async def export_win_rate(self) -> None:
        log_path = Path("./logs")
        log_path.mkdir(parents=True, exist_ok=True)
        total_games = self.win + self.lose
        _current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        _current_date = datetime.datetime.now().strftime("%Y%m%d")
        win_lost_dict = {
            "date": _current_date,
            "time": _current_time,
            "win": self.win,
            "lose": self.lose,
            "total": total_games,
            "win_rate": self.win / total_games,
        }
        _start_time_string = self.start_time.strftime("%Y%m%d%H%M%S")
        async with await anyio.open_file(f"./logs/{_start_time_string}.json", "w") as f:
            await f.write(json.dumps(win_lost_dict))
        if self.save2db:
            try:
                engine = create_engine(self.database.postgres.postgres_dsn, echo=True)
                data = pd.DataFrame([win_lost_dict])
                data.to_sql(
                    name="all_star_match_history", con=engine, if_exists="append", index=False
                )
            except Exception:
                logfire.error("Error Occurred while saving to database", _exc_info=True)

    async def count_win_rate(self) -> None:
        conditions = ["win", "lose"]
        button_name = self.found_result.found_button_name_en
        if button_name in conditions:
            if button_name == "win":
                self.win += 1
                await self.export_win_rate()
            elif button_name == "lose":
                self.lose += 1
                await self.export_win_rate()

    async def switch_game(self, device: Union[Page, APage, AdbDevice, ShiftPosition]) -> None:
        if isinstance(device, AdbDevice) and self.switch_nums == 0:
            logfire.warn("Switching Game!!")
            device.click(x=1600, y=630)
            await asyncio.sleep(5)
            device.click(x=1600, y=830)
            await asyncio.sleep(5)
            device.click(x=1600, y=930)
            await asyncio.sleep(5)
            self.switch_nums += 1

            notify = Notification(
                title="尊敬的老闆, 我已經幫您打完王朝了",
                current_status="成功",
                description="王朝已完成，現在開始執行五對五全場爭霸，沒有其他事情的話我先去採棉花了。",
            )
            await notify.send_discord_notification()

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
                        await self.click_button(device=device_details.device)
                        if self.found_result.found_button_name_en == "confirm":
                            await self.switch_game(device=device_details.device)

                        await self.count_win_rate()

                        await asyncio.sleep(config_dict.delay_after_click)

            except Exception as e:
                _random_interval = secrets.randbelow(self.random_interval)
                logfire.error(
                    f"Error Occurred, Retrying in {_random_interval} seconds", _exc_info=True
                )
                notify = Notification(
                    title="尊敬的老闆, 發生錯誤!!",
                    current_status="錯誤",
                    description=f"採棉花的過程中發生錯誤，請您檢查一下 {e!s}",
                )
                await notify.send_discord_notification()
                await asyncio.sleep(_random_interval)
            _random_interval = secrets.randbelow(self.random_interval)
            await asyncio.sleep(_random_interval)
