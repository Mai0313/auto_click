import os
import time
from typing import Union, Optional
import datetime

import yaml
from pydantic import Field, BaseModel, computed_field, field_validator, model_validator
import pyautogui
from src.get_screen import GetScreen
from src.find_matched import FindMatched
from playwright.sync_api import sync_playwright
from src.models.image_models import Settings


class WebAutomation(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    check_list: list[str] = Field(
        ..., description="The check list, it should be a list of image names"
    )
    auto_click: bool = Field(..., description="Whether to click the button automatically")

    @computed_field
    @property
    def image_configs(self) -> list[dict]:
        with open("./configs/settings.yaml", encoding="utf-8") as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
        return settings

    def main(self):
        while True:
            additional_delay = True
            if "localhost" not in self.target:
                screenshot, win_x, win_y = GetScreen.from_exist_window(self.target)
            else:
                screenshot, page, browser = GetScreen.from_remote_window(self.target)
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
                        # This condition should be placed here since we need to know if it detects the image.
                        # Even if you don't want to click the button, you still need to wait.
                        if self.auto_click is True:
                            if "localhost" in self.target:
                                button_center_x = loc[0] + button_shape[1] / 2
                                button_center_y = loc[1] + button_shape[0] / 2
                                page.mouse.click(button_center_x, button_center_y)
                            else:
                                button_center_x = loc[0] + button_shape[1] / 2 + win_x
                                button_center_y = loc[1] + button_shape[0] / 2 + win_y
                                # pyautogui.scroll(image_cfg.scroll, x=button_center_x, y=button_center_y)
                                pyautogui.moveTo(x=button_center_x, y=button_center_y)
                                pyautogui.click()
                        time.sleep(image_cfg.image_click_delay)
                        additional_delay = False
            if additional_delay is True:
                time.sleep(5)


if __name__ == "__main__":
    target = "雀魂麻将"
    # target = "http://localhost:9222"
    base_check_list = [
        "遊戲結束確認",
        "遊戲結束確認2",
        "開始段位",
        "胡了",
        "對局結束",
        "結算畫面",
        # "獲得獎勵",
        "簽到",
        "關閉",
        "叉叉",
        "進入遊戲",
        "好的",
        # "一般場",
    ]
    additional_check_list = ["銀之間", "三人東"]
    auto_click = True

    check_list = [*base_check_list, *additional_check_list]
    auto_web = WebAutomation(target=target, check_list=check_list, auto_click=auto_click)
    auto_web.main()
