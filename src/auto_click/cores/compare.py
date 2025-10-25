from typing import TYPE_CHECKING
import asyncio
from pathlib import Path
from functools import lru_cache

import cv2
import numpy as np
import pandas as pd
import logfire
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image

from .config import ImageModel

if TYPE_CHECKING:
    from cv2.typing import MatLike


@lru_cache(maxsize=32)
def _load_and_convert_template(image_path: str) -> "MatLike":
    """Load and convert template image to grayscale with caching.

    Args:
        image_path (str): Path to the template image.

    Returns:
        MatLike: Grayscale template image.

    Notes:
        Results are cached using LRU cache to avoid repeated disk I/O.
    """
    color_button_image = cv2.imread(image_path)
    return cv2.cvtColor(color_button_image, cv2.COLOR_BGR2GRAY)


def _sync_match_template(
    gray_screenshot: "MatLike", button_image: "MatLike"
) -> tuple[float, tuple[int, int]]:
    """Perform template matching synchronously (CPU-intensive operation).

    Args:
        gray_screenshot (MatLike): Grayscale screenshot image.
        button_image (MatLike): Grayscale template image.

    Returns:
        tuple[float, tuple[int, int]]: (max_val, max_loc) from matching.

    Notes:
        This function is designed to run in a thread pool for better performance.
    """
    gray_matched = cv2.matchTemplate(
        image=gray_screenshot,
        templ=button_image,
        method=cv2.TM_CCOEFF_NORMED,
        result=None,
        mask=None,
    )
    _, max_val, _, max_loc = cv2.minMaxLoc(gray_matched)
    return max_val, max_loc


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
        """Record position data to CSV file asynchronously.

        This method runs the CSV I/O operations in a thread pool to avoid blocking.
        """

        def _sync_record_position() -> None:
            """Synchronous helper for CSV operations."""
            position_data = pd.DataFrame()
            position_log_path = Path("./logs/positions.csv")
            if position_log_path.exists():
                position_data = pd.read_csv(position_log_path)

            data_dict_list = [self.image_cfg.model_dump()]
            new_position_data = pd.DataFrame(data_dict_list).astype(str)
            merged_data = pd.concat([position_data, new_position_data], ignore_index=True)
            merged_data = merged_data.drop_duplicates(
                subset=["image_name", "image_path"], keep="last"
            )
            merged_data = merged_data.reset_index(drop=True)
            merged_data.to_csv(position_log_path.as_posix(), index=False)

        # Run CSV operations in thread pool to avoid blocking
        await asyncio.to_thread(_sync_record_position)

    async def find(self) -> FoundPosition:
        """Finds the position of a button image within a screenshot.

        Raises:
            ValueError: If an invalid alignment value is provided.

        Returns:
            FoundPosition: The found position of the button image.

        Notes:
            CPU-intensive template matching is run in a thread pool for better performance.
        """
        # Convert screenshot to numpy array and grayscale in one step
        if isinstance(self.screenshot, bytes):
            # For bytes, decode directly to grayscale
            screenshot_array = np.frombuffer(self.screenshot, dtype=np.uint8)
            color_screenshot = cv2.imdecode(screenshot_array, cv2.IMREAD_COLOR)
        else:
            # For PIL Image, convert to array
            color_screenshot = np.array(self.screenshot)
            color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)

        # Convert screenshot to grayscale
        gray_screenshot: MatLike = cv2.cvtColor(color_screenshot, cv2.COLOR_BGR2GRAY)

        # Load and convert template image (cached)
        button_image: MatLike = _load_and_convert_template(self.image_cfg.image_path)

        # Match the button image with the screenshot (run in thread pool)
        max_val, max_loc = await asyncio.to_thread(
            _sync_match_template, gray_screenshot, button_image
        )

        if max_val > self.image_cfg.confidence:
            logfire.info(
                "Found Position from Current Screen",
                max_val=max_val,
                **self.image_cfg.model_dump(exclude_none=True),
            )

            # Calculate X and Y coordinates of the button center
            click_x = int(max_loc[0] + button_image.shape[1] // 2)
            click_y = int(max_loc[1] + button_image.shape[0] // 2)
            logfire.info(
                "Found Image",
                button_x=click_x,
                button_y=click_y,
                button_name_en=Path(self.image_cfg.image_path).stem,
                button_name_cn=self.image_cfg.image_name,
            )

            return FoundPosition(
                button_x=click_x,
                button_y=click_y,
                found_button_name_en=Path(self.image_cfg.image_path).stem,
                found_button_name_cn=self.image_cfg.image_name,
            )
        return FoundPosition()
