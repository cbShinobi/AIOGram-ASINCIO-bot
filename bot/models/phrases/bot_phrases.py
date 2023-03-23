from pydantic import Field

from ..config_model import ConfigModel
from .admin import AdminPhrases


class BotPhrases(ConfigModel):
    __filenames__ = ("phrases.json",)

    admin: AdminPhrases = Field(AdminPhrases())  # type: ignore

    bot_started: str = Field("Бот {me.username} успешно запущен")
    start_message: str = Field("Используйте кнопки в меню ниже")
    create_game_button_text: str = Field("Создать игру")
    enter_game_name: str = Field("Введите название игры")
    enter_game_description: str = Field("Введите описание игры")
    enter_game_datetime: str = Field("Введите дату игры в формате ДД.ММ.ГГГГ чч:мм")
    enter_game_location: str = Field("Введите место проведения игры")
    enter_game_seats: str = Field("Введите количество мест(всего)")
    game_created_message_text: str = Field(
        "Игра создана!\n\n"
        "{name}\n\n"
        "Описание: {description}\n\n"
        "Место проведения: {location}\n\n"
        "Начинается: {starts_at}\n\n"
        "Количество мест:{seats}\n\n"
        "Участники: {members}")
    games_list_button_text: str = Field("Список игр")
    mygames_list_button_text: str = Field("Мои игры")
    game_message_text_fmt: str = Field("{game.name}\n\nОписание: {game.description}\n\nМесто проведения: {game.location}\n\nНачинается: {starts_at}\n\nКоличество мест:{game.seats}\n\nУчастники: {members}")
    invalid_datetime_error: str = Field("Невозможно создать игру ранее сегодняшней даты")
    join_game_button_text: str = Field("Участвовать")
    already_joined_game_message_text: str = Field("Вы уже участвуете в этой игре")
    joined_game_message_text: str = Field("Вы записались на игру {game.name}")
