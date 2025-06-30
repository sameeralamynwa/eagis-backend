from functools import lru_cache
from pathlib import Path
from typing import Annotated
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    template_path: Path = Path(__file__).resolve().parent / "templates"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_config():
    return Config()


ConfigDependency = Annotated[Config, Depends()]
