from typing import Union

from PIL import Image
from pydantic import BaseModel, ConfigDict
from adbutils._device import AdbDevice
from playwright.sync_api import Page


class ShiftPosition(BaseModel):
    shift_x: int
    shift_y: int


class Screenshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    screenshot: Union[bytes, Image.Image]
    device: Union[AdbDevice, Page, ShiftPosition]

    def save(self, save_path: str) -> str:
        save_path = f"{save_path}.png" if not save_path.endswith(".png") else save_path
        if isinstance(self.screenshot, bytes):
            with open(save_path, "wb") as f:
                f.write(self.screenshot)
        elif isinstance(self.screenshot, Image.Image):
            self.screenshot.save(save_path)
        return save_path

    def calibrate(self, button_center_x: int, button_center_y: int) -> tuple[int, int]:
        # if the device is from a window process, we need to add shift_x, shift_y to the button_center_x, button_center_y
        # since we do not know the exact position of the window.
        if isinstance(self.device, Page):
            pass  # place holder for future implementation
        if isinstance(self.device, AdbDevice):
            pass  # place holder for future implementation
        if isinstance(self.device, ShiftPosition):
            button_center_x = button_center_x + self.device.shift_x
            button_center_y = button_center_y + self.device.shift_y
        return button_center_x, button_center_y
