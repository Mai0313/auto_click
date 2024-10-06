from typing import Union

import cv2
import numpy as np
from pydantic import Field, BaseModel, ConfigDict, computed_field
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page

from src.types.image_models import ImageModel
from src.types.output_models import FoundPosition, ShiftPosition


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

    @computed_field
    @property
    def __screenshot_array(self) -> tuple[np.ndarray, np.ndarray]:
        """Converts the screenshot to color and grayscale arrays.

        Returns:
            color_screenshot (np.ndarray): The screenshot in color format.
            gray_screenshot (np.ndarray): The screenshot in grayscale format.
        """
        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2GRAY)
        return color_screenshot, gray_screenshot

    def __draw_rectangle(
        self, matched_image_position: tuple[int, int], max_loc: cv2.typing.Point, draw_black: bool
    ) -> cv2.typing.MatLike:
        """Draws a rectangle on the image and saves the resulting image.

        Args:
            matched_image_position (tuple[int, int]): The position of the matched image.
            max_loc (cv2.typing.Point): The maximum location of the matched image.
            draw_black (bool): Flag indicating whether to draw a black rectangle.

        Returns:
            color_screenshot (np.ndarray): The screenshot with the red rectangle drawn on it.

        Todo:
            Add logging functionality
        """
        color_screenshot, _ = self.__screenshot_array

        if draw_black:
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
        return color_screenshot

    def find(self) -> FoundPosition:
        """Finds the position of a button image within a screenshot.

        Returns:
            button_center_x (int): The x-coordinate of the button center.
            button_center_y (int): The y-coordinate of the button center.
            color_screenshot (np.ndarray): The screenshot with the red rectangle drawn on it.

        Todo:
            Add logging functionality
        """
        button_center_x, button_center_y = 0, 0
        _, gray_screenshot = self.__screenshot_array
        button_image = cv2.imread(self.image_cfg.image_path, 0)

        result = cv2.matchTemplate(gray_screenshot, button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        button_center_x = int(max_loc[0] + button_image.shape[1])
        button_center_y = int(max_loc[1] + button_image.shape[0])
        matched_image_position = (button_center_x, button_center_y)

        color_screenshot = self.__draw_rectangle(
            matched_image_position=matched_image_position, max_loc=max_loc, draw_black=False
        )
        blackout_screenshot = self.__draw_rectangle(
            matched_image_position=matched_image_position, max_loc=max_loc, draw_black=True
        )

        if max_val > self.image_cfg.confidence:
            return FoundPosition(
                button_center_x=button_center_x,
                button_center_y=button_center_y,
                color_screenshot=color_screenshot,
                blackout_screenshot=blackout_screenshot,
            )
        return FoundPosition(
            button_center_x=None,
            button_center_y=None,
            color_screenshot=color_screenshot,
            blackout_screenshot=blackout_screenshot,
        )
