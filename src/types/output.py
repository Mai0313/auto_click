from pydantic import Field, BaseModel, ConfigDict


class FoundPosition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    button_x: int = Field(
        ..., description="The x-coordinate of the button center.", frozen=False, deprecated=False
    )
    button_y: int = Field(
        ..., description="The y-coordinate of the button center.", frozen=False, deprecated=False
    )
    name_cn: str = Field(
        ..., description="The name of the found button in Chinese.", frozen=True, deprecated=False
    )
    name_en: str = Field(
        ..., description="The name of the found button in English.", frozen=True, deprecated=False
    )
