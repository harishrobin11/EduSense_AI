"""Application configuration using Pydantic Settings."""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "EduSense AI"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "edusense_dev_secret_key_change_in_production_32bytes"

    # API Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./edusense.db"

    # LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    @property
    def is_sqlite(self) -> bool:
        """Check if current database is SQLite."""
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
