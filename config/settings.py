"""
Settings configuration for financial analytics pipelines.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase Configuration
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    supabase_db_name: Optional[str] = Field(None, env="SUPABASE_DB_NAME")

    # Pipeline Configuration
    default_rsi_period: int = Field(default=14, env="DEFAULT_RSI_PERIOD")
    batch_size: int = Field(default=100, env="BATCH_SIZE")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
