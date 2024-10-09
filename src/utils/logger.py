from typing import Literal
from pathlib import Path

import cv2
import mlflow
from pydantic import BaseModel, computed_field


class CustomLogger(BaseModel):
    original_image_path: str

    @computed_field
    @property
    def image_name(self) -> str:
        return Path(self.original_image_path).name

    def save_single_image(
        self, screenshot: cv2.typing.MatLike, image_type: Literal["color", "blackout"]
    ) -> None:
        self._save_image(screenshot, image_type)

    def save_multiple_images(self, pair_dict: dict[str, cv2.typing.MatLike]) -> None:
        for image_type, screenshot in pair_dict.items():
            self._save_image(screenshot, image_type)

    def _save_image(self, screenshot: cv2.typing.MatLike, image_type: str) -> None:
        log_dir = Path(f"./logs/{image_type}")
        log_dir.mkdir(exist_ok=True, parents=True)
        screenshot_path = log_dir / self.image_name
        if not screenshot_path.exists():
            cv2.imwrite(str(screenshot_path.absolute()), screenshot)

    def save_single_image_mlflow(
        self, screenshot: cv2.typing.MatLike, image_type: Literal["color", "blackout"]
    ) -> None:
        self._log_image_mlflow(screenshot, image_type)

    def save_multiple_images_mlflow(self, pair_dict: dict[str, cv2.typing.MatLike]) -> None:
        for image_type, screenshot in pair_dict.items():
            self._log_image_mlflow(screenshot, image_type)

    def _log_image_mlflow(self, screenshot: cv2.typing.MatLike, image_type: str) -> None:
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        mlflow.log_image(image=screenshot_rgb, artifact_file=f"{image_type}/{self.image_name}")

    def save_all_image(
        self, screenshot: cv2.typing.MatLike, image_type: Literal["color", "blackout"]
    ) -> None:
        self.save_single_image(screenshot=screenshot, image_type=image_type)
        self.save_single_image_mlflow(screenshot=screenshot, image_type=image_type)

    def save_all_images(self, pair_dict: dict[str, cv2.typing.MatLike]) -> None:
        self.save_multiple_images(pair_dict=pair_dict)
        self.save_multiple_images_mlflow(pair_dict=pair_dict)
