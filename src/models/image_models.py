from pydantic import BaseModel


class Settings(BaseModel):
    image_name: str
    image_path: str
    image_click_delay: int
    screenshot_option: bool
    confidence: float
    scroll: int
