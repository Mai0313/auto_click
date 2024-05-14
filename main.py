import time

import yaml
from pydantic import Field, BaseModel, computed_field
import pyautogui
from src.get_screen import GetScreen
from src.find_matched import FindMatched
from src.models.image_models import Settings, ConfigModel


class RemoteContoller(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    config_model: ConfigModel = Field(...)

    def main(self) -> None:
        while True:
            additional_delay = True
            if "localhost" in self.target:
                screenshot, page = GetScreen.from_remote_window(self.target)
            elif "com." in self.target:
                screenshot, device = GetScreen.from_adb_device(self.target, 16416)
            else:
                screenshot, shift_position = GetScreen.from_exist_window(self.target)
            if screenshot is not None:
                for image_config_dict in self.config_model.image_list:
                    find_matched = FindMatched(
                        image_cfg=image_config_dict,
                        check_list=self.config_model.base_check_list,
                        screenshot=screenshot,
                    )
                    loc, button_shape = find_matched.find()
                    if loc and button_shape:
                        if self.config_model.auto_click is True:
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
                        time.sleep(image_config_dict.image_click_delay)
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
    config = OmegaConf.load("./configs/all_stars.yaml")
    config_model = ConfigModel(**config)

    auto_web = RemoteContoller(target=target, config_model=config_model)
    auto_web.main()
