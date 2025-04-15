from pathlib import Path

import cv2
import numpy as np
import logfire
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page

from .types.config import ImageModel
from .types.output import FoundPosition


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

    async def find(self) -> FoundPosition:
        """Finds the position of a button image within a screenshot.

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

            click_x = int(max_loc[0] + width // 2)
            click_y = int(max_loc[1] + height // 2)

            return FoundPosition(
                button_x=click_x,
                button_y=click_y,
                name_en=Path(self.image_cfg.image_path).stem,
                name_cn=self.image_cfg.image_name,
            )
        return FoundPosition()
