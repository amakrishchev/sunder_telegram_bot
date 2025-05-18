import pdfkit
from jinja2 import Environment, FileSystemLoader


import os
import logging

logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("templates"))


def generate_guarantee_certificate(data: dict) -> str:
    """Генерирует PDF сертификат гарантии"""
    template = env.get_template("guarantee.html")
    html = template.render(data)

    os.makedirs("certificates", exist_ok=True)
    filename = f"certificates/guarantee_{data['order_id']}.pdf"

    pdfkit.from_string(html, filename)
    return filename
