from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from db_api.utils import get_or_create_user


class GetDBUser(BaseMiddleware):

    async def on_process_message(self, message: types.Message, data: dict):
        data["user"] = await get_or_create_user(message.from_user)

    async def on_process_callback_query(self, cq: types.CallbackQuery, data: dict):
        data["user"] = await get_or_create_user(cq.from_user)

    async def on_process_inline_query(self, iq: types.InlineQuery, data: dict):
        data["user"] = await get_or_create_user(iq.from_user)
