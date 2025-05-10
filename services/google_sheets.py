import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel
from typing import List, Dict  # , Optional
import logging

# Настройка логгера
logger = logging.getLogger(__name__)


class ProductData(BaseModel):
    article: str
    name: str
    category: str
    manual_link: str
    image_link: str
    ozon_link: str
    promo_code: str


class ClientData(BaseModel):
    name: str
    phone: str
    product_link: str
    article: str
    product_name: str
    purchase_date: str
    warranty_end: str
    promo_code: str
    status: str = "new"


class GoogleSheetsService:
    def __init__(self, credentials_path: str):
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        self.client = gspread.authorize(creds)

    def _get_sheet(self, spreadsheet_id: str, sheet_name: str):
        """Получает лист таблицы по ID и названию"""
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            return spreadsheet.worksheet(sheet_name)
        except Exception as e:
            logger.error(f"Error accessing sheet: {e}")
            raise

    async def get_product_categories(self) -> List[str]:
        """
        Получает список уникальных категорий товаров
        Возвращает:
            List[str]: Список категорий
        """
        sheet = self._get_sheet("SPREADSHEET_ID", "Products")
        records = sheet.get_all_records()
        return list(set([item['category'] for item in records]))

    async def get_products_by_category(self, category: str) -> List[ProductData]:
        """
        Получает товары по категории
        Параметры:
            category (str): Название категории
        Возвращает:
            List[ProductData]: Список товаров
        """
        sheet = self._get_sheet("SPREADSHEET_ID", "Products")
        records = sheet.get_all_records()
        return [ProductData(**item) for item in records if item['category'] == category]

    async def add_guarantee_request(self, data: ClientData) -> bool:
        """
        Добавляет запрос на гарантию в таблицу
        Параметры:
            data (ClientData): Данные клиента
        Возвращает:
            bool: Успешность операции
        """
        try:
            sheet = self._get_sheet("SPREADSHEET_ID", "Clients")
            sheet.append_row(list(data.dict().values()))
            return True
        except Exception as e:
            logger.error(f"Error adding guarantee request: {e}")
            return False

    async def add_problem_request(self, data: Dict) -> bool:
        """Аналогично add_guarantee_request для проблем"""
        pass
