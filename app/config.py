"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the prototype application."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="HR Agent Engine", alias="APP_NAME")
    database_url: str = Field(default="sqlite:///./hr_agent_engine.db", alias="DATABASE_URL")
    mock_llm: bool = Field(default=True, alias="MOCK_LLM")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    request_timeout_seconds: int = Field(default=5, alias="REQUEST_TIMEOUT_SECONDS")
    agent_retry_attempts: int = Field(default=1, alias="AGENT_RETRY_ATTEMPTS")
    stm_limit: int = Field(default=5, alias="STM_LIMIT")
    ltm_significance_threshold: float = Field(default=0.7, alias="LTM_SIGNIFICANCE_THRESHOLD")
    low_confidence_threshold: float = Field(default=0.6, alias="LOW_CONFIDENCE_THRESHOLD")
    audit_limit: int = Field(default=25, alias="AUDIT_LIMIT")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
