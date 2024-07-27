from typing import Union, Optional

from PIL import Image
from pydantic import Field, BaseModel
from adbutils._device import AdbDevice
from playwright.sync_api import Page
from src.types.output_models import ShiftPosition


class ImageModel(BaseModel):
    image_name: str = Field(...)
    image_path: str = Field(...)
    delay_after_click: int = Field(...)
    screenshot_option: bool = Field(...)
    confidence: float = Field(...)


class OutputImage(BaseModel):
    screenshot: Union[bytes, Image.Image]
    device: Union[AdbDevice, Page, ShiftPosition]

    def save(self, save_path: str) -> str:
        save_path = f"{save_path}.png" if not save_path.endswith(".png") else save_path
        self.screenshot.save(save_path)
        return save_path


class ConfigModel(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    auto_click: bool = Field(...)
    adb_port: int = Field(...)
    loops: int = Field(...)
    global_interval: int = Field(...)
    base_check_list: list[str] = Field(...)
    additional_check_list: list[Optional[str]] = Field(...)
    image_list: list[ImageModel] = Field(...)
