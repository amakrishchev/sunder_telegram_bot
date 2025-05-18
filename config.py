from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Токен бота из BotFather
    TELEGRAM_TOKEN: str

    # Настройки Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Настройки Google Sheets
    GOOGLE_SHEETS_CREDENTIALS: str = "path/to/credentials.json"
    SPREADSHEET_ID: str

    # API ключ для анализа чеков
    DEEPSEEK_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


def load_config() -> Settings:
    """Загружает конфигурацию из .env файла"""
    return Settings()
