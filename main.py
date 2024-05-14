import time

from PIL import Image
from git import Union
from adbutils import AdbDevice
from pydantic import Field, BaseModel
import pyautogui
from src.compare import ImageComparison
from src.get_screen import GetScreen
from playwright.sync_api import Page
from src.models.image_models import ConfigModel
from src.models.output_models import ShiftPosition


class RemoteContoller(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    config_model: ConfigModel = Field(...)

    def get_device(
        self,
    ) -> Union[tuple[bytes, Page], tuple[bytes, AdbDevice], tuple[Image.Image, ShiftPosition]]:
        if self.target.startswith("http"):
            return GetScreen.from_remote_window(self.target)
        elif self.target.startswith("com"):
            return GetScreen.from_adb_device(self.target, 16416)
        else:
            # this will return screenshot, shift_position; not device.
            return GetScreen.from_exist_window(self.target)

    def click_button(
        self,
        device: Union[Page, AdbDevice, ShiftPosition],
        button_center_x: int,
        button_center_y: int,
    ) -> None:
        x, y = button_center_x / 2, button_center_y / 2
        if isinstance(device, Page):
            device.mouse.click(x=x, y=y)
        elif isinstance(device, AdbDevice):
            device.click(x=x, y=y)
        else:
            pyautogui.moveTo(x=x + device.shift_x, y=y + device.shift_y)
            pyautogui.click()

    def main(self) -> None:
        for _ in range(self.config_model.loops):
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
                    time.sleep(config_dict.image_click_delay)
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
