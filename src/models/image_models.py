from typing import Union

from pydantic import Field, BaseModel


class Settings(BaseModel):
    image_name: str
    image_path: str
    delay_after_click: int
    screenshot_option: bool
    confidence: float


class ConfigModel(BaseModel):
    auto_click: bool = Field(...)
    loops: int = Field(...)
    global_interval: int = Field(...)
    base_check_list: list[str] = Field(...)
    additional_check_list: list[Union[str, None]] = Field(...)
    image_list: list[Settings] = Field(...)
