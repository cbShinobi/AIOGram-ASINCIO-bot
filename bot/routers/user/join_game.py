from aiogram import types

from ...bot import bot
from ...callback_data import JoinGameCallbackData
from ...services.database.models import BotUser, Game, GameMember
from . import router


@router.callback_query(JoinGameCallbackData.filter())
async def join_game_handler(query: types.CallbackQuery, bot_user: BotUser):
    data = JoinGameCallbackData.unpack(query.data)  # type: ignore
    game = await Game.filter(id=data.game_id).get()

    if await game.members.filter(bot_user=bot_user).exists():
        return await query.answer(
            bot.phrases.already_joined_game_message_text, show_alert=True
        )

    await GameMember.create(bot_user=bot_user, game=game)
    await query.answer(bot.phrases.joined_game_message_text.format(game=game))
