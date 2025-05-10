import pdfkit
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    def __init__(self, templates_dir: str = "templates"):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )

    def generate_guarantee_certificate(self, data: Dict) -> str:
        """
        Генерирует PDF сертификат гарантии
        Параметры:
            data (Dict): Данные для сертификата
        Возвращает:
            str: Путь к файлу PDF
        """
        try:
            template = self.env.get_template("guarantee.html")
            html = template.render(data)

            output_path = f"temp/guarantee_{data['order_id']}.pdf"
            pdfkit.from_string(html, output_path)

            return output_path
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
