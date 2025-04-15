from typing import Optional

from pydantic import Field, BaseModel, ConfigDict


class FoundPosition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    button_x: Optional[int] = Field(
        default=None,
        description="The x-coordinate of the button center.",
        frozen=False,
        deprecated=False,
    )
    button_y: Optional[int] = Field(
        default=None,
        description="The y-coordinate of the button center.",
        frozen=False,
        deprecated=False,
    )
    name_cn: str = Field(
        default="",
        description="The name of the found button in Chinese.",
        frozen=True,
        deprecated=False,
    )
    name_en: str = Field(
        default="",
        description="The name of the found button in English.",
        frozen=True,
        deprecated=False,
    )
