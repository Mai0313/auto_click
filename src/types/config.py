from pydantic import Field, BaseModel

from .image_models import ImageModel


class ConfigModel(BaseModel):
    target: str = Field(
        ...,
        description="This field can be either a window title or a URL or cdp url.",
        frozen=True,
        deprecated=False,
    )
    save2db: bool = Field(
        ...,
        description="Indicates whether to save the results to the database or not.",
        frozen=True,
        deprecated=False,
    )
    auto_click: bool = Field(
        ...,
        description="Indicates whether auto click is enabled or not.",
        frozen=True,
        deprecated=False,
    )
    serials: list[str] = Field(
        default=["16384", "16416"], description="The serial number of the device."
    )
    random_interval: int = Field(
        ...,
        description="The interval between each click in seconds.",
        frozen=True,
        deprecated=False,
    )
    image_list: list[ImageModel] = Field(
        ...,
        description="The list of images to compare, it should contain path and name.",
        frozen=True,
        deprecated=False,
    )
    # switch_conditions: Optional[list[ImageModel]] = Field(
    #     default=None,
    #     description="The list of image to switch game in some conditions.",
    #     frozen=True,
    #     deprecated=False,
    # )
