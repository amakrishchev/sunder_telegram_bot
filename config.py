from pydantic import BaseSettings


class Settings(BaseSettings):
    telegram_token: str
    google_sheets_credentials: str
    openai_api_key: str

    class Config:
        env_file = ".env"


def load_config():
    return Settings()
