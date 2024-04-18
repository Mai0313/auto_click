import os
import time
from typing import Union
import datetime

import yaml
from pydantic import Field, BaseModel, computed_field, field_validator, model_validator
import pyautogui
from src.get_screen import GetScreen
from src.find_matched import FindMatched
from playwright.sync_api import sync_playwright
from src.models.image_models import Settings


class WebAutomation(BaseModel):
    target: str = Field(..., description="This field can be either a window title or a URL.")
    check_list: list[str] = Field(
        ..., description="The check list, it should be a list of image names"
    )

    @computed_field
    @property
    def image_configs(self) -> list[dict]:
        with open("./configs/settings.yaml", encoding="utf-8") as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
        return settings

    def main(self):
        while True:
            if not self.target.startswith("http"):
                screenshot, win_x, win_y = GetScreen.from_exist_window(self.target)
            else:
                screenshot, page, browser = GetScreen.from_new_window(self.target)
            if screenshot is not None:
                for image_config in self.image_configs:
                    image_cfg = Settings(**image_config)

                    find_matched = FindMatched(
                        image_cfg=image_cfg,
                        check_list=self.check_list,
                        screenshot=screenshot,
                    )
                    loc, button_shape = find_matched.find()
                    if loc and button_shape:
                        if not self.target.startswith("http"):
                            button_center_x = loc[0] + button_shape[1] / 2 + win_x
                            button_center_y = loc[1] + button_shape[0] / 2 + win_y
                            pyautogui.moveTo(button_center_x, button_center_y)
                            # pyautogui.click()
                        elif self.target.startswith("http"):
                            button_center_x = loc[0] + button_shape[1] / 2
                            button_center_y = loc[1] + button_shape[0] / 2
                            # page.mouse.click(button_center_x, button_center_y)
                        time.sleep(image_cfg.image_click_delay)
                break
            # time.sleep(5)


if __name__ == "__main__":
    target = "雀魂麻将"
    base_check_list = [
        "遊戲結束確認",
        "開始段位",
        "胡了",
        "對局結束",
        "結算畫面",
        "獲得獎勵",
        "簽到",
        "關閉",
        "叉叉",
        "進入遊戲",
        "好的",
    ]
    additional_check_list = ["金之間", "四人南"]

    check_list = [*base_check_list, *additional_check_list]
    auto_web = WebAutomation(target=target, check_list=check_list)
    auto_web.main()
