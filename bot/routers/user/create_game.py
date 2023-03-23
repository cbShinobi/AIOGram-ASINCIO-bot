import datetime

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from ... import markups
from ...bot import bot
from ...services.database.models import BotUser, Game, GameMember
from ...utils.form import Form, FormField
from . import router


class CreateGameForm(Form):
    starts_at: datetime.datetime = FormField(
        enter_message_text=bot.phrases.enter_game_datetime,
    )
    name: str = FormField(enter_message_text=bot.phrases.enter_game_name)
    description: str = FormField(enter_message_text=bot.phrases.enter_game_description)
    seats: int = FormField(enter_message_text=bot.phrases.enter_game_seats)
    location: str = FormField(enter_message_text=bot.phrases.enter_game_location)


@CreateGameForm.submit()
async def create_game_form_submit(form: CreateGameForm, bot_user: BotUser, state: FSMContext):
    starts_at = form.starts_at
    if starts_at and starts_at < datetime.datetime.now():
        await bot.send_message(bot_user.id, bot.phrases.invalid_datetime_error)
        await CreateGameForm.start(router, state)
        return

    try:
        game = await Game.create(created_by=bot_user, **form.__dict__)
    except ValueError:
        await bot.send_message(bot_user.id, bot.phrases.invalid_datetime_error)
        await CreateGameForm.start(router, state)
        return

    await GameMember.create(game=game, bot_user=bot_user)
    await bot.send_message(
        bot_user.id,

        bot.phrases.game_created_message_text.format(
            name=game.name,
            starts_at=game.starts_at.strftime('%d.%m.%Y %H:%M'),
            description=game.description,
            seats=game.seats,
            location=game.location
        ),
        reply_markup=markups.start_markup,
    )


@router.message(F.text == bot.phrases.create_game_button_text)
async def create_game_handler(message: types.Message, state: FSMContext):
    await CreateGameForm.start(router, state)
