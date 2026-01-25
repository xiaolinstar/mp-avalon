from __future__ import annotations

import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Env
    APP_ENV: str = Field(default="dev", description="dev, test, prod")

    # Flask
    # In production, SECRET_KEY should be handled securely and not use the default
    SECRET_KEY: SecretStr = Field(default="dev-key")
    FLASK_DEBUG: bool = True

    # WeChat
    # These are mandatory in non-test environments.
    # Using Optional here but logic in __init__ can enforce presence if not in test.
    WECHAT_TOKEN: SecretStr = Field(default="")
    WECHAT_APPID: str = Field(default="")
    WECHAT_AES_KEY: SecretStr = Field(default="")

    # Database
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost/avalon_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "TEXT"  # TEXT or JSON
    LOG_FILE: str | None = None
    SENTRY_DSN: str | None = None

    model_config = SettingsConfigDict(
        # Load .env first, then environment variables will override
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, **values):
        super().__init__(**values)

        # 1. Handle test environment database
        if self.APP_ENV == "test" and "DATABASE_URL" not in os.environ:
            self.DATABASE_URL = "sqlite:///:memory:"

        # 2. Fail-Fast for production environment
        if self.APP_ENV == "prod":
            self.validate_production_settings()

    def validate_production_settings(self):
        """Ensure critical settings are provided in production."""
        if self.SECRET_KEY.get_secret_value() == "dev-key":
            raise ValueError("SECRET_KEY must be changed in production!")

        if not self.WECHAT_APPID or not self.WECHAT_TOKEN.get_secret_value():
            raise ValueError("WeChat configuration is mandatory in production!")


settings = Settings()
