from aiogram import types
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from .bot import bot
from .callback_data import JoinGameCallbackData
from .services.database.models import Game

remove_markup = types.ReplyKeyboardRemove(remove_keyboard=True)

start_markup = (
    ReplyKeyboardBuilder()
    .button(text=bot.phrases.create_game_button_text)
    .button(text=bot.phrases.games_list_button_text)
    .button(text=bot.phrases.mygames_list_button_text)
    .adjust(2, repeat=True)
    .as_markup(resize_keyboard=True)
)


def create_join_game_markup(game: Game):
    return (
        InlineKeyboardBuilder()
        .button(
            text=bot.phrases.join_game_button_text,
            callback_data=JoinGameCallbackData(game_id=game.id),
        )
        .as_markup()
    )
