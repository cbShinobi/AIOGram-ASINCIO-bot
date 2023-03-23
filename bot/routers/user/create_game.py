import datetime

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from ... import markups
from ...bot import bot
from ...services.database.models import BotUser, Game, GameMember
from ...utils.form import Form, FormField
from . import router


class CreateGameForm(Form):
    name: str = FormField(enter_message_text=bot.phrases.enter_game_name)
    description: str = FormField(enter_message_text=bot.phrases.enter_game_description)
    # location: str = FormField(enter_message_text=bot.phrases.enter_game_location)
    starts_at: datetime.datetime = FormField(
        enter_message_text=bot.phrases.enter_game_datetime
    )


@CreateGameForm.submit()
async def create_game_form_submit(form: CreateGameForm, bot_user: BotUser):
     try:
        if form.starts_at <= datetime.datetime.now():
            # Введенное значение времени меньше или равно текущему времени.
            # Запись не разрешена.
            raise ValueError(game_created_message_error_text)
        game = await Game.create(created_by=bot_user, **form.__dict__)
        await GameMember.create(game=game, bot_user=bot_user)
        await bot.send_message(
            bot_user.id,
            bot.phrases.game_created_message_text,
            reply_markup=markups.start_markup,
        )
    except ValueError:
        # Invalid time input, ask the user to enter the time again
        await bot.send_message(
            bot_user.id,
            bot.phrases.enter_game_datetime,
            reply_markup=types.ReplyKeyboardRemove(),
        )

@router.message(F.text == bot.phrases.create_game_button_text)
async def create_game_handler(message: types.Message, state: FSMContext):
    await CreateGameForm.start(router, state)
