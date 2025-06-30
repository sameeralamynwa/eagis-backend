from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Annotated
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEV = "dev"
    PROD = "prod"


class FileStorage(str, Enum):
    LOCAL = "local"
    S3 = "S3"


class Config(BaseSettings):
    # from env file
    app_env: AppEnv
    app_name: str
    app_url: str
    db_connection: str
    db_connection_sync: str
    jwt_secrete: str
    access_token_expire_minutes: int
    css_version: str = "1.0"
    file_storage: FileStorage = FileStorage.LOCAL
    local_storage_path: str = "uploads"
    allowed_images: list[str] = []
    max_image_size_bytes: int = 1000 * 1000 * 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # custom
    root_path: Path = Path(__file__).resolve().parent.parent
    static_path: Path = Path(__file__).resolve().parent.parent / "static"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def app_in_dev(self):
        return self.app_env == AppEnv.DEV

    @property
    def app_in_prod(self):
        return self.app_env == AppEnv.PROD


@lru_cache
def get_config():
    return Config()  # type: ignore


ConfigDepedency = Annotated[Config, Depends(get_config)]
