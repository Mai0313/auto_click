from pydantic import Field, BaseModel

from src.types.image_models import ImageModel


class ConfigModel(BaseModel):
    """Represents the configuration model for auto click functionality.

    Attributes:
        target (str): The target of the auto click, which can be either a window title, a URL, or a CDP URL.
        auto_click (bool): Indicates whether auto click is enabled or not.
        random_interval (int): The random interval between auto clicks.
        image_list (list[ImageModel]): The list of image models to be used for auto click matching.
    """

    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    auto_click: bool = Field(...)
    random_interval: int = Field(...)
    image_list: list[ImageModel] = Field(...)
