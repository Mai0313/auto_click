from io import BytesIO
import os
from typing import Union
import datetime

import cv2
import numpy as np
from pydantic import Field, BaseModel, ConfigDict, computed_field, model_validator
import PIL.Image as Image
from rich.console import Console
from src.models.image_models import Settings

console = Console()


class FindMatched(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: Settings = Field(..., description="The image configuration")
    check_list: list[str] = Field(
        ..., description="The check list, it should be a list of image names"
    )
    screenshot: Union[Image.Image, bytes] = Field(..., description="The screenshot image")

    @model_validator(mode="after")
    def get_screenshot_image(self):
        if isinstance(self.screenshot, bytes):
            image_stream = BytesIO(self.screenshot)
            return Image.open(image_stream)
        return self.screenshot

    @computed_field
    @property
    def screenshot_array(self) -> tuple[np.ndarray, np.ndarray]:
        if isinstance(self.screenshot, bytes):
            image_stream = BytesIO(self.screenshot)
            pil_image = Image.open(image_stream)
            color_screenshot = np.array(pil_image)
            gray_screenshot = np.array(pil_image.convert("L"))
        else:
            color_screenshot = np.array(self.screenshot)
            gray_screenshot = cv2.cvtColor(np.array(self.screenshot), cv2.COLOR_RGB2GRAY)
        return color_screenshot, gray_screenshot

    @computed_field
    @property
    def log_filename(self) -> str:
        log_dir = "./data/logs"
        os.makedirs(log_dir, exist_ok=True)
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{log_dir}/{now}.png"
        return log_filename

    def find(self):
        if not os.path.exists(self.image_cfg.image_path):
            raise Exception(f"Unable to find button image from path: {self.image_cfg.image_path}")
        if self.image_cfg.image_name not in self.check_list:
            return None, None

        button_image = cv2.imread(self.image_cfg.image_path, 0)
        if button_image is None:
            raise Exception(f"Unable to load button image from path: {self.image_cfg.image_path}")

        color_screenshot, gray_screenshot = self.screenshot_array

        result = cv2.matchTemplate(gray_screenshot, button_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.1:  # self.image_cfg.confidence:
            button_w = button_image.shape[1]
            button_h = button_image.shape[0]
            top_left = max_loc
            bottom_right = (top_left[0] + button_w, top_left[1] + button_h)
            if self.image_cfg.screenshot_option is True:
                cv2.rectangle(color_screenshot, top_left, bottom_right, (0, 0, 255), 2)
                cv2.imwrite(self.log_filename, color_screenshot)
            console.print(
                f"{self.image_cfg.image_name} Found at {button_image.shape} and screenshot option is {self.image_cfg.screenshot_option}"
            )
            return max_loc, button_image.shape
        return None, None
