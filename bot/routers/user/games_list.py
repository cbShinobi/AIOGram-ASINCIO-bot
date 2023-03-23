import datetime

from aiogram import F, types

from ... import markups
from ...bot import bot
from ...services.database.models import BotUser, Game
from . import router


async def send_game(bot_user: BotUser, game: Game):
    starts_at_fmt = datetime.datetime.strftime(game.starts_at, r"%d.%m.%Y %H:%M")
    members_fmt = " | ".join(m.bot_user.contacts for m in game.members)

    await bot.send_message(
        bot_user.id,
        bot.phrases.game_message_text_fmt.format(
            game=game,  members=members_fmt, starts_at=starts_at_fmt
        ),
        reply_markup=markups.create_join_game_markup(game),
    )


@router.message(F.text == bot.phrases.games_list_button_text)
async def games_list_message_handler(message: types.Message, bot_user: BotUser):
    now = datetime.datetime.now()

    games = (
        await Game.filter(starts_at__gt=now)
        .order_by("-starts_at")
        .prefetch_related("members", "members__bot_user")
        .all()
    )

    for game in games:
        await send_game(bot_user, game)
