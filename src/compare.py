from typing import Union, Literal
import asyncio
from pathlib import Path

import cv2
import numpy as np
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page

from .types.image_models import ImageModel
from .types.output_models import FoundPosition, ShiftPosition


class ImageComparisonMode(BaseModel):
    pass


class ImageComparison(BaseModel):
    """Represents an image comparison object.

    This class provides methods to compare an image with a screenshot and find the position of a button image within the screenshot.

    Attributes:
        image_cfg (ImageModel): The image configuration.
        screenshot (Union[Image.Image, bytes]): The screenshot image.
        device (Union[Page, AdbDevice, ShiftPosition]): The device.

    Methods:
        __save_images: Saves the images to the logs directory.
        __draw_rectangle: Draws a rectangle on the image and saves the resulting image.
        find: Finds the position of a button image within a screenshot.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Union[Image.Image, bytes] = Field(..., description="The screenshot image")
    device: Union[Page, AdbDevice, ShiftPosition] = Field(..., description="The device")

    async def __save_images(self, image_type: str, screenshot: np.ndarray) -> None:
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True, parents=True)
        screenshot_path = (
            log_dir / Path(self.image_cfg.image_path).with_suffix(f".{image_type}.png").name
        )
        if not screenshot_path.exists():
            cv2.imwrite(str(screenshot_path.absolute()), screenshot)

    async def __draw_rectangle(
        self,
        screenshot: np.ndarray,
        button_x: int,
        button_y: int,
        max_loc: cv2.typing.Point,
        draw_black: bool,
        click_x: int,
        click_y: int,
    ) -> np.ndarray:
        """Draws a rectangle on the image, draws a small square at the click position, and saves the resulting image.

        Args:
            screenshot (np.ndarray): The screenshot in color format.
            button_x (int): The x-coordinate of the bottom-right corner of the matched template.
            button_y (int): The y-coordinate of the bottom-right corner of the matched template.
            max_loc (cv2.typing.Point): The top-left corner of the matched template.
            draw_black (bool): Flag indicating whether to draw a black rectangle.
            click_x (int): The x-coordinate of the click position.
            click_y (int): The y-coordinate of the click position.

        Returns:
            screenshot (np.ndarray): The screenshot with the rectangle and click position drawn on it.
        """
        matched_image_position = (button_x, button_y)

        # Draw the red rectangle on the image
        cv2.rectangle(screenshot, max_loc, matched_image_position, (0, 0, 255), 2)

        # Draw the small green square at the click position
        square_size = 10  # Adjust size as needed
        half_square = square_size // 2

        # Ensure the green square stays within the red rectangle
        top_left_square_x = max(click_x - half_square, max_loc[0])
        top_left_square_y = max(click_y - half_square, max_loc[1])
        bottom_right_square_x = min(click_x + half_square, button_x)
        bottom_right_square_y = min(click_y + half_square, button_y)
        top_left_square = (top_left_square_x, top_left_square_y)
        bottom_right_square = (bottom_right_square_x, bottom_right_square_y)

        cv2.rectangle(screenshot, top_left_square, bottom_right_square, (61, 145, 64), 2)

        await self.__save_images(image_type="color", screenshot=screenshot)

        if draw_black:
            # Create a mask with a white rectangle to keep the area inside the red box
            masked_screenshot = np.zeros_like(screenshot)
            cv2.rectangle(masked_screenshot, max_loc, matched_image_position, (255, 255, 255), -1)
            # Create a fully black image
            black_img = np.zeros_like(screenshot)
            # Keep the red box area, black out the rest
            screenshot = cv2.bitwise_and(screenshot, masked_screenshot) + cv2.bitwise_and(
                black_img, cv2.bitwise_not(masked_screenshot)
            )
            await self.__save_images(image_type="blackout", screenshot=screenshot)

        # Crop the internal region of the rectangle
        top_left = max_loc
        bottom_right = (button_x, button_y)
        cropped_region = screenshot[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
        await self.__save_images(image_type="cropped", screenshot=cropped_region)

        return screenshot

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
            width = button_image.shape[1]
            height = button_image.shape[0]

            # Calculate the bottom-right corner of the matched template
            button_x = int(max_loc[0] + width)
            button_y = int(max_loc[1] + height)

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

            if self.image_cfg.screenshot_option:
                tasks = []
                for draw_black in [True, False]:
                    task = asyncio.create_task(
                        self.__draw_rectangle(
                            screenshot=color_screenshot.copy(),
                            button_x=button_x,
                            button_y=button_y,
                            max_loc=max_loc,
                            draw_black=draw_black,
                            click_x=click_x,
                            click_y=click_y,
                        )
                    )
                    tasks.append(task)

                await asyncio.gather(*tasks)

            return FoundPosition(
                button_x=click_x,
                button_y=click_y,
                found_button_name_en=Path(self.image_cfg.image_path).stem,
                found_button_name_cn=self.image_cfg.image_name,
            )
        return FoundPosition()
