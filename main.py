import time
import getpass
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
    send_to_logfire=False,
    token=None,
    project_name="auto-click",
    service_name=f"{getpass.getuser()}",
    trace_sample_rate=1.0,
    show_summary=True,
    data_dir=".logfire",
    fast_shutdown=True,
    console={
        "colors": "auto",
        "span_style": "show-parents",
        "verbose": True,
        "min_log_level": "info",
    },
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
        self, device: Page | AdbDevice | ShiftPosition, button_center_x: int, button_center_y: int
    ) -> None:
        if isinstance(device, Page):
            device.mouse.click(x=button_center_x, y=button_center_y)
        elif isinstance(device, AdbDevice):
            device.click(x=button_center_x, y=button_center_y)
        else:
            pyautogui.moveTo(
                x=button_center_x + device.shift_x, y=button_center_y + device.shift_y
            )
            pyautogui.click()

    def main(self) -> None:
        while True:
            try:
                device_details = self.get_screenshot()
                for config_dict in self.image_list:
                    button_center_x, button_center_y = ImageComparison(
                        image_cfg=config_dict, screenshot=device_details.screenshot
                    ).find()
                    if (
                        button_center_x
                        and button_center_y
                        and self.auto_click is True
                        and config_dict.click_this is True
                    ):
                        self.click_button(
                            device=device_details.device,
                            button_center_x=button_center_x,
                            button_center_y=button_center_y,
                        )
                        time.sleep(config_dict.delay_after_click)
            except Exception as e:
                logfire.error("Error in getting device:", error=e)
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
