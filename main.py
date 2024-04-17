import os
import time
from typing import Union
from calendar import c
import datetime

import yaml
from pydantic import Field, BaseModel, computed_field, field_validator, model_validator
import pyautogui
from src.get_screen import GetScreen
from src.find_matched import FindMatched
from playwright.sync_api import sync_playwright
from src.models.image_models import Settings


class WebAutomation(BaseModel):
    log_dir: str
    target: str = Field(..., description="This field can be either a window title or a URL.")

    @model_validator(mode="after")
    def create_folder(self):
        os.makedirs(self.log_dir, exist_ok=True)
        return self

    @computed_field
    @property
    def image_configs(self) -> list[dict]:
        with open("./configs/settings.yaml", encoding="utf-8") as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
            return settings

    def main(self, strategy: list[str]):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{self.log_dir}/{now}.png"
        while True:
            if not self.target.startswith("http"):
                screenshot, win_x, win_y = GetScreen.from_exist_window(self.target)
            else:
                screenshot, page, browser = GetScreen.from_new_window(self.target)
            if screenshot is not None:
                for image_config in self.image_configs:
                    image_cfg = Settings(**image_config)
                    image_name = image_cfg.image_name
                    if image_name not in strategy:
                        continue
                    image_path = image_cfg.image_path
                    image_click_delay = image_cfg.image_click_delay
                    screenshot_option = image_cfg.screenshot_option
                    find_matched = FindMatched(
                        base_image=image_cfg.image_path,
                        log_filename=log_filename,
                        screenshot=screenshot,
                        screenshot_option=screenshot_option,
                    )
                    loc, button_shape = find_matched.find()
                    if loc and button_shape:
                        if not self.target.startswith("http"):
                            button_center_x = loc[0] + button_shape[1] / 2 + win_x
                            button_center_y = loc[1] + button_shape[0] / 2 + win_y
                            pyautogui.moveTo(button_center_x, button_center_y)
                            pyautogui.click()
                        elif self.target.startswith("http"):
                            button_center_x = loc[0] + button_shape[1] / 2
                            button_center_y = loc[1] + button_shape[0] / 2
                            page.mouse.click(button_center_x, button_center_y)
                        time.sleep(image_click_delay)
            time.sleep(5)


if __name__ == "__main__":
    log_dir = "./data/logs"
    target = "雀魂麻将"
    strategy = [
        "遊戲結束確認",
        "開始段位",
        "金之間",
        "四人南",
        "胡了",
        "對局結束",
        "獲得獎勵",
        "簽到v1",
        "簽到v2",
        "關閉",
        "叉叉",
        "進入遊戲",
        "好的",
    ]
    auto_web = WebAutomation(log_dir=log_dir, target=target)
    auto_web.main(strategy=strategy)
