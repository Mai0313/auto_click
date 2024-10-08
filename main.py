import time
from typing import Union
import secrets
import datetime

import yaml
import mlflow
import logfire
from adbutils import AdbDevice
from pydantic import computed_field, model_validator
import pyautogui
from src.compare import ImageComparison
from src.get_screen import GetScreen
from src.types.config import ConfigModel
from src.utils.logger import Logger
from playwright.sync_api import Page
from src.utils.get_serial import ADBDeviceManager
from src.types.output_models import Screenshot, ShiftPosition

logfire.configure(send_to_logfire=False)


class RemoteContoller(ConfigModel):
    @computed_field
    @property
    def serial(self) -> str:
        """We want to run ADBDeviceManager only once, so we use computed_field."""
        apps = ADBDeviceManager(host="127.0.0.1", target=self.target).get_correct_serial()
        return apps.serial

    @model_validator(mode="after")
    def init_mlflow(self) -> "RemoteContoller":
        mlflow.set_tracking_uri("./mlruns")
        mlflow.set_experiment(experiment_name=self.target)
        return self

    def get_screenshot(self) -> Screenshot:
        if self.target.startswith("http"):
            return GetScreen.from_remote_window(url=self.target)
        if self.target.startswith("com"):
            return GetScreen.from_adb_device(url=self.target, serial=self.serial)
        # this will return screenshot, shift_position; not device.
        return GetScreen.from_exist_window(window_title=self.target)

    def click_button(
        self,
        device: Union[Page, AdbDevice, ShiftPosition],
        calibrated_x: int,
        calibrated_y: int,
        click_this: bool,
    ) -> None:
        if self.auto_click and click_this:
            if isinstance(device, Page):
                device.mouse.click(x=calibrated_x, y=calibrated_y)
            if isinstance(device, AdbDevice):
                device.click(x=calibrated_x, y=calibrated_y)
            if isinstance(device, ShiftPosition):
                pyautogui.moveTo(x=calibrated_x, y=calibrated_y)
                pyautogui.click()

    def main(self) -> None:
        while True:
            run_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with mlflow.start_run(run_name=run_name):
                try:
                    device_details = self.get_screenshot()
                    for config_dict in self.image_list:
                        image_conpare = ImageComparison(
                            image_cfg=config_dict,
                            screenshot=device_details.screenshot,
                            device=device_details.device,
                        )
                        found = image_conpare.find()
                        if found.button_center_x and found.button_center_y:
                            calibrated_x, calibrated_y = device_details.calibrate(
                                button_center_x=found.button_center_x,
                                button_center_y=found.button_center_y,
                            )
                            self.click_button(
                                device=device_details.device,
                                calibrated_x=calibrated_x,
                                calibrated_y=calibrated_y,
                                click_this=config_dict.click_this,
                            )
                            logfire.info(
                                "Button found",
                                button_name=config_dict.image_name,
                                x=calibrated_x,
                                y=calibrated_y,
                                auto_click=self.auto_click,
                                click_this=config_dict.click_this,
                            )
                            mlflow.log_metrics(
                                metrics={
                                    "button_center_x": found.button_center_x,
                                    "button_center_y": found.button_center_y,
                                    "calibrated_x": calibrated_x,
                                    "calibrated_y": calibrated_y,
                                }
                            )
                            custom_logger = Logger(original_image_path=config_dict.image_path)
                            custom_logger.save_mlflow(
                                screenshot=found.color_screenshot, image_type="color"
                            )
                            custom_logger.save_mlflow(
                                screenshot=found.blackout_screenshot, image_type="blackout"
                            )
                            if config_dict.screenshot_option is True:
                                custom_logger.save(
                                    screenshot=found.color_screenshot, image_type="color"
                                )
                                custom_logger.save(
                                    screenshot=found.blackout_screenshot, image_type="blackout"
                                )
                            time.sleep(config_dict.delay_after_click)
                except Exception as e:
                    _random_interval = secrets.randbelow(self.random_interval)
                    logfire.error(
                        f"Error: {e}, Retrying in {_random_interval} seconds", _exc_info=True
                    )
                    time.sleep(_random_interval)
            _random_interval = secrets.randbelow(self.random_interval)
            time.sleep(_random_interval)


def load_yaml(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as file:
        configs = yaml.safe_load(file)
    return configs


if __name__ == "__main__":
    config_path = "./configs/games/all_stars.yaml"
    configs = load_yaml(config_path=config_path)
    auto_web = RemoteContoller(**configs)
    auto_web.main()

    # configs = load_hydra_config()
    # game_config = configs["games"]
    # auto_web = RemoteContoller(**game_config)
    # auto_web.main()
