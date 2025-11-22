import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field
from typing import Literal, Optional

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

WORKER_LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d][%(processName)s] %(module)16s:%(lineno)-3d %(levelname)-7s - %(message)s"


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT
    date_format: str = "%Y-%m-%d %H:%M:%S"

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]
    


class AIConfig(BaseModel):
    openai_api_key: Optional[str] = Field(None, description="OpenAI API ключ")
    gigachat_credentials: Optional[str] = Field(None, description="GigaChat credentials")
    ai_provider: str = Field("openai", description="AI провайдер: openai или gigachat")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    
    # AI настройки
    openai_api_key: Optional[str] = None
    gigachat_credentials: Optional[str] = None
    ai_provider: str = "openai"
    
    # Общие настройки
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    logging: LoggingConfig = LoggingConfig()
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
