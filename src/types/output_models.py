from typing import Optional

from pydantic import Field, BaseModel, ConfigDict


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
