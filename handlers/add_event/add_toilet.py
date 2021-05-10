import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from bjb_toolkit.datetime.datetime_parser import parse_datetime
from bjb_toolkit.datetime.timezone_utils import get_local_now
from db_api import ToiletRecord
from db_api import User
from handlers.states import ToiletStates
from keyboards.callback_datas import event_callback, toilet_callback, fast_datetime_callback
from keyboards.default import cancel_kb, start_kb
from keyboards.inline.fast_datetime_select import fast_datetime_kb
from keyboards.inline.toilet import toilet_kb
from loader import dp


@dp.callback_query_handler(event_callback.filter(name='Туалет'), state="select_event")
async def select_toilet_quantity(call: CallbackQuery, state: FSMContext):
    await ToiletStates.first()
    await state.update_data(user_id=call.from_user.id)
    await call.message.edit_text(call.message.html_text + '\n' + 'Туалет')

    answer = hbold('2. Выберите категорию (4-х бальная шкала)')
    await call.message.answer(answer, reply_markup=toilet_kb)


@dp.message_handler(state=ToiletStates.enter_toilet_quantity)
async def select_toilet_quantity_error(message: types.Message):
    answer = 'Для ввода категории воспользуйтесь клавиатурой под сообщением'
    await message.answer(answer)


@dp.callback_query_handler(toilet_callback.filter(), state=ToiletStates.enter_toilet_quantity)
async def select_toilet_dt(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(category=int(callback_data['cat']))
    await ToiletStates.enter_toilet_date.set()
    await call.message.edit_text(call.message.html_text + '\n' + f'Туалет: {callback_data["cat"]}')

    answer = hbold('3. Введите дату и время')
    await call.answer()
    await call.message.answer(answer, reply_markup=fast_datetime_kb)


@dp.callback_query_handler(fast_datetime_callback.filter(),
                           state=ToiletStates.enter_toilet_date)
async def fast_select_dt(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User):
    selected_btn = callback_data['minutes']
    await call.message.edit_text(
        call.message.html_text + '\n' + callback_data['title']
    )

    if selected_btn == '-1':
        await ToiletStates.enter_toilet_date_text.set()
        await call.answer()
        return

    selected_dt = get_local_now(user.timezone) - datetime.timedelta(minutes=int(selected_btn))
    await save(call.message, state, selected_dt, user)
    await call.answer()


@dp.message_handler(state=ToiletStates.enter_toilet_date)
async def fast_select_dt_error(message: types.Message):
    await message.answer('Для ввода даты и времени воспользуйтесь кнопками под сообщением',
                         reply_markup=cancel_kb)


@dp.message_handler(state=ToiletStates.enter_toilet_date_text)
async def save_record(message: types.Message, state: FSMContext, user: User):
    text = message.text
    parsed_dt = parse_datetime(text)
    if not parsed_dt:
        await message.answer(hbold('Дата и время введены некорректно, попробуйте еще раз'),
                             reply_markup=cancel_kb)
        return

    await save(message, state, parsed_dt, user)


async def save(message, state: FSMContext, dt, user):
    await state.update_data(dt=dt)
    toilet_data = await state.get_data()
    await state.finish()

    toilet_record = ToiletRecord(toilet_data['category'], toilet_data['dt'], token=user.token)
    await toilet_record.save()
    toilet_record_desc = toilet_record.format_output(user.timezone, with_date=True)
    await message.answer(hbold('Туалет успешно добавлен!\n\n👉 ') + toilet_record_desc,
                         reply_markup=start_kb)
