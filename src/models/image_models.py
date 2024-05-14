from typing import Union

from pydantic import Field, BaseModel


class Settings(BaseModel):
    image_name: str
    image_path: str
    image_click_delay: int
    screenshot_option: bool
    confidence: float
    scroll: int


class ConfigModel(BaseModel):
    auto_click: bool = Field(...)
    base_check_list: list[str] = Field(...)
    additional_check_list: list[Union[str, None]] = Field(...)
    image_list: list[Settings] = Field(...)
