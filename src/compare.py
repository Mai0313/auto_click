from pathlib import Path

import cv2
import numpy as np
import logfire
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page

from .utils.config import ImageModel


class FoundPosition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    button_x: int = Field(
        ..., description="The x-coordinate of the button center.", frozen=False, deprecated=False
    )
    button_y: int = Field(
        ..., description="The y-coordinate of the button center.", frozen=False, deprecated=False
    )
    name_cn: str = Field(
        ..., description="The name of the found button in Chinese.", frozen=True, deprecated=False
    )
    name_en: str = Field(
        ..., description="The name of the found button in English.", frozen=True, deprecated=False
    )


class ImageComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Image.Image | bytes = Field(..., description="The screenshot image")
    device: Page | AdbDevice = Field(..., description="The device")

    async def find(self) -> FoundPosition | None:
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
        return None
