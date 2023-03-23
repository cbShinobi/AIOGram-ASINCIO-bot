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

@CreateGameForm.field('starts_at')
async def starts_at_field(value: str, field: FormField, bot_user: BotUser) -> datetime.datetime:
    try:
        starts_at = datetime.datetime.fromisoformat(value)
        if starts_at <= datetime.datetime.now():
            raise ValueError()
        return starts_at
    except ValueError:
        await bot.send_message(
            bot_user.id,
            bot.phrases.enter_game_datetime,
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return Form.SKIP_FIELD

@CreateGameForm.submit()
async def create_game_form_submit(form: CreateGameForm, bot_user: BotUser):
    game = await Game.create(created_by=bot_user, **form.__dict__)
    await GameMember.create(game=game, bot_user=bot_user)
    await bot.send_message(
        bot_user.id,
        bot.phrases.game_created_message_text,
        reply_markup=markups.start_markup,
    )

@router.message(F.text == bot.phrases.create_game_button_text)
async def create_game_handler(message: types.Message, state: FSMContext):
    await CreateGameForm.start(router, state)
