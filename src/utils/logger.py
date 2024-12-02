from enum import Enum
from typing import Union, Literal
from pathlib import Path

import cv2
import numpy as np
from pydantic import BaseModel, computed_field


class ImageType(str, Enum):
    COLOR = "color"
    BLACKOUT = "blackout"


class CustomLogger(BaseModel):
    original_image_path: str

    @computed_field
    @property
    def image_name(self) -> str:
        return Path(self.original_image_path).name

    async def save_images(
        self,
        images: Union[np.ndarray, dict[ImageType, np.ndarray]],
        save_to: Literal["local", "both"] = "both",
    ) -> None:
        if isinstance(images, np.ndarray):
            images = {ImageType.COLOR: images}

        for image_type, screenshot in images.items():
            if save_to in ("local", "both"):
                await self.__save_image_local(screenshot, image_type)

    async def __save_image_local(self, screenshot: np.ndarray, image_type: ImageType) -> None:
        log_dir = Path(f"./logs/{image_type}")
        log_dir.mkdir(exist_ok=True, parents=True)
        screenshot_path = log_dir / self.image_name
        if not screenshot_path.exists():
            cv2.imwrite(str(screenshot_path.absolute()), screenshot)
