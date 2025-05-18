import os
import base64
import httpx
from pydantic import BaseModel, Field
from config import load_config
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ReceiptData(BaseModel):
    article: str = Field(..., alias="артикул")
    product_name: str = Field(..., alias="название товара")
    purchase_date: str = Field(..., alias="дата покупки")
    price: float = Field(..., alias="цена")


class ReceiptAnalyzer:
    def __init__(self):
        self.config = load_config()
        self.timeout = 30.0

    async def _make_api_request(self, base64_image: str) -> Optional[dict]:
        """Отправляет запрос к DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-vision",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Извлеки из чека: артикул (только цифры), название товара, дату покупки (дд.мм.гггг), цену. Верни JSON."
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

    async def analyze_receipt(self, image_path: str):
        """Анализирует чек и возвращает структурированные данные"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            response = await self._make_api_request(base64_image)
            if not response:
                return None

            content = response['choices'][0]['message']['content']
            return ReceiptData.model_validate_json(content)

        except Exception as e:
            logger.error(f"Receipt analysis error: {e}")
            return None


# Глобальный экземпляр для использования в хендлерах
receipt_analyzer = ReceiptAnalyzer()
