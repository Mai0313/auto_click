import os
import time
from typing import Union
import datetime

from pydantic import Field, BaseModel, computed_field, field_validator, model_validator
import pyautogui
from src.get_screen import GetScreen
from src.find_matched import FindMatched
from playwright.sync_api import sync_playwright


class WebAutomation(BaseModel):
    pic_samples: list
    log_dir: str
    target: str = Field(..., description="This field can be either a window title or a URL.")

    @model_validator(mode="after")
    def create_folder(self):
        os.makedirs(self.log_dir, exist_ok=True)
        return self

    @model_validator(mode="after")
    def validate_pic_samples(self):
        for pic_sample in self.pic_samples:
            if not os.path.exists(pic_sample):
                raise ValueError(f"{pic_sample} not found")
        return self

    def main(self):
        if not self.target.startswith("http"):
            while True:
                now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                log_filename = f"{self.log_dir}/{now}.png"
                screenshot, (win_x, win_y) = GetScreen.from_exist_window(self.target)
                if screenshot is not None:
                    for pic_sample in self.pic_samples:
                        find_matched = FindMatched(
                            base_image=pic_sample, log_filename=log_filename, screenshot=screenshot
                        )
                        loc, button_shape = find_matched.find()
                        if loc and button_shape:
                            button_center_x = loc[0] + button_shape[1] / 2 + win_x
                            button_center_y = loc[1] + button_shape[0] / 2 + win_y
                            pyautogui.moveTo(button_center_x, button_center_y)
                            # pyautogui.click()
                            break
                time.sleep(5)

        else:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                while True:
                    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    log_filename = f"{self.log_dir}/{now}.png"
                    screenshot, page = GetScreen.from_new_window(browser, self.target)
                    if screenshot is not None:
                        for pic_sample in self.pic_samples:
                            find_matched = FindMatched(
                                base_image=pic_sample,
                                log_filename=log_filename,
                                screenshot=screenshot,
                            )
                            loc, button_shape = find_matched.find()
                            if loc and button_shape:
                                button_center_x = loc[0] + button_shape[1] / 2
                                button_center_y = loc[1] + button_shape[0] / 2
                                page.mouse.click(button_center_x, button_center_y)
                                break
                    time.sleep(5)


if __name__ == "__main__":
    pic_samples = ["./data/samples/confirm.png"]
    log_dir = "./data/logs"
    target = "雀魂麻将"
    auto_web = WebAutomation(pic_samples=pic_samples, log_dir=log_dir, target=target)
    auto_web.main()
