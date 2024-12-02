from typing import Union, Optional
from pathlib import Path

from PIL import Image
import numpy as np
from pydantic import Field, BaseModel, ConfigDict
from adbutils._device import AdbDevice
from playwright.sync_api import Page
from playwright.async_api import Page as APage


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
        default=None,
        description="The x-coordinate of the button center.",
        frozen=True,
        deprecated=False,
    )
    calibrated_x: Optional[int] = Field(
        default=None,
        description="The calibrated x-coordinate of the button center.",
        frozen=True,
        deprecated=False,
    )
    button_center_y: Optional[int] = Field(
        default=None,
        description="The y-coordinate of the button center.",
        frozen=True,
        deprecated=False,
    )
    calibrated_y: Optional[int] = Field(
        default=None,
        description="The calibrated y-coordinate of the button center.",
        frozen=True,
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
    color_screenshot: Optional[np.ndarray] = Field(
        default=None,
        description="The screenshot of the button in color.",
        frozen=True,
        deprecated=False,
    )
    blackout_screenshot: Optional[np.ndarray] = Field(
        default=None,
        description="The screenshot of the button with a blackout effect.",
        frozen=True,
        deprecated=False,
    )


class Screenshot(BaseModel):
    """Represents a screenshot captured from a device.

    Attributes:
        model_config (ConfigDict): The configuration dictionary for the model.
        screenshot (Union[bytes, Image.Image]): The screenshot image data.
        device (Union[AdbDevice, Page, APage, ShiftPosition]): The device from which the screenshot was captured.

    Methods:
        save: Save the screenshot to a specified path.
        calibrate: Adjust the button center coordinates based on the device
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    screenshot: Union[bytes, Image.Image]
    device: Union[AdbDevice, Page, APage, ShiftPosition]

    async def save(self, save_path: str) -> str:
        """Asynchronously saves the screenshot to the specified path.

        Args:
            save_path (str): The path where the screenshot will be saved. If the path does not end with ".png", it will be automatically appended.

        Returns:
            str: The full path where the screenshot was saved.
        """
        output_path = (
            Path(f"{save_path}.png") if not save_path.endswith(".png") else Path(save_path)
        )
        await self.__save_image(output_path=output_path)
        return output_path.absolute().as_posix()

    async def __save_image(self, output_path: Path) -> None:
        if isinstance(self.screenshot, bytes):
            output_path.write_bytes(self.screenshot)
        elif isinstance(self.screenshot, Image.Image):
            self.screenshot.save(output_path)
        else:
            raise TypeError("不支持的屏幕截图类型。")
