import yaml
from pydantic import Field, BaseModel, model_validator


class Settings(BaseModel):
    image_name: str
    image_path: str
    image_click_delay: int
    screenshot_option: bool
