"""Application configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        ...,
        description="PostgreSQL connection string",
    )

    bot_service_host: str = Field(
        default="0.0.0.0",
        description="Host to bind the service to",
    )
    bot_service_port: int = Field(
        default=8000,
        description="Port to bind the service to",
    )

    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for GPT models",
    )
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for Claude models",
    )
    llm_model: str = Field(
        default="gpt-4",
        description="LLM model to use (gpt-4, gpt-3.5-turbo, claude-3-sonnet-20240229, etc.)",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )

    def get_llm_provider(self) -> Literal["openai", "anthropic"]:
        """Determine which LLM provider to use based on model name."""
        if "gpt" in self.llm_model.lower():
            return "openai"
        elif "claude" in self.llm_model.lower():
            return "anthropic"
        else:
            return "openai"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
