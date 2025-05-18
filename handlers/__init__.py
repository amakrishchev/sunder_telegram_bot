from .start import register_start_handlers
from .guarantee import register_guarantee_handlers

# Храним состояния пользователей {user_id: state}
user_states = {}


def register_handlers(bot):
    register_start_handlers(bot)
    register_guarantee_handlers(bot, user_states)
