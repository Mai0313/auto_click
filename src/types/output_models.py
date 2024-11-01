from typing import Union, Optional
import asyncio
from pathlib import Path

from PIL import Image
import numpy as np
from pydantic import Field, BaseModel, ConfigDict
from adbutils._device import AdbDevice
from playwright.sync_api import Page


class ShiftPosition(BaseModel):
    """Represents a shift in position.

    Attributes:
        shift_x (int): The amount to shift in the x-axis.
        shift_y (int): The amount to shift in the y-axis.
    """

    shift_x: int
    shift_y: int


class FoundPosition(BaseModel):
    """Represents the position of a found button on the screen.

    Attributes:
        button_center_x (Optional[int]): The x-coordinate of the button center.
        button_center_y (Optional[int]): The y-coordinate of the button center.
        color_screenshot (cv2.typing.MatLike): The screenshot of the button in color.
        blackout_screenshot (cv2.typing.MatLike): The screenshot of the button with blackout effect.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    button_center_x: Optional[int] = Field(
        default=None, description="The x-coordinate of the button center."
    )
    button_center_y: Optional[int] = Field(
        default=None, description="The y-coordinate of the button center."
    )
    color_screenshot: np.ndarray
    blackout_screenshot: np.ndarray


class Screenshot(BaseModel):
    """Represents a screenshot captured from a device.

    Attributes:
        model_config (ConfigDict): The configuration dictionary for the model.
        screenshot (Union[bytes, Image.Image]): The screenshot image data.
        device (Union[AdbDevice, Page, ShiftPosition]): The device from which the screenshot was captured.

    Methods:
        save: Save the screenshot to a specified path.
        calibrate: Adjust the button center coordinates based on the device
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    screenshot: Union[bytes, Image.Image]
    device: Union[AdbDevice, Page, ShiftPosition]

    def save(self, save_path: str) -> str:
        """Saves the screenshot to the specified path.

        Args:
            save_path (str): The path where the screenshot will be saved. If the path does not end with ".png", it will be appended automatically.

        Returns:
            str: The full path where the screenshot was saved.

        Raises:
            TypeError: If the screenshot is not of a supported type (bytes or PIL Image).
        """
        save_path = f"{save_path}.png" if not save_path.endswith(".png") else save_path
        save_path_obj = Path(save_path)

        if isinstance(self.screenshot, bytes):
            self._save_bytes(self.screenshot, save_path_obj)
        elif isinstance(self.screenshot, Image.Image):
            self._save_image(self.screenshot, save_path_obj)
        else:
            raise TypeError("不支持的屏幕截图类型。")
        return str(save_path_obj)

    async def a_save(self, save_path: str) -> str:
        """Asynchronously saves the screenshot to the specified path.

        Args:
            save_path (str): The path where the screenshot will be saved. If the path does not end with ".png", it will be automatically appended.

        Returns:
            str: The full path where the screenshot was saved.

        Raises:
            TypeError: If the screenshot type is not supported.
        """
        save_path = f"{save_path}.png" if not save_path.endswith(".png") else save_path
        save_path_obj = Path(save_path)

        if isinstance(self.screenshot, bytes):
            await asyncio.to_thread(self._save_bytes, self.screenshot, save_path_obj)
        elif isinstance(self.screenshot, Image.Image):
            await asyncio.to_thread(self._save_image, self.screenshot, save_path_obj)
        else:
            raise TypeError("不支持的屏幕截图类型。")
        return str(save_path_obj)

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

    @staticmethod
    def _save_bytes(data: bytes, path: Path) -> None:
        with open(path, "wb") as f:
            f.write(data)

    @staticmethod
    def _save_image(image: Image.Image, path: Path) -> None:
        image.save(path)
