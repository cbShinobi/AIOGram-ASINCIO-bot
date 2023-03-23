from enum import IntEnum

from aiogram.filters.callback_data import CallbackData


class JoinGameCallbackData(CallbackData, prefix="join-game"):
    game_id: int

