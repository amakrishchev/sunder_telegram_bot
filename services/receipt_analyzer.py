import requests
import logging
from typing import Optional, Dict
from pydantic import BaseModel
import base64
import httpx

logger = logging.getLogger(__name__)

class ReceiptData(BaseModel):
    article: str
    product_name: str
    purchase_date: str
    price: float

class DeepSeekAnalyzer:
    def __init__(self, api_key: str, api_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _encode_image(self, image_path: str) -> str:
        """Кодирует изображение в base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def analyze_receipt(self, image_path: str) -> Optional[ReceiptData]:
        """
        Анализирует чек через DeepSeek API
        Параметры:
            image_path (str): Путь к изображению чека
        Возвращает:
            Optional[ReceiptData]: Распознанные данные или None
        """
        try:
            # Кодируем изображение
            base64_image = await self._encode_image(image_path)

            # Формируем промпт
            prompt = """
            Проанализируй изображение чека Ozon и извлеки следующую информацию:
            1. Артикул товара (только цифры)
            2. Полное название товара
            3. Дату покупки в формате ДД.ММ.ГГГГ
            4. Цену товара (только число)

            Верни ответ в формате JSON со следующими полями:
            {
                "article": "артикул",
                "product_name": "название товара",
                "purchase_date": "дата покупки",
                "price": цена
            }
            """

            # Формируем тело запроса
            payload = {
                "model": "deepseek-vision",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }

            # Отправляем запрос
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    return ReceiptData.parse_raw(content)
                else:
                    logger.error(f"DeepSeek API error: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error analyzing receipt with DeepSeek: {e}")
            return None
