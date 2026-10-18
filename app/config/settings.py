from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from pydantic_core import MultiHostUrl
from functools import lru_cache
from pathlib import Path


CURRENT_PATH = Path(__file__).resolve().parent
BASE_DIR = CURRENT_PATH.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    gemini_api_key : SecretStr
    postgres_host : str
    postgres_port : int
    postgres_db : str
    postgres_user : str
    postgres_password : SecretStr

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return str(MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db
        ))

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()