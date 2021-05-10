from aiogram import types

from loader import dp
from settings.strings import UNKNOWN_COMMAND_ANSWER


@dp.message_handler()
async def unknown_command(message: types.Message):
    if message.via_bot:
        return
    kb = message.reply_markup
    await message.answer(UNKNOWN_COMMAND_ANSWER, reply_markup=kb)
