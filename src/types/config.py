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
    enable_click: bool = Field(
        ...,
        title="Click This",
        description="Indicates whether to click the image or not",
        frozen=True,
        deprecated=False,
    )
    enable_screenshot: bool = Field(
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


class ConfigModel(BaseModel):
    enable: bool = Field(
        ...,
        description="Indicates whether auto click is enabled or not.",
        frozen=True,
        deprecated=False,
    )
    target: str = Field(
        ...,
        description="This field can be either a window title or a URL or cdp url.",
        frozen=True,
        deprecated=False,
    )
    serials: list[str] = Field(
        default=["16384", "16416"], description="The serial number of the device."
    )
    image_list: list[ImageModel] = Field(
        ...,
        description="The list of images to compare, it should contain path and name.",
        frozen=True,
        deprecated=False,
    )
