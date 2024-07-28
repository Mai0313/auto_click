from typing import Optional

from pydantic import Field, BaseModel

from src.types.image_models import ImageModel


class ConfigModel(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    auto_click: bool = Field(...)
    adb_port: int = Field(...)
    loops: int = Field(...)
    global_interval: int = Field(...)
    base_check_list: list[str] = Field(...)
    additional_check_list: list[Optional[str]] = Field(...)
    image_list: list[ImageModel] = Field(...)
