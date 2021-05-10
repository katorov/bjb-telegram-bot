from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold

from keyboards.default import cancel_kb
from keyboards.inline.select_event import select_event_kb
from loader import dp
from settings.strings import INSTRUCTION_BEFORE_ADD_EVENT


@dp.message_handler(Text(equals='Добавить событие'), state='*')
async def select_event(message: types.Message, state: FSMContext):
    await state.set_state('select_event')
    await state.reset_data()
    await message.answer(INSTRUCTION_BEFORE_ADD_EVENT, reply_markup=cancel_kb)
    await message.answer(hbold('1. Выберите тип события'), reply_markup=select_event_kb)


@dp.message_handler(state='select_event')
async def select_event_error_msg(message: types.Message):
    answer = 'Для выбора события нужно нажать на кнопку'
    await message.answer(answer)
