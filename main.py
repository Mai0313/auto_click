import time

import yaml
from pydantic import Field, BaseModel, computed_field
import pyautogui
from src.compare import ImageComparison
from src.get_screen import GetScreen
from src.models.image_models import Settings, ConfigModel


class RemoteContoller(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    config_model: ConfigModel = Field(...)

    def main(self) -> None:
        while True:
            if "http" in self.target:
                screenshot, device = GetScreen.from_remote_window(self.target)
            elif "com." in self.target:
                screenshot, device = GetScreen.from_adb_device(self.target, 16416)
            else:
                screenshot, shift_position = GetScreen.from_exist_window(self.target)
            if screenshot:
                for image_config_dict in self.config_model.image_list:
                    find_matched = ImageComparison(
                        image_cfg=image_config_dict,
                        check_list=self.config_model.base_check_list,
                        screenshot=screenshot,
                    )
                    button_center_x, button_center_y = find_matched.find()
                    if button_center_x and button_center_y:
                        if self.config_model.auto_click is True:
                            if "http" in self.target:
                                device.mouse.click(button_center_x / 2, button_center_y / 2)
                            elif "com." in self.target:
                                device.click(button_center_x / 2, button_center_y / 2)
                            else:
                                button_center_x = button_center_x / 2 + shift_position.shift_x
                                button_center_y = button_center_y / 2 + shift_position.shift_y
                                pyautogui.moveTo(x=button_center_x, y=button_center_y)
                                pyautogui.click()
                        time.sleep(image_config_dict.image_click_delay)


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
