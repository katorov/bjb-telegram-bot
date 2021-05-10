from aiogram import types

from settings import strings
from keyboards.default import start_kb
from loader import dp


@dp.message_handler(commands='help', state='*')
async def help_msg(message: types.Message):
    await message.answer(strings.HELP, reply_markup=start_kb)
