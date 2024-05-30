import os
import time
from typing import Union

from PIL import Image
from pydantic import Field, BaseModel
import pyautogui
from src.utils.logger import logfire
from playwright.sync_api import Page

logfire.install_auto_tracing(modules=["src.compare", "src.get_screen", "src.models", "adbutils"])

from adbutils import AdbDevice
from src.compare import ImageComparison
from src.get_screen import GetScreen
from src.models.env_models import EnvironmentSettings
from src.models.image_models import ConfigModel
from src.models.output_models import ShiftPosition


class RemoteContoller(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    config_model: ConfigModel = Field(...)
    serial: str = Field(default_factory=lambda: None)

    def __init__(self, target: str, config_model: ConfigModel):
        super().__init__(target=target, config_model=config_model)
        settings = EnvironmentSettings()
        self.serial = f"127.0.0.1:{settings.adb_port}"
        os.system(f".\\binaries\\adb.exe connect {self.serial}")

    def get_device(
        self,
    ) -> Union[tuple[bytes, Page], tuple[bytes, AdbDevice], tuple[Image.Image, ShiftPosition]]:
        if self.target.startswith("http"):
            return GetScreen.from_remote_window(self.target)
        elif self.target.startswith("com"):
            return GetScreen.from_adb_device(self.target, self.serial)
        else:
            # this will return screenshot, shift_position; not device.
            return GetScreen.from_exist_window(self.target)

    def click_button(
        self,
        device: Union[Page, AdbDevice, ShiftPosition],
        button_center_x: int,
        button_center_y: int,
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
        # n = 0
        while True:
            screenshot, device = self.get_device()
            for config_dict in self.config_model.image_list:
                button_center_x, button_center_y = ImageComparison(
                    image_cfg=config_dict,
                    check_list=self.config_model.base_check_list,
                    screenshot=screenshot,
                ).find()
                if button_center_x and button_center_y and self.config_model.auto_click is True:
                    self.click_button(
                        device=device,
                        button_center_x=button_center_x,
                        button_center_y=button_center_y,
                    )
                    logfire.info(
                        "{image_name} Found.",
                        image_name=config_dict.image_name,
                        _tags=[config_dict.image_name],
                    )
                    time.sleep(config_dict.delay_after_click)
            time.sleep(self.config_model.global_interval)


if __name__ == "__main__":
    from omegaconf import OmegaConf

    # target = "雀魂麻将"  # "http://localhost:9222"
    # config = OmegaConf.load("./configs/mahjong.yaml")
    # config_model = ConfigModel(**config)
    # check_list = [*config_model.base_check_list, *config_model.additional_check_list]
    # config_model.base_check_list = check_list

    target = "com.longe.allstarhmt"
    config = OmegaConf.load("./configs/all_stars.yaml")
    config_model = ConfigModel(**config)

    auto_web = RemoteContoller(target=target, config_model=config_model)
    auto_web.main()
