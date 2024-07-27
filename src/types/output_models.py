from typing import Union

from PIL import Image
from pydantic import BaseModel, ConfigDict
from adbutils._device import AdbDevice
from playwright.sync_api import Page


class ShiftPosition(BaseModel):
    shift_x: int
    shift_y: int


class DeviceOutput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    screenshot: Union[bytes, Image.Image]
    device: Union[AdbDevice, Page, ShiftPosition]

    def save(self, save_path: str) -> str:
        save_path = f"{save_path}.png" if not save_path.endswith(".png") else save_path
        self.screenshot.save(save_path)
        return save_path
