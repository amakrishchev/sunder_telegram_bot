import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import load_config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
config = load_config()


class GoogleSheetsClient:
    def __init__(self):
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            config.GOOGLE_SHEETS_CREDENTIALS, scope)
        self.client = gspread.authorize(creds)
        self.sheet = None

    async def connect(self, sheet_name: str):
        """Подключается к указанному листу"""
        try:
            spreadsheet = self.client.open_by_key(config.SPREADSHEET_ID)
            self.sheet = spreadsheet.worksheet(sheet_name)
            return True
        except Exception as e:
            logger.error(f"Google Sheets connection error: {e}")
            return False

    async def add_guarantee_request(self, data: dict) -> bool:
        """Добавляет запрос на гарантию в таблицу"""
        try:
            if not self.sheet:
                await self.connect("Гарантии")

            row = [
                data["name"],
                data["phone"],
                data["product_link"],
                data["article"],
                data["product_name"],
                data["purchase_date"],
                data["warranty_end"],
                data["promo_code"],
                data["status"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            self.sheet.append_row(row)
            return True
        except Exception as e:
            logger.error(f"Failed to add guarantee request: {e}")
            return False
