import time
from typing import Union
import secrets

import yaml
import logfire
from adbutils import AdbDevice
from pydantic import computed_field
import pyautogui
from src.compare import ImageComparison
from src.get_screen import GetScreen
from src.types.config import ConfigModel
from playwright.sync_api import Page
from src.utils.get_serial import ADBDeviceManager
from src.types.output_models import Screenshot, ShiftPosition

logfire.configure(
    send_to_logfire=True,
    token="t5yWZMmjyRH5ZVqvJRwwHHfm5L3SgbRjtkk7chW3rjSp",  # noqa: S106
    project_name="auto-click",
    show_summary=True,
    data_dir=".logfire",
    inspect_arguments=None,
)


class RemoteContoller(ConfigModel):
    @computed_field
    @property
    def serial(self) -> str:
        """We want to run ADBDeviceManager only once, so we use computed_field."""
        apps = ADBDeviceManager(host="127.0.0.1", target=self.target).get_correct_serial()
        return apps.serial

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
        else:
            logfire.info(
                "Button found but click feature is disabled",
                x=calibrated_x,
                y=calibrated_y,
                auto_click=self.auto_click,
                click_this=click_this,
            )

    def main(self) -> None:
        while True:
            try:
                device_details = self.get_screenshot()
                for config_dict in self.image_list:
                    button_center_x, button_center_y = ImageComparison(
                        image_cfg=config_dict,
                        screenshot=device_details.screenshot,
                        device=device_details.device,
                    ).find()
                    if button_center_x and button_center_y:
                        calibrated_x, calibrated_y = device_details.calibrate(
                            button_center_x=button_center_x, button_center_y=button_center_y
                        )
                        self.click_button(
                            device=device_details.device,
                            calibrated_x=calibrated_x,
                            calibrated_y=calibrated_y,
                            click_this=config_dict.click_this,
                        )
                        time.sleep(config_dict.delay_after_click)
            except Exception as e:
                logfire.error("Error in getting device:", error=e, _exc_info=True)
                _random_interval = secrets.randbelow(self.random_interval)
                logfire.info("Retrying...", retry_interval=_random_interval)
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
