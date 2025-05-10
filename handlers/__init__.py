from aiogram import Dispatcher
from .common import register_common_handlers
from .guarantee import register_guarantee_handlers
from .instructions import register_instructions_handlers
from .problems import register_problems_handlers
from .manager import register_manager_handlers


def register_handlers(dp: Dispatcher) -> None:
    """
    Регистрирует все обработчики для бота.
    Параметры:
        dp (Dispatcher): Диспетчер aiogram.
    """
    register_common_handlers(dp)
    register_guarantee_handlers(dp)
    register_instructions_handlers(dp)
    register_problems_handlers(dp)
    register_manager_handlers(dp)
