from typing import Literal
from pathlib import Path

import cv2
import numpy as np
import logfire
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page

from .types.config import ImageModel
from .types.output_models import FoundPosition


class ImageComparison(BaseModel):
    """Represents an image comparison object.

    This class provides methods to compare an image with a screenshot and find the position of a button image within the screenshot.

    Attributes:
        image_cfg (ImageModel): The image configuration.
        screenshot (Union[Image.Image, bytes]): The screenshot image.
        device (Union[Page, AdbDevice]): The device.

    Methods:
        __save_images: Saves the images to the logs directory.
        __draw_rectangle: Draws a rectangle on the image and saves the resulting image.
        find: Finds the position of a button image within a screenshot.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Image.Image | bytes = Field(..., description="The screenshot image")
    device: Page | AdbDevice = Field(..., description="The device")

    async def find(
        self,
        vertical_align: Literal["top", "center", "bottom"],
        horizontal_align: Literal["left", "center", "right"],
    ) -> FoundPosition:
        """Finds the position of a button image within a screenshot.

        Args:
            vertical_align (Literal["top", "center", "bottom"]): The vertical alignment within the matched template. Defaults to "center".
            horizontal_align (Literal["left", "center", "right"]): The horizontal alignment within the matched template. Defaults to "center".

        Raises:
            ValueError: If an invalid alignment value is provided.

        Returns:
            FoundPosition: The found position of the button image.
        """
        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        color_button_image = cv2.imread(self.image_cfg.image_path)

        # Convert both images to grayscale
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_BGR2GRAY)
        button_image = cv2.cvtColor(color_button_image, cv2.COLOR_BGR2GRAY)

        # Match the button image with the screenshot
        gray_matched = cv2.matchTemplate(
            image=gray_screenshot,
            templ=button_image,
            method=cv2.TM_CCOEFF_NORMED,
            result=None,
            mask=None,
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(gray_matched)

        if max_val > self.image_cfg.confidence:
            logfire.info(
                "Found Position from Current Screen",
                max_val=max_val,
                **self.image_cfg.model_dump(exclude_none=True),
            )
            width = button_image.shape[1]
            height = button_image.shape[0]

            # Calculate click_x based on horizontal alignment
            if horizontal_align == "left":
                click_x = int(max_loc[0])
            elif horizontal_align == "center":
                click_x = int(max_loc[0] + width // 2)
            elif horizontal_align == "right":
                click_x = int(max_loc[0] + width)
            else:
                raise ValueError(f"Invalid horizontal_align value: {horizontal_align}")

            # Calculate click_y based on vertical alignment
            if vertical_align == "top":
                click_y = int(max_loc[1])
            elif vertical_align == "center":
                click_y = int(max_loc[1] + height // 2)
            elif vertical_align == "bottom":
                click_y = int(max_loc[1] + height)
            else:
                raise ValueError(f"Invalid vertical_align value: {vertical_align}")

            return FoundPosition(
                button_x=click_x,
                button_y=click_y,
                found_button_name_en=Path(self.image_cfg.image_path).stem,
                found_button_name_cn=self.image_cfg.image_name,
            )
        return FoundPosition()
