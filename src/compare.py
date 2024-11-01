from typing import Union, Literal
import asyncio
from pathlib import Path

import cv2
import numpy as np
import mlflow
import logfire
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page
from playwright.async_api import Page as APage

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

    async def __get_screenshot_array(self) -> tuple[np.ndarray, np.ndarray]:
        """Converts the screenshot to color and grayscale arrays.

        Returns:
            color_screenshot (np.ndarray): The screenshot in color format.
            gray_screenshot (np.ndarray): The screenshot in grayscale format.
        """
        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_BGR2GRAY)
        return color_screenshot, gray_screenshot

    async def __draw_rectangle(
        self,
        color_screenshot: np.ndarray,
        matched_image_position: tuple[int, int],
        max_loc: cv2.typing.Point,
        draw_black: bool,
    ) -> np.ndarray:
        """Draws a rectangle on the image and saves the resulting image.

        Args:
            color_screenshot (np.ndarray): The screenshot in color format.
            matched_image_position (tuple[int, int]): The position of the matched image.
            max_loc (cv2.typing.Point): The maximum location of the matched image.
            draw_black (bool): Flag indicating whether to draw a black rectangle.

        Returns:
            color_screenshot (np.ndarray): The screenshot with the red rectangle drawn on it.
        """
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

    async def find_and_select(
        self,
        vertical_align: Literal["top", "center", "bottom"] = "center",
        horizontal_align: Literal["left", "center", "right"] = "center",
    ) -> FoundPosition:
        """Finds the position of a button image within a screenshot.

        Args:
            vertical_align (Literal['top', 'center', 'bottom'], optional): Vertical alignment within the matched rectangle. Defaults to 'center'.
            horizontal_align (Literal['left', 'center', 'right'], optional): Horizontal alignment within the matched rectangle. Defaults to 'center'.

        Returns:
            FoundPosition: An object containing the coordinates and other information.

        Raises:
            ValueError: If an invalid alignment is provided.

        """
        color_screenshot, gray_screenshot = await self.__get_screenshot_array()
        image_path = Path(self.image_cfg.image_path)
        image_name_en = image_path.stem
        image_name_cn = self.image_cfg.image_name
        button_image = cv2.imread(image_path.as_posix(), 0)

        result = cv2.matchTemplate(gray_screenshot, button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > self.image_cfg.confidence:
            x = max_loc[0]
            y = max_loc[1]
            template_width = button_image.shape[1]
            template_height = button_image.shape[0]

            # Determine alignment positions within the matched rectangle
            if horizontal_align == "left":
                x_align = x
            elif horizontal_align == "center":
                x_align = x + template_width / 2
            elif horizontal_align == "right":
                x_align = x + template_width
            else:
                raise ValueError(f"Invalid horizontal_align: {horizontal_align}")

            if vertical_align == "top":
                y_align = y
            elif vertical_align == "center":
                y_align = y + template_height / 2
            elif vertical_align == "bottom":
                y_align = y + template_height
            else:
                raise ValueError(f"Invalid vertical_align: {vertical_align}")

            # Define the small rectangle size
            small_rect_size = 10  # Size of the small square
            half_size = small_rect_size / 2

            # Calculate the top-left and bottom-right points of the small rectangle
            small_rect_top_left = (int(x_align - half_size), int(y_align - half_size))
            small_rect_bottom_right = (int(x_align + half_size), int(y_align + half_size))

            # Ensure the small rectangle is within image boundaries
            img_height, img_width = color_screenshot.shape[:2]
            small_rect_top_left = (max(0, small_rect_top_left[0]), max(0, small_rect_top_left[1]))
            small_rect_bottom_right = (
                min(img_width, small_rect_bottom_right[0]),
                min(img_height, small_rect_bottom_right[1]),
            )

            # Draw the matched template rectangle (optional)
            cv2.rectangle(
                color_screenshot, (x, y), (x + template_width, y + template_height), (255, 0, 0), 2
            )

            # Draw the small rectangle at the specified alignment point
            cv2.rectangle(
                color_screenshot, small_rect_top_left, small_rect_bottom_right, (0, 0, 255), 2
            )

            # Calculate the center of the small rectangle
            button_x = int((small_rect_top_left[0] + small_rect_bottom_right[0]) / 2)
            button_y = int((small_rect_top_left[1] + small_rect_bottom_right[1]) / 2)

            # Calibrate the coordinates if necessary
            calibrated_x, calibrated_y = await self.a_calibrate(
                button_center_x=button_x, button_center_y=button_y
            )
            # matched_image_position = (calibrated_x, calibrated_y)

            # Update the blackout_screenshot if needed (depends on your implementation)
            blackout_screenshot = color_screenshot.copy()
            cv2.rectangle(
                blackout_screenshot, small_rect_top_left, small_rect_bottom_right, (0, 0, 0), -1
            )

            # Logging and metrics (adjust as needed)
            logfire.info(
                f"Found {image_name_cn}",
                button_x=button_x,
                calibrated_x=calibrated_x,
                button_y=button_y,
                calibrated_y=calibrated_y,
                button_name_en=image_name_en,
                button_name_cn=image_name_cn,
                button_file_path=image_path.as_posix(),
                auto_click=self.image_cfg.click_this,
            )
            mlflow.log_metrics(
                metrics={
                    "button_x": button_x,
                    "calibrated_x": calibrated_x,
                    "button_y": button_y,
                    "calibrated_y": calibrated_y,
                }
            )

            return FoundPosition(
                button_center_x=button_x,
                calibrated_x=calibrated_x,
                button_center_y=button_y,
                calibrated_y=calibrated_y,
                found_button_name_en=image_name_en,
                found_button_name_cn=image_name_cn,
                color_screenshot=color_screenshot,
                blackout_screenshot=blackout_screenshot,
            )
        return FoundPosition(
            button_center_x=None,
            calibrated_x=None,
            button_center_y=None,
            calibrated_y=None,
            found_button_name_en=None,
            found_button_name_cn=None,
            color_screenshot=None,
            blackout_screenshot=None,
        )

    async def find(self) -> FoundPosition:
        """Finds the position of a button image within a screenshot.

        Returns:
            button_center_x (int): The x-coordinate of the button center.
            button_center_y (int): The y-coordinate of the button center.
            color_screenshot (np.ndarray): The screenshot with the red rectangle drawn on it.

        Todo:
            Add logging functionality
        """
        button_center_x, button_center_y = 0, 0
        color_screenshot, gray_screenshot = await self.__get_screenshot_array()
        image_path = Path(self.image_cfg.image_path)
        image_name_en = image_path.stem
        image_name_cn = self.image_cfg.image_name
        button_image = cv2.imread(image_path.as_posix(), 0)

        result = cv2.matchTemplate(gray_screenshot, button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > self.image_cfg.confidence:
            button_center_x = int(max_loc[0] + button_image.shape[1])
            button_center_y = int(max_loc[1] + button_image.shape[0])

            calibrated_x, calibrated_y = await self.a_calibrate(
                button_center_x=button_center_x, button_center_y=button_center_y
            )
            matched_image_position = (calibrated_x, calibrated_y)

            tasks = [
                asyncio.create_task(
                    self.__draw_rectangle(
                        color_screenshot=color_screenshot,
                        matched_image_position=matched_image_position,
                        max_loc=max_loc,
                        draw_black=False,
                    )
                ),
                asyncio.create_task(
                    self.__draw_rectangle(
                        color_screenshot=color_screenshot,
                        matched_image_position=matched_image_position,
                        max_loc=max_loc,
                        draw_black=True,
                    )
                ),
            ]

            blackout_screenshot, color_screenshot = await asyncio.gather(*tasks)

            logfire.info(
                f"Found {image_name_cn}",
                button_center_x=button_center_x,
                calibrated_x=calibrated_x,
                button_center_y=button_center_y,
                calibrated_y=calibrated_y,
                button_name_en=image_name_en,
                button_name_cn=image_name_cn,
                button_file_path=image_path.as_posix(),
                auto_click=self.image_cfg.click_this,
            )
            mlflow.log_metrics(
                metrics={
                    "button_center_x": button_center_x,
                    "calibrated_x": calibrated_x,
                    "button_center_y": button_center_y,
                    "calibrated_y": calibrated_y,
                }
            )
            return FoundPosition(
                button_center_x=button_center_x,
                calibrated_x=calibrated_x,
                button_center_y=button_center_y,
                calibrated_y=calibrated_y,
                found_button_name_en=image_name_en,
                found_button_name_cn=image_name_cn,
                color_screenshot=color_screenshot,
                blackout_screenshot=blackout_screenshot,
            )
        return FoundPosition(
            button_center_x=None,
            calibrated_x=None,
            button_center_y=None,
            calibrated_y=None,
            found_button_name_en=None,
            found_button_name_cn=None,
            color_screenshot=None,
            blackout_screenshot=None,
        )

    def calibrate(self, button_center_x: int, button_center_y: int) -> tuple[int, int]:
        """Adjusts the button center coordinates based on the device type.

        Args:
            button_center_x (int): The x-coordinate of the button center.
            button_center_y (int): The y-coordinate of the button center.

        Returns:
            tuple[int, int]: The adjusted button center coordinates.
        """
        # if the device is from a window process, we need to add shift_x, shift_y to the button_center_x, button_center_y
        # since we do not know the exact position of the window.
        if isinstance(self.device, Page):
            # button_center_x = button_center_x // 2
            # button_center_y = button_center_y // 2
            pass
        if isinstance(self.device, APage):
            # button_center_x = button_center_x // 2
            # button_center_y = button_center_y // 2
            pass
        if isinstance(self.device, AdbDevice):
            # button_center_x = button_center_x // 2
            # button_center_y = button_center_y // 2
            pass
        if isinstance(self.device, ShiftPosition):
            button_center_x = button_center_x + self.device.shift_x
            button_center_y = button_center_y + self.device.shift_y
        return button_center_x, button_center_y

    async def a_calibrate(self, button_center_x: int, button_center_y: int) -> tuple[int, int]:
        """Adjusts the button center coordinates based on the device type.

        Args:
            button_center_x (int): The x-coordinate of the button center.
            button_center_y (int): The y-coordinate of the button center.

        Returns:
            tuple[int, int]: The adjusted button center coordinates.
        """
        return await asyncio.to_thread(self.calibrate, button_center_x, button_center_y)
