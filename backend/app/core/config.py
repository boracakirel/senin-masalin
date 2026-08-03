from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Senin Masalın API"
    app_version: str = "0.1.0"
    database_url: str = Field(
        default="mysql+pymysql://root@127.0.0.1:3306/senin_masalin",
        validation_alias="DATABASE_URL",
    )
    nvidia_api_key: str = Field(default="", validation_alias="NVIDIA_API_KEY")
    nvidia_api_url: str = Field(
        default="https://integrate.api.nvidia.com/v1/chat/completions",
        validation_alias="NVIDIA_API_URL",
    )
    nvidia_model: str = Field(
        default="meta/llama-3.3-70b-instruct",
        validation_alias="NVIDIA_MODEL",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
