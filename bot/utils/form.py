import datetime
import functools
import inspect
from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generator, Optional, Type, TypeVar

from aiogram import F, types
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey
from aiogram.utils.magic_filter import MagicFilter

# TODO: support for pattern enter message like
#       class SomeForm(Form, enter_message_pattern="Enter {field_name}")

# TODO: support for enter message callback

# TODO: support for any kind of filters (e. g. async, Filter subclass, etc...)

# TODO: try again message text
# TODO: .from_tortoise_model

TForm = TypeVar("TForm", bound="Form")
SubmitCallback = Optional[Callable[..., Any]]


class FormState(StatesGroup):
    waiting_field_value = State()


@dataclass(frozen=True)
class FormFieldInfo:
    enter_message_text: str
    error_message_text: Optional[str]
    filter: Optional[MagicFilter]


def FormField(
    *,
    enter_message_text: str,
    filter: Optional[MagicFilter] = None,
    error_message_text: Optional[str] = None,
) -> Any:
    return FormFieldInfo(
        enter_message_text=enter_message_text,
        error_message_text=error_message_text,
        filter=filter,
    )


@dataclass
class _FormFieldData:
    name: str
    type: Type
    info: FormFieldInfo


class Form(ABC):
    __field_generator_cache: Dict[
        StorageKey, Generator[_FormFieldData, None, None]
    ] = {}

    __default_filters = {
        str: F.text,
        int: F.text.func(int),
        float: F.text.func(float),
        datetime.date: F.text.func(
            lambda text: datetime.datetime.strptime(text, r"%d.%m.%Y").date()
        ),
        datetime.datetime: F.text.func(
            lambda text: datetime.datetime.strptime(text, r"%d.%m.%Y %H:%M")
        ),
        datetime.time: F.text.func(
            lambda text: datetime.datetime.strptime(text, r"%H:%M").time()
        ),
        types.PhotoSize: F.photo.func(lambda photo: photo[-1]),
        types.Document: F.document.func(lambda document: document),
    }

    __submit_callback: SubmitCallback = None

    @classmethod
    def submit(cls):
        def decorator(submit_callback: SubmitCallback):
            cls.__submit_callback = submit_callback

        return decorator

    @classmethod
    def __from_state_data(cls, state_data):
        form_object = cls()
        form_object.__dict__.update(state_data["values"])
        return form_object

    @classmethod
    def __create_current_field_generator(cls):
        for field_name, field_type in cls.__annotations__.items():
            field_info = getattr(cls, field_name)

            if not isinstance(field_info, FormFieldInfo):
                continue

            field_data = _FormFieldData(field_name, field_type, field_info)
            yield field_data

    @classmethod
    def __get_current_field_generator(cls, key: StorageKey):
        if generator := cls.__field_generator_cache.get(key):
            return generator

        generator = cls.__create_current_field_generator()
        cls.__field_generator_cache[key] = generator
        return generator

    @classmethod
    def __clear_field_generator_cache(cls, key: StorageKey):
        if key not in cls.__field_generator_cache:
            return False

        del cls.__field_generator_cache[key]
        return True

    @classmethod
    def __get_filter_from_type(cls, field_type: Type):
        field_filter = cls.__default_filters.get(field_type)

        if field_filter is None:
            raise ValueError("This field type is not supported yet")

        return field_filter

    @classmethod
    def __prepare_submit_callback(cls, *args, **kwargs):
        if cls.__submit_callback is None:
            raise TypeError("Submit callback should be set")

        arg_spec = inspect.getfullargspec(cls.__submit_callback)
        prepared_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in arg_spec.args or k in arg_spec.kwonlyargs
        }

        submit_callback_partial = functools.partial(
            cls.__submit_callback, *args, **prepared_kwargs
        )

        return submit_callback_partial

    @classmethod
    async def start(
        cls,
        router: Router,
        state_ctx: FSMContext,
    ):
        cls.__clear_field_generator_cache(state_ctx.key)
        field_generator = cls.__get_current_field_generator(state_ctx.key)
        first_field: _FormFieldData = next(field_generator)

        await state_ctx.set_state(FormState.waiting_field_value)
        await state_ctx.update_data(
            current_field=first_field, values={}, form_id=id(cls)
        )
        await state_ctx.bot.send_message(
            state_ctx.key.chat_id, first_field.info.enter_message_text
        )

        if getattr(cls, "__registered", False):
            return

        router.message.register(
            cls.__resolve_callback,
            FormState.waiting_field_value,
            cls.__current_field_filter,
        )

        cls.__registered = True

    @classmethod
    async def __resolve_callback(
        cls, message: types.Message, state: FSMContext, value: Any, **data
    ):
        state_data = await state.get_data()
        current_field: _FormFieldData = state_data["current_field"]
        state_data["values"][current_field.name] = value
        await state.set_data(state_data)

        current_field_generator = cls.__get_current_field_generator(state.key)

        try:
            next_field = next(current_field_generator)
            await state.update_data(current_field=next_field)
            await message.answer(next_field.info.enter_message_text)
        except StopIteration:
            state_data = await state.get_data()
            await state.clear()
            data["state"] = state
            form_object = cls.__from_state_data(state_data)
            cls.__clear_field_generator_cache(state.key)

            if cls.__submit_callback:
                prepared_submit_callback = cls.__prepare_submit_callback(
                    form_object, **data
                )

                await prepared_submit_callback()

    @classmethod
    async def __current_field_filter(cls, message: types.Message, state: FSMContext):
        state_data = await state.get_data()

        if state_data["form_id"] != id(cls):
            return

        current_field: _FormFieldData = state_data["current_field"]

        field_filter = current_field.info.filter or cls.__get_filter_from_type(
            current_field.type
        )

        filter_result = field_filter.resolve(message)

        if filter_result is None:
            if current_field.info.error_message_text:
                await message.answer(current_field.info.error_message_text)

            return False

        return {"value": filter_result}
