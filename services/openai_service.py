import openai
import logging
from typing import Optional, Dict
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ReceiptData(BaseModel):
    article: str
    product_name: str
    purchase_date: str
    price: float


class OpenAIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    async def analyze_receipt(self, image_url: str) -> Optional[ReceiptData]:
        """
        Анализирует чек через OpenAI API
        Параметры:
            image_url (str): Ссылка на изображение чека
        Возвращает:
            Optional[ReceiptData]: Распознанные данные или None
        """
        try:
            prompt = """
            Проанализируй чек Ozon и извлеки:
            1. Артикул товара (число)
            2. Название товара
            3. Дату покупки (в формате ДД.ММ.ГГГГ)
            4. Цену товара

            Верни ответ в JSON формате.
            """

            response = await openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": image_url},
                        ],
                    }
                ],
                max_tokens=300,
            )

            result = response.choices[0].message.content
            return ReceiptData.parse_raw(result)
        except Exception as e:
            logger.error(f"Error analyzing receipt: {e}")
            return None
