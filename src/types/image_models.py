from pydantic import Field, BaseModel


class ImageModel(BaseModel):
    """Represents an image model.

    Attributes:
        image_name (str): The name of the image.
        image_path (str): The path to the image.
        delay_after_click (int): The delay after the click when the image is found.
        click_this (bool): Indicates whether to click the image or not.
        screenshot_option (bool): Indicates whether to take a screenshot or not.
        confidence (float): The confidence level for image matching.
    """

    image_name: str = Field(..., description="The name of the image")
    image_path: str = Field(..., description="The path to the image")
    delay_after_click: int = Field(
        ..., description="The delay after the click when the image is found"
    )
    click_this: bool = Field(..., description="Indicates whether to click the image or not")
    screenshot_option: bool = Field(
        ..., description="Indicates whether to take a screenshot or not"
    )
    confidence: float = Field(..., description="The confidence level for image matching")
