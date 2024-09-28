import os
from typing import Union

import cv2
import numpy as np
import logfire
from pydantic import Field, BaseModel, ConfigDict, computed_field
import PIL.Image as Image
from adbutils._device import AdbDevice
from playwright.sync_api import Page

from .types import ImageModel, ShiftPosition


class ImageComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Union[Image.Image, bytes] = Field(..., description="The screenshot image")
    device: Union[Page, AdbDevice, ShiftPosition] = Field(..., description="The device")

    @computed_field
    @property
    def __screenshot_array(self) -> tuple[np.ndarray, np.ndarray]:
        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2GRAY)
        return color_screenshot, gray_screenshot

    @computed_field
    @property
    def __log_filename(self) -> str:
        # now = datetime.datetime.now().strftime("%Y%m%d")
        log_dir = "./logs"
        os.makedirs(log_dir, exist_ok=True)
        image_name = self.image_cfg.image_path.split("/")[-1].split(".")[0]
        log_filename = f"{log_dir}/{image_name}.png"
        return log_filename

    @computed_field
    @property
    def __button_image(self) -> cv2.typing.MatLike:
        __button_image = cv2.imread(self.image_cfg.image_path, 0)
        if __button_image is None:
            logfire.warn("Unable to load button image", **self.image_cfg.model_dump())
        return __button_image

    def __draw_rectangle(
        self, matched_image_position: tuple[int, int], max_loc: cv2.typing.Point, draw_black: bool
    ) -> None:
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
        # Save the resulting image
        cv2.imwrite(self.__log_filename, color_screenshot)
        logfire.info(
            "The screenshot has been saved",
            log_filename=self.__log_filename,  # Remove leading underscores
            **self.image_cfg.model_dump(),
        )

    def find(self) -> tuple[int, int]:
        button_center_x, button_center_y = 0, 0
        _, gray_screenshot = self.__screenshot_array

        result = cv2.matchTemplate(gray_screenshot, self.__button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        button_center_x = int(max_loc[0] + self.__button_image.shape[1])
        button_center_y = int(max_loc[1] + self.__button_image.shape[0])
        matched_image_position = (button_center_x, button_center_y)

        if max_val > self.image_cfg.confidence:
            logfire.info(
                "Found the target image",
                confidence_decision=max_val,
                button_center_x=button_center_x,
                button_center_y=button_center_y,
                **self.image_cfg.model_dump(),
            )
            if self.image_cfg.screenshot_option is True:
                self.__draw_rectangle(
                    matched_image_position=matched_image_position, max_loc=max_loc, draw_black=True
                )
        return button_center_x, button_center_y
