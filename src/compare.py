from typing import Union
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


class ImageComparison(BaseModel):
    """Represents an image comparison object.

    This class provides methods to compare an image with a screenshot and find the position of a button image within the screenshot.

    Attributes:
        image_cfg (ImageModel): The image configuration.
        screenshot (Union[Image.Image, bytes]): The screenshot image.
        device (Union[Page, AdbDevice, ShiftPosition]): The device.

    Methods:
        __screenshot_array: Converts the screenshot to color and grayscale arrays.
        __draw_rectangle: Draws a rectangle on the image and saves the resulting image.
        find: Finds the position of a button image within a screenshot.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Union[Image.Image, bytes] = Field(..., description="The screenshot image")
    device: Union[Page, AdbDevice, ShiftPosition] = Field(..., description="The device")

    async def save_images(self, images: dict[str, np.ndarray]) -> None:
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True, parents=True)

        for image_type, screenshot in images.items():
            screenshot_path = (
                log_dir / Path(self.image_cfg.image_path).with_suffix(f".{image_type}.png").name
            )
            if not screenshot_path.exists():
                cv2.imwrite(str(screenshot_path.absolute()), screenshot)

    async def __draw_rectangle(
        self,
        color_screenshot: np.ndarray,
        button_center_x: int,
        button_center_y: int,
        max_loc: cv2.typing.Point,
        draw_black: bool,
    ) -> np.ndarray:
        """Draws a rectangle on the image and saves the resulting image.

        Args:
            color_screenshot (np.ndarray): The screenshot in color format.
            button_center_x (int): The x-coordinate of the button center.
            button_center_y (int): The y-coordinate of the button center.
            max_loc (cv2.typing.Point): The maximum location of the matched image.
            draw_black (bool): Flag indicating whether to draw a black rectangle.

        Returns:
            color_screenshot (np.ndarray): The screenshot with the red rectangle drawn on it.
        """
        image_type = "color"
        matched_image_position = (button_center_x, button_center_y)
        if draw_black:
            image_type = "blackout"
            # Create a mask with a white rectangle to keep the area inside the red box
            masked_color_screenshot = np.zeros_like(color_screenshot)
            cv2.rectangle(
                masked_color_screenshot, max_loc, matched_image_position, (255, 255, 255), -1
            )
            # Create a fully black image
            black_img = np.zeros_like(color_screenshot)
            # Keep the red box area, black out the rest
            color_screenshot = cv2.bitwise_and(
                color_screenshot, masked_color_screenshot
            ) + cv2.bitwise_and(black_img, cv2.bitwise_not(masked_color_screenshot))

        # Draw the red rectangle on the image
        cv2.rectangle(color_screenshot, max_loc, matched_image_position, (0, 0, 255), 2)
        await self.save_images(images={image_type: color_screenshot})
        return color_screenshot

    async def __color_similarity_2d(self, image: np.ndarray, color: tuple) -> np.ndarray:
        """Calculate the similarity between a given color and each pixel in a 2D image.

        Args:
            image (np.ndarray): 2D array representing the image.
            color (tuple): A tuple representing the RGB color (r, g, b).

        Returns:
            np.ndarray: A 2D array of uint8 values representing the similarity of each pixel to the given color.
        """
        # r, g, b = cv2.split(cv2.subtract(image, (*color, 0)))
        # positive = cv2.max(cv2.max(r, g), b)
        # r, g, b = cv2.split(cv2.subtract((*color, 0), image))
        # negative = cv2.max(cv2.max(r, g), b)
        # return cv2.subtract(255, cv2.add(positive, negative))
        diff = cv2.subtract(image, (*color, 0))
        r, g, b = cv2.split(diff)
        cv2.max(r, g, dst=r)
        cv2.max(r, b, dst=r)
        positive = r
        cv2.subtract((*color, 0), image, dst=diff)
        r, g, b = cv2.split(diff)
        cv2.max(r, g, dst=r)
        cv2.max(r, b, dst=r)
        negative = r
        cv2.add(positive, negative, dst=positive)
        cv2.subtract(255, positive, dst=positive)
        return positive

    async def find(self) -> FoundPosition:
        """Finds the position of a button image within a screenshot.

        Returns:
            FoundPosition: The found position of the button image.
        """
        _image_path = Path(self.image_cfg.image_path)

        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_BGR2GRAY)

        button_image = cv2.imread(_image_path.as_posix(), 0)

        gray_matched = cv2.matchTemplate(gray_screenshot, button_image, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, max_loc = cv2.minMaxLoc(gray_matched)

        if max_val > self.image_cfg.confidence:
            button_center_x = int(max_loc[0] + button_image.shape[1])
            button_center_y = int(max_loc[1] + button_image.shape[0])
            cv2.imwrite("gray_screenshot.png", gray_screenshot)
            cv2.imwrite("button_image.png", button_image)

            if self.image_cfg.screenshot_option:
                tasks = []
                for draw_black in [True, False]:
                    task = asyncio.create_task(
                        self.__draw_rectangle(
                            color_screenshot=color_screenshot,
                            button_center_x=button_center_x,
                            button_center_y=button_center_y,
                            max_loc=max_loc,
                            draw_black=draw_black,
                        )
                    )
                    tasks.append(task)

                await asyncio.gather(*tasks)
            return FoundPosition(
                button_center_x=button_center_x,
                button_center_y=button_center_y,
                found_button_name_en=_image_path.stem,
                found_button_name_cn=self.image_cfg.image_name,
            )
        return FoundPosition()
