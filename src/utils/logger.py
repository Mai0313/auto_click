from typing import Literal
from pathlib import Path

import cv2
import mlflow
from pydantic import BaseModel, computed_field


class Logger(BaseModel):
    original_image_path: str

    @computed_field
    @property
    def image_name(self) -> str:
        return Path(self.original_image_path).name

    def save(
        self, screenshot: cv2.typing.MatLike, image_type: Literal["color", "blackout"]
    ) -> None:
        log_dir = Path(f"./logs/{image_type}")
        log_dir.mkdir(exist_ok=True, parents=True)
        screenshot_path = Path(f"{log_dir.as_posix()}/{self.image_name}")
        if not screenshot_path.exists():
            cv2.imwrite(screenshot_path.absolute(), screenshot)

    def save_mlflow(
        self, screenshot: cv2.typing.MatLike, image_type: Literal["color", "blackout"]
    ) -> None:
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        mlflow.log_image(image=screenshot_rgb, artifact_file=f"{image_type}/{self.image_name}")
