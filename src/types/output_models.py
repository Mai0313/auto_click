from typing import Optional
from pathlib import Path

from PIL import Image
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
        button_x (Optional[int]): The x-coordinate of the button center.
        button_y (Optional[int]): The y-coordinate of the button center.
        found_button_name_en (Optional[str]): The name of the found button in English.
        found_button_name_cn (Optional[str]): The name of the found button in Chinese.
        color_screenshot (Optional[np.ndarray]): The screenshot of the button in color.
        blackout_screenshot (Optional[np.ndarray]): The screenshot of the button with a blackout effect.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    button_x: Optional[int] = Field(
        default=None,
        description="The x-coordinate of the button center.",
        frozen=False,
        deprecated=False,
    )
    button_y: Optional[int] = Field(
        default=None,
        description="The y-coordinate of the button center.",
        frozen=False,
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

    async def calibrate(self, shift_x: int, shift_y: int) -> None:
        """Adjusts the button center coordinates based on the device type.

        Args:
            shift_x (int): The amount to shift the button center along the x-axis.
            shift_y (int): The amount to shift the button center along the y-axis.
        """
        if self.button_x and self.button_y:
            self.button_x += shift_x
            self.button_y += shift_y


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
    screenshot: bytes | Image.Image
    device: AdbDevice | Page | APage | ShiftPosition

    async def save(self, save_path: str) -> str:
        """Asynchronously saves the screenshot to the specified path.

        Args:
            save_path (str): The path where the screenshot will be saved. If the path does not end with ".png", it will be automatically appended.

        Raises:
            TypeError: If the screenshot type is not supported.

        Returns:
            str: The full path where the screenshot was saved.
        """
        output_path = (
            Path(f"{save_path}.png") if not save_path.endswith(".png") else Path(save_path)
        )
        if isinstance(self.screenshot, bytes):
            output_path.write_bytes(self.screenshot)
        elif isinstance(self.screenshot, Image.Image):
            self.screenshot.save(output_path)
        else:
            raise TypeError("不支持的屏幕截图类型。")
        return output_path.absolute().as_posix()
