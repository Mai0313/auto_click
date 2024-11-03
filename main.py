from typing import Union
import asyncio
import secrets
import datetime

import yaml
import logfire
from adbutils import AdbDevice
from pydantic import Field, model_validator
import pyautogui
from src.compare import ImageComparison
from src.screenshot import GetScreen
from src.types.game import GameResult
from src.types.config import ConfigModel
from playwright.sync_api import Page
from playwright.async_api import Page as APage
from src.utils.get_serial import ADBDeviceManager
from src.types.output_models import Screenshot, FoundPosition, ShiftPosition

logfire.configure(send_to_logfire=False)

current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


class RemoteController(ConfigModel, GameResult):
    found_result: FoundPosition = Field(default_factory=FoundPosition)

    @model_validator(mode="after")
    def _init_serial(self) -> "RemoteController":
        if self.serial:
            adb_manager = ADBDeviceManager(
                host="127.0.0.1", ports=[self.serial], target=self.target
            )
        else:
            adb_manager = ADBDeviceManager(host="127.0.0.1", target=self.target)
        apps = adb_manager.get_correct_serial()
        self.serial = apps.serial
        return self

    async def get_screenshot(self) -> Screenshot:
        if self.target.startswith("http"):
            return await GetScreen.a_from_remote_window(url=self.target)
        if self.target.startswith("com"):
            return await GetScreen.from_adb_device(url=self.target, serial=self.serial)
        # 返回 screenshot 和 shift_position，而不是 device
        return await GetScreen.from_exist_window(window_title=self.target)

    async def click_button(self, device: Union[Page, APage, AdbDevice, ShiftPosition]) -> None:
        if self.found_result.calibrated_x and self.found_result.calibrated_y:
            if isinstance(device, Page):
                device.mouse.click(
                    x=self.found_result.calibrated_x, y=self.found_result.calibrated_y
                )
            elif isinstance(device, APage):
                await device.mouse.click(
                    x=self.found_result.calibrated_x, y=self.found_result.calibrated_y
                )
            elif isinstance(device, AdbDevice):
                device.click(x=self.found_result.calibrated_x, y=self.found_result.calibrated_y)
            elif isinstance(device, ShiftPosition):
                pyautogui.moveTo(
                    x=self.found_result.calibrated_x, y=self.found_result.calibrated_y
                )
                pyautogui.click()

    async def count_win_rate(self) -> None:
        if self.found_result.found_button_name_en == "win":
            self.win += 1
            await self.a_export(today=current_time)
        elif self.found_result.found_button_name_en == "lose":
            self.lose += 1
            await self.a_export(today=current_time)

    async def main(self) -> None:
        while True:
            try:
                device_details = await self.get_screenshot()
                for config_dict in self.image_list:
                    image_compare = ImageComparison(
                        image_cfg=config_dict,
                        screenshot=device_details.screenshot,
                        device=device_details.device,
                    )

                    self.found_result = await image_compare.find()

                    if self.auto_click and config_dict.click_this:
                        await self.click_button(device=device_details.device)

                        await self.count_win_rate()

                        await asyncio.sleep(config_dict.delay_after_click)
            except Exception as e:
                _random_interval = secrets.randbelow(self.random_interval)
                logfire.error(
                    f"Error: {e}, Retrying in {_random_interval} seconds", _exc_info=True
                )
                await asyncio.sleep(_random_interval)
            _random_interval = secrets.randbelow(self.random_interval)
            await asyncio.sleep(_random_interval)


def load_yaml(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as file:
        configs = yaml.safe_load(file)
    return configs


if __name__ == "__main__":
    config_path = "./configs/games/all_stars.yaml"
    configs = load_yaml(config_path=config_path)
    auto_web = RemoteController(**configs)
    asyncio.run(auto_web.main())
