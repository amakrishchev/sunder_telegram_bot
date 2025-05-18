import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


class Config:
    # Токен бота из @BotFather
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    # Доступ в БД
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        # 'dbname': os.getenv('DB')
    }

    # Настройки Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Google Sheets
    GSHEETS_CREDENTIALS = os.getenv("GSHEETS_CREDENTIALS", "path/to/credentials.json")
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

    # DeepSeek API
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


# Создаем экземпляр конфига
config = Config()
