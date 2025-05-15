from typing import Optional
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import logfire
from pydantic import Field, BaseModel, ConfigDict
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page

from .screenshot import ShiftPosition
from .types.config import ImageModel


class FoundPosition(BaseModel):
    """Represents the position of a found button on the screen.

    Attributes:
        button_x (Optional[int]): The x-coordinate of the button center.
        button_y (Optional[int]): The y-coordinate of the button center.
        found_button_name_en (Optional[str]): The name of the found button in English.
        found_button_name_cn (Optional[str]): The name of the found button in Chinese.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    button_x: Optional[int] = Field(
        default=None,
        description="The x-coordinate of the button center.",
        frozen=False,
        deprecated=False,
    )
    button_y: Optional[int] = Field(
        default=None,
        description="The y-coordinate of the button center.",
        frozen=False,
        deprecated=False,
    )
    found_button_name_en: Optional[str] = Field(
        default=None,
        description="The name of the found button in English.",
        frozen=True,
        deprecated=False,
    )
    found_button_name_cn: Optional[str] = Field(
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
        device (Union[Page, AdbDevice, ShiftPosition]): The device.

    Methods:
        __save_images: Saves the images to the logs directory.
        __draw_rectangle: Draws a rectangle on the image and saves the resulting image.
        find: Finds the position of a button image within a screenshot.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Image.Image | bytes = Field(..., description="The screenshot image")
    device: Page | AdbDevice | ShiftPosition = Field(..., description="The device")

    async def __save_images(self, image_type: str, screenshot: np.ndarray) -> None:
        log_dir = Path(f"./logs/{image_type}")
        log_dir.mkdir(exist_ok=True, parents=True)
        screenshot_path = log_dir / Path(self.image_cfg.image_path).with_suffix(".png").name
        if not screenshot_path.exists():
            cv2.imwrite(str(screenshot_path.absolute()), screenshot)

    async def __draw_red_rectangle(
        self, screenshot: np.ndarray, button_x: int, button_y: int, max_loc: cv2.typing.Point
    ) -> np.ndarray:
        matched_image_position = (button_x, button_y)
        cv2.rectangle(screenshot, max_loc, matched_image_position, (0, 0, 255), 2)
        await self.__save_images(image_type="detected", screenshot=screenshot)
        return screenshot

    async def __draw_green_square(
        self,
        screenshot: np.ndarray,
        button_x: int,
        button_y: int,
        max_loc: cv2.typing.Point,
        click_x: int,
        click_y: int,
    ) -> np.ndarray:
        square_size = 10  # Adjust as needed
        half_square = square_size // 2

        top_left_square_x = max(click_x - half_square, max_loc[0])
        top_left_square_y = max(click_y - half_square, max_loc[1])
        bottom_right_square_x = min(click_x + half_square, button_x)
        bottom_right_square_y = min(click_y + half_square, button_y)
        top_left_square = (top_left_square_x, top_left_square_y)
        bottom_right_square = (bottom_right_square_x, bottom_right_square_y)

        cv2.rectangle(screenshot, top_left_square, bottom_right_square, (61, 145, 64), 2)
        await self.__save_images(image_type="point", screenshot=screenshot)
        return screenshot

    async def __blackout_region(
        self, screenshot: np.ndarray, button_x: int, button_y: int, max_loc: cv2.typing.Point
    ) -> np.ndarray:
        matched_image_position = (button_x, button_y)
        masked_screenshot = np.zeros_like(screenshot)
        cv2.rectangle(masked_screenshot, max_loc, matched_image_position, (255, 255, 255), -1)
        black_img = np.zeros_like(screenshot)
        screenshot = cv2.bitwise_and(screenshot, masked_screenshot) + cv2.bitwise_and(
            black_img, cv2.bitwise_not(masked_screenshot)
        )
        await self.__save_images(image_type="blackout", screenshot=screenshot)
        return screenshot

    async def __crop_and_save(
        self, screenshot: np.ndarray, button_x: int, button_y: int, max_loc: cv2.typing.Point
    ) -> np.ndarray:
        top_left = max_loc
        bottom_right = (button_x, button_y)
        cropped_region = screenshot[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
        await self.__save_images(image_type="cropped", screenshot=cropped_region)
        return cropped_region

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
            click_x = int(max_loc[0] + width // 2)

            # Calculate click_y
            click_y = int(max_loc[1] + height // 2)

            # if self.image_cfg.enable_screenshot:
            #     # Calculate the bottom-right corner of the matched template
            #     button_x = int(max_loc[0] + width)
            #     button_y = int(max_loc[1] + height)

            #     await self.record_position()
            #     await self.__save_images(image_type="color", screenshot=color_screenshot)
            #     tasks = [
            #         self.__draw_red_rectangle(
            #             screenshot=color_screenshot.copy(),
            #             button_x=button_x,
            #             button_y=button_y,
            #             max_loc=max_loc,
            #         ),
            #         self.__draw_green_square(
            #             screenshot=color_screenshot.copy(),
            #             button_x=button_x,
            #             button_y=button_y,
            #             max_loc=max_loc,
            #             click_x=click_x,
            #             click_y=click_y,
            #         ),
            #         self.__blackout_region(
            #             screenshot=color_screenshot.copy(),
            #             button_x=button_x,
            #             button_y=button_y,
            #             max_loc=max_loc,
            #         ),
            #         self.__crop_and_save(
            #             screenshot=color_screenshot.copy(),
            #             button_x=button_x,
            #             button_y=button_y,
            #             max_loc=max_loc,
            #         ),
            #     ]

            #     await asyncio.gather(*tasks)

            return FoundPosition(
                button_x=click_x,
                button_y=click_y,
                found_button_name_en=Path(self.image_cfg.image_path).stem,
                found_button_name_cn=self.image_cfg.image_name,
            )
        return FoundPosition()
