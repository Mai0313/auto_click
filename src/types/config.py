from typing import Literal, Optional

from pydantic import Field, BaseModel


class ImageModel(BaseModel):
    image_name: str = Field(
        ..., title="Image Name", description="The name of the image", frozen=True, deprecated=False
    )
    image_path: str = Field(
        ..., title="Image Path", description="The path to the image", frozen=True, deprecated=False
    )
    delay_after_click: int = Field(
        ...,
        title="Delay After Click",
        description="The delay after the click when the image is found",
        frozen=True,
        deprecated=False,
    )
    click_this: bool = Field(
        ...,
        title="Click This",
        description="Indicates whether to click the image or not",
        frozen=True,
        deprecated=False,
    )
    screenshot_option: bool = Field(
        ...,
        title="Screenshot Option",
        description="Indicates whether to take a screenshot or not",
        frozen=True,
        deprecated=False,
    )
    confidence: float = Field(
        ...,
        title="Confidence",
        description="The confidence level for image matching",
        frozen=True,
        deprecated=False,
    )
    vertical: Literal["top", "center", "bottom"] = Field(
        default="center",
        title="Vertical",
        description="The vertical alignment within the matched template",
        frozen=True,
        deprecated=False,
    )
    horizontal: Literal["left", "center", "right"] = Field(
        default="center",
        title="Horizontal",
        description="The horizontal alignment within the matched template",
        frozen=True,
        deprecated=False,
    )
    force_x: Optional[int] = Field(
        default=None,
        title="Force X",
        description="The x-coordinate of the force click",
        frozen=True,
        deprecated=True,
    )
    force_y: Optional[int] = Field(
        default=None,
        title="Force Y",
        description="The y-coordinate of the force click",
        frozen=True,
        deprecated=True,
    )


class ConfigModel(BaseModel):
    target: str = Field(
        ...,
        description="This field can be either a window title or a URL or cdp url.",
        frozen=True,
        deprecated=False,
    )
    auto_click: bool = Field(
        ...,
        description="Indicates whether auto click is enabled or not.",
        frozen=True,
        deprecated=False,
    )
    serial: str = Field(
        default="127.0.0.1:16384",
        description="The serial number of the device.",
        examples=["127.0.0.1:16384", "127.0.0.1:16416"],
        frozen=True,
        deprecated=False,
    )
    image_list: list[ImageModel] = Field(
        ...,
        description="The list of images to compare, it should contain path and name.",
        frozen=True,
        deprecated=False,
    )
