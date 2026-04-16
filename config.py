from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    bot_token: str
    database_url: str = "sqlite:///./data/spam_bot.db"
    spam_threshold: float = 0.95
    max_violations: int = 3
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
