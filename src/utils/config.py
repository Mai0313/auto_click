from typing import Optional

from pydantic import Field, BaseModel


class ImageModel(BaseModel):
    image_name: str = Field(
        ...,
        title="Image Name",
        description="The name of the image from `./data`",
        frozen=True,
        deprecated=False,
    )
    image_path: str = Field(
        ...,
        title="Image Path",
        description="The path to the image from `./data`",
        frozen=True,
        deprecated=False,
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
    confidence: float = Field(
        ...,
        title="Confidence",
        description="The confidence level for image matching",
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
