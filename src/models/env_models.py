from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    adb_port: int = Field(..., alias="ADB_PORT")


if __name__ == "__main__":
    settings = EnvironmentSettings()
