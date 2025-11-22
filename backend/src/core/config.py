from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # AI Provider
    ai_provider: Literal["openai", "gigachat", "yandex"] = "openai"
    openai_api_key: str = ""
    gigachat_credentials: str = ""
    yandex_api_key: str = ""
    
    # KFU Integration
    kfu_api_url: str = "https://api.kpfu.ru/v1"
    kfu_api_key: str = ""
    kfu_webhook_secret: str = ""
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
