import json
from typing import Any, Literal, Optional

import yaml
import pandas as pd
from pydantic import Field, BaseModel


class ImageModel(BaseModel):
    image_name: str = Field(
        ..., title="Image Name", description="The name of the image", frozen=True, deprecated=False
    )
    image_path: str = Field(
        ..., title="Image Path", description="The path to the image", frozen=True, deprecated=False
    )
    delay_after_click: int = Field(
        ...,
        title="Delay After Click",
        description="The delay after the click when the image is found",
        frozen=True,
        deprecated=False,
    )
    click_this: bool = Field(
        ...,
        title="Click This",
        description="Indicates whether to click the image or not",
        frozen=True,
        deprecated=False,
    )
    screenshot_option: bool = Field(
        ...,
        title="Screenshot Option",
        description="Indicates whether to take a screenshot or not",
        frozen=True,
        deprecated=False,
    )
    confidence: float = Field(
        ...,
        title="Confidence",
        description="The confidence level for image matching",
        frozen=True,
        deprecated=False,
    )
    vertical: Literal["top", "center", "bottom"] = Field(
        default="center",
        title="Vertical",
        description="The vertical alignment within the matched template",
        frozen=True,
        deprecated=False,
    )
    horizontal: Literal["left", "center", "right"] = Field(
        default="center",
        title="Horizontal",
        description="The horizontal alignment within the matched template",
        frozen=True,
        deprecated=False,
    )
    force_x: Optional[int] = Field(
        default=None,
        title="Force X",
        description="The x-coordinate of the force click",
        frozen=True,
        deprecated=True,
    )
    force_y: Optional[int] = Field(
        default=None,
        title="Force Y",
        description="The y-coordinate of the force click",
        frozen=True,
        deprecated=True,
    )

    def export_json(self, output: str) -> dict[str, Any]:
        if not output.endswith(".json"):
            raise ValueError("Output file must be a JSON file")
        data_dict = self.model_dump()
        with open(output, "w", encoding="utf-8") as file:
            json.dump(data_dict, file, indent=4, ensure_ascii=False)
        return data_dict

    def export_yaml(self, output: str) -> dict[str, Any]:
        if not output.endswith(".yaml"):
            raise ValueError("Output file must be a JSON file")
        data_dict = self.model_dump()
        with open(output, "w", encoding="utf-8") as yaml_file:
            yaml.dump(data_dict, yaml_file, allow_unicode=True)
        return data_dict

    def export_csv(self, output: str) -> pd.DataFrame:
        if not output.endswith(".csv"):
            raise ValueError("Output file must be a CSV file")
        data = pd.DataFrame([self.model_dump()]).astype(str)
        data.to_csv(output, index=False)
        return data


class ConfigModel(BaseModel):
    target: str = Field(
        ...,
        description="This field can be either a window title or a URL or cdp url.",
        frozen=True,
        deprecated=False,
    )
    save2db: bool = Field(
        ...,
        description="Indicates whether to save the results to the database or not.",
        frozen=True,
        deprecated=False,
    )
    auto_click: bool = Field(
        ...,
        description="Indicates whether auto click is enabled or not.",
        frozen=True,
        deprecated=False,
    )
    serials: list[str] = Field(
        default=["16384", "16416"], description="The serial number of the device."
    )
    random_interval: int = Field(
        ...,
        description="The interval between each click in seconds.",
        frozen=True,
        deprecated=False,
    )
    image_list: list[ImageModel] = Field(
        ...,
        description="The list of images to compare, it should contain path and name.",
        frozen=True,
        deprecated=False,
    )
    # switch_conditions: Optional[list[ImageModel]] = Field(
    #     default=None,
    #     description="The list of image to switch game in some conditions.",
    #     frozen=True,
    #     deprecated=False,
    # )
