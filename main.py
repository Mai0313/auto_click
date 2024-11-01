from typing import Union
import asyncio
import secrets
import datetime

import yaml
import mlflow
import logfire
from adbutils import AdbDevice
from pydantic import model_validator
import pyautogui
from src.compare import ImageComparison
from src.screenshot import GetScreen
from src.types.game import GameResult
from src.types.config import ConfigModel
from src.utils.logger import CustomLogger
from playwright.sync_api import Page
from playwright.async_api import Page as APage
from src.utils.get_serial import ADBDeviceManager
from src.types.output_models import Screenshot, ShiftPosition

logfire.configure(send_to_logfire=False)

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class RemoteController(ConfigModel, GameResult):
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

    @model_validator(mode="after")
    def _init_mlflow(self) -> "RemoteController":
        mlflow.set_tracking_uri("./mlruns")
        mlflow.set_experiment(experiment_name=self.target)
        return self

    async def get_screenshot(self) -> Screenshot:
        if self.target.startswith("http"):
            return await GetScreen.a_from_remote_window(url=self.target)
        if self.target.startswith("com"):
            return await GetScreen.from_adb_device(url=self.target, serial=self.serial)
        # 返回 screenshot 和 shift_position，而不是 device
        return await GetScreen.from_exist_window(window_title=self.target)

    async def click_button(
        self,
        device: Union[Page, APage, AdbDevice, ShiftPosition],
        calibrated_x: int,
        calibrated_y: int,
        click_this: bool,
    ) -> None:
        if self.auto_click and click_this:
            if isinstance(device, Page):
                device.mouse.click(x=calibrated_x, y=calibrated_y)
            elif isinstance(device, APage):
                await device.mouse.click(x=calibrated_x, y=calibrated_y)
            elif isinstance(device, AdbDevice):
                device.click(x=calibrated_x, y=calibrated_y)
            elif isinstance(device, ShiftPosition):
                pyautogui.moveTo(x=calibrated_x, y=calibrated_y)
                pyautogui.click()
            logfire.info(
                "Button Found",
                x=calibrated_x,
                y=calibrated_y,
                auto_click=self.auto_click,
                click_this=click_this,
            )

    async def main(self) -> None:
        with mlflow.start_run(run_name=current_time):
            while True:
                try:
                    device_details = await self.get_screenshot()
                    for config_dict in self.image_list:
                        image_compare = ImageComparison(
                            image_cfg=config_dict,
                            screenshot=device_details.screenshot,
                            device=device_details.device,
                        )
                        custom_logger = CustomLogger(original_image_path=config_dict.image_path)
                        found = await image_compare.find_and_select(
                            vertical_align="top", horizontal_align="right"
                        )
                        if found.found_button_name_en == "win":
                            self.win += 1
                        elif found.found_button_name_en == "lose":
                            self.lose += 1

                        await self.a_export(today=current_time)

                        # found = await image_compare.find()
                        if found.calibrated_x and found.calibrated_y:
                            await self.click_button(
                                device=device_details.device,
                                calibrated_x=found.calibrated_x,
                                calibrated_y=found.calibrated_y,
                                click_this=config_dict.click_this,
                            )
                            if config_dict.screenshot_option:
                                await custom_logger.a_save_images(
                                    images={
                                        "color": found.color_screenshot,
                                        "blackout": found.blackout_screenshot,
                                    },
                                    save_to="local",
                                )
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
