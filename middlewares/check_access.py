from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from db_api.utils import is_user_with_access
from settings.strings import ACCESS_DENIED


class IsPrivateChat(BaseMiddleware):

    async def on_process_message(self, message: types.Message, data: dict):
        is_private = bool(message.chat.type == types.ChatType.PRIVATE)
        if not is_private:
            CancelHandler()


class IsUserHaveAccess(BaseMiddleware):

    async def on_process_message(self, message: types.Message, data: dict):
        current_command = getattr(data.get('command'), 'command', None)
        if current_command in ('start', 'payment'):
            return

        access = await is_user_with_access(data['user'])
        if not access:
            await access_denied(message)


async def access_denied(message: types.Message):
    await message.answer(ACCESS_DENIED)
    raise CancelHandler()
