from io import BytesIO
import os
from typing import Union
import datetime

import cv2
import numpy as np
from pydantic import Field, BaseModel, ConfigDict, computed_field, model_validator
import PIL.Image as Image
from src.utils.logger import logfire
from src.models.image_models import Settings


class ImageComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: Settings = Field(..., description="The image configuration")
    check_list: list[str] = Field(
        ..., description="The check list, it should be a list of image names"
    )
    screenshot: Union[Image.Image, bytes] = Field(..., description="The screenshot image")

    @model_validator(mode="after")
    def get_screenshot_image(self) -> Union[Image.Image, bytes]:
        if isinstance(self.screenshot, bytes):
            image_stream = BytesIO(self.screenshot)
            return Image.open(image_stream)
        return self.screenshot

    @computed_field
    @property
    def screenshot_array(self) -> tuple[np.ndarray, np.ndarray]:
        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2GRAY)
        return color_screenshot, gray_screenshot

    @computed_field
    @property
    def log_filename(self) -> str:
        log_dir = "./data/logs"
        os.makedirs(log_dir, exist_ok=True)
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{log_dir}/{now}.png"
        return log_filename

    @computed_field
    @property
    def button_image(self) -> cv2.typing.MatLike:
        button_image = cv2.imread(self.image_cfg.image_path, 0)
        if button_image is None:
            logfire.fatal(
                "Unable to load button image from path: {image_path}",
                image_path=self.image_cfg.image_path,
                _tags=["Fatal Error"],
            )
            raise Exception(f"Unable to load button image from path: {self.image_cfg.image_path}")
        return button_image

    def draw_rectangle(
        self, matched_image_position: tuple[int, int], max_loc: cv2.typing.Point
    ) -> None:
        color_screenshot, _ = self.screenshot_array
        cv2.rectangle(color_screenshot, max_loc, matched_image_position, (0, 0, 255), 2)
        cv2.imwrite(self.log_filename, color_screenshot)
        logfire.warn(
            "The screenshot has been taken under {log_filename}",
            log_filename=self.log_filename,
            _tags=["Screenshot"],
        )

    def find(self) -> tuple[Union[int, None], Union[int, None]]:
        if self.image_cfg.image_name not in self.check_list:
            return None, None

        _, gray_screenshot = self.screenshot_array

        result = cv2.matchTemplate(gray_screenshot, self.button_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        button_center_x = int(max_loc[0] + self.button_image.shape[1])
        button_center_y = int(max_loc[1] + self.button_image.shape[0])
        matched_image_position = (button_center_x, button_center_y)

        if max_val > self.image_cfg.confidence:
            logfire.info(
                "{image_name} Found with confidence: {confidence} > {set_confidence} at position: {matched_image_position}",
                image_name=self.image_cfg.image_name,
                set_confidence=self.image_cfg.confidence,
                confidence=max_val,
                matched_image_position=matched_image_position,
                _tags=[self.image_cfg.image_name],
                _exc_info=self.image_cfg,
            )
            if self.image_cfg.screenshot_option is True:
                self.draw_rectangle(matched_image_position, max_loc)
            return button_center_x, button_center_y
        return None, None

    def find_orb(self) -> tuple[Union[int, None], Union[int, None]]:
        """Finds the location of a button in a screenshot.

        Returns:
            A tuple containing the x and y coordinates of the button's center.
            If the button is not found, returns (None, None).
        """
        if self.image_cfg.image_name not in self.check_list:
            return None, None

        color_screenshot, gray_screenshot = self.screenshot_array

        orb = cv2.ORB_create()

        keypoints_button, descriptors_button = orb.detectAndCompute(self.button_image, None)
        keypoints_screenshot, descriptors_screenshot = orb.detectAndCompute(gray_screenshot, None)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors_button, descriptors_screenshot)

        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) > 0:
            best_match = matches[0]
            button_center_x = int(keypoints_screenshot[best_match.trainIdx].pt[0])
            button_center_y = int(keypoints_screenshot[best_match.trainIdx].pt[1])

            if self.image_cfg.screenshot_option is True:
                self.draw_rectangle(
                    (button_center_x, button_center_y),
                    (
                        int(keypoints_button[best_match.queryIdx].pt[0]),
                        int(keypoints_button[best_match.queryIdx].pt[1]),
                    ),
                )

            return button_center_x, button_center_y

        return None, None

    def find_sift(self) -> tuple[Union[int, None], Union[int, None]]:
        """Finds the location of a button in a screenshot using SIFT feature matching.

        Returns:
            A tuple containing the x and y coordinates of the center of the matched button.
            If no match is found, returns (None, None).
        """
        if self.image_cfg.image_name not in self.check_list:
            return None, None

        color_screenshot, gray_screenshot = self.screenshot_array

        # Initialize SIFT detector
        sift = cv2.SIFT_create()

        # Detect keypoints and descriptors
        keypoints_button, descriptors_button = sift.detectAndCompute(self.button_image, None)
        keypoints_screenshot, descriptors_screenshot = sift.detectAndCompute(gray_screenshot, None)

        # Use BFMatcher for matching
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors_button, descriptors_screenshot, k=2)

        # Apply Lowe's ratio test to filter matching points
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        if len(good_matches) > 0:
            # Get the position of the best match keypoint
            best_match = good_matches[0]
            button_center_x = int(keypoints_screenshot[best_match.trainIdx].pt[0])
            button_center_y = int(keypoints_screenshot[best_match.trainIdx].pt[1])

            if self.image_cfg.screenshot_option is True:
                self.draw_rectangle(
                    (button_center_x, button_center_y),
                    (
                        int(keypoints_button[best_match.queryIdx].pt[0]),
                        int(keypoints_button[best_match.queryIdx].pt[1]),
                    ),
                )

            return button_center_x, button_center_y

        return None, None
