import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from bjb_toolkit.datetime.datetime_parser import parse_datetime, hh_mm_printer
from bjb_toolkit.datetime.timezone_utils import naive_to_local, get_local_now
from db_api import User
from db_api import WalkRecord
from handlers.states import WalkStates
from keyboards.callback_datas import event_callback, quantity_callback, fast_datetime_callback
from keyboards.default import cancel_kb, start_kb
from keyboards.inline.fast_datetime_select import fast_datetime_kb
from keyboards.inline.quantity import QuantityKb
from loader import dp


@dp.callback_query_handler(event_callback.filter(name='Прогулка'), state="select_event")
async def select_walk_quantity(call: CallbackQuery, state: FSMContext):
    await WalkStates.first()
    await state.update_data(user_id=call.from_user.id)
    await call.message.edit_text(call.message.html_text + '\n' + 'Прогулка')

    answer = hbold('2. Укажите длительность в минутах')
    kb, _, _ = QuantityKb.get()
    await call.message.answer(answer, reply_markup=kb)


@dp.message_handler(state=WalkStates.enter_walk_quantity)
async def select_walk_quantity_error(message: types.Message):
    answer = 'Для ввода длительности воспользуйтесь клавиатурой под сообщением'
    await message.answer(answer)


@dp.callback_query_handler(quantity_callback.filter(), state=WalkStates.enter_walk_quantity)
async def select_walk_dt(call: CallbackQuery, callback_data: dict, state: FSMContext):
    kb, result, modified = QuantityKb.get(callback_data)
    if result:
        await state.update_data(quantity=int(callback_data['current_quantity']))
        await WalkStates.enter_walk_date.set()
        await call.message.edit_text(call.message.html_text + '\n' + f'{hh_mm_printer(result)}')

        answer = hbold('3. Введите дату и время начала прогулки')
        await call.message.answer(answer, reply_markup=fast_datetime_kb)
    elif modified:
        await call.message.edit_reply_markup(kb)
    if callback_data['error'] == '0 started':
        await call.answer(text='Число не дожно начинаться с нуля', show_alert=True)
    if callback_data['error'] == 'empty number':
        await call.answer(text='Число не может быть пустым', show_alert=True)

    await call.answer()


@dp.callback_query_handler(fast_datetime_callback.filter(),
                           state=WalkStates.enter_walk_date)
async def fast_select_dt(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User):
    selected_btn = callback_data['minutes']
    await call.message.edit_text(
        call.message.html_text + '\n' + callback_data['title']
    )

    if selected_btn == '-1':
        await WalkStates.enter_walk_date_text.set()
        await call.answer()
        return

    selected_dt = get_local_now(user.timezone) - datetime.timedelta(minutes=int(selected_btn))
    await save(call.message, state, selected_dt, user)
    await call.answer()


@dp.message_handler(state=WalkStates.enter_walk_date)
async def fast_select_dt_error(message: types.Message):
    await message.answer('Для ввода даты и времени воспользуйтесь кнопками под сообщением',
                         reply_markup=cancel_kb)


@dp.message_handler(state=WalkStates.enter_walk_date_text)
async def save_record(message: types.Message, state: FSMContext, user: User):
    text = message.text
    parsed_dt = naive_to_local(parse_datetime(text), user.timezone)
    if not parsed_dt:
        await message.answer(hbold('Дата и время введены некорректно, попробуйте еще раз'),
                             reply_markup=cancel_kb)
        return

    await save(message, state, parsed_dt, user)


async def save(message, state: FSMContext, dt, user):
    await state.update_data(dt=dt)
    walk_data = await state.get_data()
    await state.finish()

    walk_record = WalkRecord(walk_data['quantity'], dt, token=user.token)
    await walk_record.save()
    walk_record_desc = walk_record.format_output(user.timezone, with_date=True)
    await message.answer(hbold('Прогулка успешно добавлена!\n\n👉') + walk_record_desc,
                         reply_markup=start_kb)
