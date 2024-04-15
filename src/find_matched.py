# from PIL.Image import Image  # for type hinting
from io import BytesIO
from typing import Union

import cv2
import numpy as np
from pydantic import Field, BaseModel, ConfigDict, computed_field, model_validator
import PIL.Image as Image


class FindMatched(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_image: str = Field(..., description="The path to the image to be matched")
    log_filename: str = Field(..., description="The path to save the matched image")
    screenshot: Union[Image.Image, bytes]
    screenshot_option: bool = Field(
        ...,
        description="The option to take a screenshot; true for save screenshot, false for not save screenshot",
    )

    @model_validator(mode="after")
    def get_screenshot_image(self):
        if isinstance(self.screenshot, bytes):
            image_stream = BytesIO(self.screenshot)
            return Image.open(image_stream)
        return self.screenshot

    @computed_field
    @property
    def color_screenshot(self) -> np.ndarray:
        if isinstance(self.screenshot, bytes):
            image_stream = BytesIO(self.screenshot)
            pil_image = Image.open(image_stream)
            color_screenshot = np.array(pil_image)
        else:
            color_screenshot = np.array(self.screenshot)
        return color_screenshot

    @computed_field
    @property
    def gray_screenshot(self) -> np.ndarray:
        if isinstance(self.screenshot, bytes):
            image_stream = BytesIO(self.screenshot)
            pil_image = Image.open(image_stream)
            gray_screenshot = np.array(pil_image.convert("L"))
        else:
            gray_screenshot = cv2.cvtColor(np.array(self.screenshot), cv2.COLOR_RGB2GRAY)
        return gray_screenshot

    def find(self):
        button_image = cv2.imread(self.base_image, 0)
        if button_image is None:
            raise Exception(f"Unable to load button image from path: {self.base_image}")

        result = cv2.matchTemplate(self.gray_screenshot, button_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        threshold = 0.9
        if max_val > threshold:
            button_w = button_image.shape[1]
            button_h = button_image.shape[0]
            top_left = max_loc
            bottom_right = (top_left[0] + button_w, top_left[1] + button_h)
            if self.screenshot_option is True:
                color_screenshot = self.color_screenshot.copy()
                cv2.rectangle(color_screenshot, top_left, bottom_right, (0, 0, 255), 2)
                cv2.imwrite(self.log_filename, color_screenshot)
            return max_loc, button_image.shape
        return None, None
