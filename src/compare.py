import os
import time
import datetime

import cv2
import numpy as np
import logfire
from pydantic import Field, BaseModel, ConfigDict, computed_field
import PIL.Image as Image

from src.types.image_models import ImageModel


class ImageComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Image.Image | bytes = Field(..., description="The screenshot image")

    # @model_validator(mode="after")
    # def get_screenshot_image(self) -> Image.Image | bytes:
    #     if isinstance(self.screenshot, bytes):
    #         image_stream = BytesIO(self.screenshot)
    #         return Image.open(image_stream)
    #     return self.screenshot

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
        time.sleep(1)
        return log_filename

    @computed_field
    @property
    def button_image(self) -> cv2.typing.MatLike:
        button_image = cv2.imread(self.image_cfg.image_path, 0)
        if button_image is None:
            logfire.warn("Unable to load button image", **self.image_cfg.model_dump())
        return button_image

    def draw_rectangle(
        self, matched_image_position: tuple[int, int], max_loc: cv2.typing.Point
    ) -> None:
        color_screenshot, _ = self.screenshot_array
        cv2.rectangle(color_screenshot, max_loc, matched_image_position, (0, 0, 255), 2)
        cv2.imwrite(self.log_filename, color_screenshot)
        logfire.info(
            "The screenshot has been saved",
            log_filename=self.log_filename,
            **self.image_cfg.model_dump(),
        )

    def find(self) -> tuple[int | None, int | None]:
        _, gray_screenshot = self.screenshot_array

        result = cv2.matchTemplate(gray_screenshot, self.button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        button_center_x = int(max_loc[0] + self.button_image.shape[1])
        button_center_y = int(max_loc[1] + self.button_image.shape[0])
        matched_image_position = (button_center_x, button_center_y)

        if max_val > self.image_cfg.confidence:
            logfire.info(
                "Found the target image",
                confidence_decision=max_val,
                button_center_x=button_center_x,
                button_center_y=button_center_y,
                **self.image_cfg.model_dump(),
            )
            if self.image_cfg.screenshot_option is True:
                self.draw_rectangle(matched_image_position, max_loc)
            return button_center_x, button_center_y
        return None, None
