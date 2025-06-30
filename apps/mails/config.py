from enum import Enum
from functools import lru_cache
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MailAdapters(str, Enum):
    DEV = "dev_mail"
    FASTMAIL = "fast_mail"


class Config(BaseSettings):
    template_path: Path = Path(__file__).resolve().parent / "templates"
    mail_adapter: MailAdapters
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: SecretStr

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_config():
    return Config()
