from pydantic import Field, BaseModel

from src.types.image_models import ImageModel


class ConfigModel(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    auto_click: bool = Field(...)
    adb_ports: list[int] = Field(...)
    loops: int = Field(...)
    global_interval: int = Field(...)
    base_check_list: list[str] = Field(...)
    additional_check_list: list[str | None] = Field(...)
    image_list: list[ImageModel] = Field(...)
