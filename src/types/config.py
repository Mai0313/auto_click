from pydantic import Field, BaseModel

from src.types.image_models import ImageModel


class ConfigModel(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    auto_click: bool = Field(...)
    random_interval: int = Field(...)
    image_list: list[ImageModel] = Field(...)
