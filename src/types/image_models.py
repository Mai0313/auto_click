from pydantic import Field, BaseModel


class ImageModel(BaseModel):
    image_name: str = Field(...)
    image_path: str = Field(...)
    delay_after_click: int = Field(...)
    click_this: bool = Field(...)
    screenshot_option: bool = Field(...)
    confidence: float = Field(...)
