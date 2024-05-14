import time

import yaml
from pydantic import Field, BaseModel, computed_field
import pyautogui
from src.get_screen import GetScreen
from src.find_matched import FindMatched
from src.models.image_models import Settings


class RemoteContoller(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    image_config_path: str
    check_list: list[str] = Field(
        ..., description="The check list, it should be a list of image names"
    )
    auto_click: bool = Field(..., description="Whether to click the button automatically")

    @computed_field
    @property
    def image_configs(self) -> list[dict]:
        with open(self.image_config_path, encoding="utf-8") as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
        return settings

    def main(self) -> None:
        while True:
            additional_delay = True
            if "localhost" in self.target:
                screenshot, page = GetScreen.from_remote_window(self.target)
            elif "com." in self.target:
                screenshot, device = GetScreen.from_adb_device(self.target)
            else:
                screenshot, shift_position = GetScreen.from_exist_window(self.target)
            if screenshot is not None:
                for image_config in self.image_configs:
                    image_cfg = Settings(**image_config)

                    find_matched = FindMatched(
                        image_cfg=image_cfg, check_list=self.check_list, screenshot=screenshot
                    )
                    loc, button_shape = find_matched.find()
                    if loc and button_shape:
                        if self.auto_click is True:
                            if "localhost" in self.target:
                                button_center_x = loc[0] + button_shape[1] / 2
                                button_center_y = loc[1] + button_shape[0] / 2
                                page.mouse.click(button_center_x, button_center_y)
                            elif "com." in self.target:
                                button_center_x = loc[0] + button_shape[1] / 2
                                button_center_y = loc[1] + button_shape[0] / 2
                                device.click(button_center_x, button_center_y)
                            else:
                                button_center_x = (
                                    loc[0] + button_shape[1] / 2 + shift_position.shift_x
                                )
                                button_center_y = (
                                    loc[1] + button_shape[0] / 2 + shift_position.shift_y
                                )
                                pyautogui.moveTo(x=button_center_x, y=button_center_y)
                                pyautogui.click()
                        time.sleep(image_cfg.image_click_delay)
                        additional_delay = False
            if additional_delay is True:
                time.sleep(5)


if __name__ == "__main__":
    from omegaconf import OmegaConf

    # target = "雀魂麻将"  # "http://localhost:9222"
    # config = OmegaConf.load("./configs/settings/mahjong.yaml")
    # base_check_list = config.base_check_list
    # image_config_path = "./configs/path/mahjong.yaml"
    # additional_check_list = config.additional_check_list
    # auto_click = True
    # check_list = [*base_check_list, *additional_check_list]

    target = "com.longe.allstarhmt"
    config = OmegaConf.load("./configs/settings/all_stars.yaml")
    base_check_list = config.base_check_list
    image_config_path = "./configs/path/all_stars.yaml"
    auto_click = True
    check_list = base_check_list

    auto_web = RemoteContoller(
        target=target,
        image_config_path=image_config_path,
        check_list=check_list,
        auto_click=auto_click,
    )
    auto_web.main()
