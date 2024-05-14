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


class ImageComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: Settings = Field(..., description="The image configuration")
    check_list: list[str] = Field(
        ..., description="The check list, it should be a list of image names"
    )
    screenshot: Union[Image.Image, bytes] = Field(..., description="The screenshot image")

    @model_validator(mode="after")
    def get_screenshot_image(self) -> Union[Image.Image, bytes]:
        if isinstance(self.screenshot, bytes):
            image_stream = BytesIO(self.screenshot)
            return Image.open(image_stream)
        return self.screenshot

    @computed_field
    @property
    def screenshot_array(self) -> tuple[np.ndarray, np.ndarray]:
        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2GRAY)
        return color_screenshot, gray_screenshot

    @computed_field
    @property
    def log_filename(self) -> str:
        log_dir = "./data/logs"
        os.makedirs(log_dir, exist_ok=True)
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{log_dir}/{now}.png"
        return log_filename

    @computed_field
    @property
    def button_image(self) -> cv2.typing.MatLike:
        button_image = cv2.imread(self.image_cfg.image_path, 0)
        if button_image is None:
            raise Exception(f"Unable to load button image from path: {self.image_cfg.image_path}")
        return button_image

    def draw_rectangle(
        self, matched_image_position: tuple[int, int], max_loc: cv2.typing.Point
    ) -> None:
        if self.image_cfg.screenshot_option is True:
            color_screenshot, _ = self.screenshot_array
            cv2.rectangle(color_screenshot, max_loc, matched_image_position, (0, 0, 255), 2)
            cv2.imwrite(self.log_filename, color_screenshot)

    def find(self) -> tuple[Union[int, None], Union[int, None]]:
        if self.image_cfg.image_name not in self.check_list:
            return None, None

        _, gray_screenshot = self.screenshot_array

        result = cv2.matchTemplate(gray_screenshot, self.button_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        button_center_x = int(max_loc[0] + self.button_image.shape[1])
        button_center_y = int(max_loc[1] + self.button_image.shape[0])
        matched_image_position = (button_center_x, button_center_y)
        self.draw_rectangle(matched_image_position, max_loc)

        if max_val > self.image_cfg.confidence:
            console.print(f"{self.image_cfg.image_name} Found at {self.button_image.shape}")
            return button_center_x, button_center_y
        return None, None
