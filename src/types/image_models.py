from pydantic import Field, BaseModel


class ImageModel(BaseModel):
    image_name: str = Field(
        ..., description="The name of the image", frozen=True, deprecated=False
    )
    image_path: str = Field(
        ..., description="The path to the image", frozen=True, deprecated=False
    )
    delay_after_click: int = Field(
        ...,
        description="The delay after the click when the image is found",
        frozen=True,
        deprecated=False,
    )
    click_this: bool = Field(
        ...,
        description="Indicates whether to click the image or not",
        frozen=True,
        deprecated=False,
    )
    screenshot_option: bool = Field(
        ...,
        description="Indicates whether to take a screenshot or not",
        frozen=True,
        deprecated=False,
    )
    confidence: float = Field(
        ..., description="The confidence level for image matching", frozen=True, deprecated=False
    )
