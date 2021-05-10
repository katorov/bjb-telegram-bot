from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import start_kb
from loader import dp


@dp.message_handler(commands='cancel', state='*')
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отменено', reply_markup=start_kb)
