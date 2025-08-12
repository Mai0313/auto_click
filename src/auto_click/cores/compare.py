from typing import TYPE_CHECKING
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import logfire
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image

from .config import ImageModel

if TYPE_CHECKING:
    from cv2.typing import MatLike


class FoundPosition(BaseModel):
    """Represents the position of a found button on the screen.

    Attributes:
        button_x (Optional[int]): The x-coordinate of the button center.
        button_y (Optional[int]): The y-coordinate of the button center.
        found_button_name_en (Optional[str]): The name of the found button in English.
        found_button_name_cn (Optional[str]): The name of the found button in Chinese.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    button_x: int | None = Field(
        default=None,
        description="The x-coordinate of the button center.",
        frozen=False,
        deprecated=False,
    )
    button_y: int | None = Field(
        default=None,
        description="The y-coordinate of the button center.",
        frozen=False,
        deprecated=False,
    )
    found_button_name_en: str | None = Field(
        default=None,
        description="The name of the found button in English.",
        frozen=True,
        deprecated=False,
    )
    found_button_name_cn: str | None = Field(
        default=None,
        description="The name of the found button in Chinese.",
        frozen=True,
        deprecated=False,
    )

    async def calibrate(self, shift_x: int, shift_y: int) -> None:
        """Adjusts the button center coordinates based on the device type.

        Args:
            shift_x (int): The amount to shift the button center along the x-axis.
            shift_y (int): The amount to shift the button center along the y-axis.
        """
        if self.button_x and self.button_y:
            self.button_x += shift_x
            self.button_y += shift_y


class ImageComparison(BaseModel):
    """Represents an image comparison object.

    This class provides methods to compare an image with a screenshot and find the position of a button image within the screenshot.

    Attributes:
        image_cfg (ImageModel): The image configuration.
        screenshot (Union[Image.Image, bytes]): The screenshot image.

    Methods:
        __save_images: Saves the images to the logs directory.
        __draw_rectangle: Draws a rectangle on the image and saves the resulting image.
        find: Finds the position of a button image within a screenshot.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Image.Image | bytes = Field(..., description="The screenshot image")

    async def record_position(self) -> None:
        position_data = pd.DataFrame()
        position_log_path = Path("./logs/positions.csv")
        if position_log_path.exists():
            position_data = pd.read_csv(position_log_path)

        data_dict_list = [self.image_cfg.model_dump()]
        new_position_data = pd.DataFrame(data_dict_list).astype(str)
        merged_data = pd.concat([position_data, new_position_data], ignore_index=True)
        merged_data = merged_data.drop_duplicates(subset=["image_name", "image_path"], keep="last")
        merged_data = merged_data.reset_index(drop=True)
        merged_data.to_csv(position_log_path.as_posix(), index=False)

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
        gray_screenshot: MatLike = cv2.cvtColor(color_screenshot, cv2.COLOR_BGR2GRAY)
        button_image: MatLike = cv2.cvtColor(color_button_image, cv2.COLOR_BGR2GRAY)

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

            # Calculate click_x
            click_x = int(max_loc[0] + width // 2)

            # Calculate click_y
            click_y = int(max_loc[1] + height // 2)

            return FoundPosition(
                button_x=click_x,
                button_y=click_y,
                found_button_name_en=Path(self.image_cfg.image_path).stem,
                found_button_name_cn=self.image_cfg.image_name,
            )
        return FoundPosition()
