from pydantic import Field, BaseModel, model_validator


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


class DeviceModel(BaseModel):
    target: str = Field(
        ...,
        title="The Application Name",
        description="This field can be either a window title or a URL or cdp url.",
        frozen=True,
        deprecated=False,
    )
    host: str = Field(
        ...,
        title="The ADB host",
        description="The host address of the device.",
        frozen=True,
        deprecated=False,
    )
    serial: str = Field(
        ...,
        title="The ADB serial",
        description="The serial number of the device.",
        frozen=True,
        deprecated=False,
    )

    @model_validator(mode="after")
    def _setup(self) -> "DeviceModel":
        if self.host and not self.serial:
            raise ValueError("Serial number is required when host is provided.")
        if not self.host and self.serial:
            raise ValueError("Host is required when serial number is provided.")
        return self


class ConfigModel(DeviceModel):
    enable: bool = Field(
        ...,
        title="Enable Auto Click",
        description="Indicates whether auto click is enabled or not.",
        frozen=True,
        deprecated=False,
    )
    image_list: list[ImageModel] = Field(
        ...,
        description="The list of images to compare, it should contain path and name.",
        frozen=True,
        deprecated=False,
    )
