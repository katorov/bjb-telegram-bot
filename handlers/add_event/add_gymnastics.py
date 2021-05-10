import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from bjb_toolkit.datetime import naive_to_local, get_local_now, parse_datetime
from db_api import GymnasticsRecord, User
from handlers.states import GymnasticsStates
from keyboards.callback_datas import event_callback, quantity_callback, fast_datetime_callback
from keyboards.default import cancel_kb, start_kb
from keyboards.inline.fast_datetime_select import fast_datetime_kb
from keyboards.inline.quantity import QuantityKb
from loader import dp


@dp.callback_query_handler(event_callback.filter(name='Гимнастика'), state="select_event")
async def select_gymnastics_quantity(call: CallbackQuery, state: FSMContext):
    await GymnasticsStates.first()
    await state.update_data(user_id=call.from_user.id)
    await call.message.edit_text(call.message.html_text + '\n' + 'Гимнастика')

    answer = hbold('2. Укажите длительность в минутах')
    kb, _, _ = QuantityKb.get()
    await call.message.answer(answer, reply_markup=kb)


@dp.message_handler(state=GymnasticsStates.enter_gymnastics_quantity)
async def select_gymnastics_quantity_error(message: types.Message):
    answer = 'Для ввода длительности воспользуйтесь клавиатурой под сообщением'
    await message.answer(answer)


@dp.callback_query_handler(quantity_callback.filter(),
                           state=GymnasticsStates.enter_gymnastics_quantity)
async def select_gymnastics_dt(call: CallbackQuery, callback_data: dict, state: FSMContext):
    kb, result, modified = QuantityKb.get(callback_data)
    if result:
        await state.update_data(quantity=int(callback_data['current_quantity']))
        await GymnasticsStates.enter_gymnastics_date.set()
        await call.message.edit_text(call.message.html_text + '\n' + f'{result} минут')
        answer = hbold('3. Введите дату и время')
        await call.message.answer(answer, reply_markup=fast_datetime_kb)
    elif modified:
        await call.message.edit_reply_markup(kb)
    if callback_data['error'] == '0 started':
        await call.answer(text='Число не дожно начинаться с нуля', show_alert=True)
    if callback_data['error'] == 'empty number':
        await call.answer(text='Число не может быть пустым', show_alert=True)

    await call.answer()


@dp.callback_query_handler(fast_datetime_callback.filter(),
                           state=GymnasticsStates.enter_gymnastics_date)
async def fast_select_dt(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User):
    selected_btn = callback_data['minutes']
    await call.message.edit_text(
        call.message.html_text + '\n' + callback_data['title']
    )

    if selected_btn == '-1':
        await GymnasticsStates.enter_gymnastics_date_text.set()
        await call.answer()
        return

    selected_dt = get_local_now(user.timezone) - datetime.timedelta(minutes=int(selected_btn))
    await save(call.message, state, selected_dt, user)
    await call.answer()


@dp.message_handler(state=GymnasticsStates.enter_gymnastics_date)
async def fast_select_dt_error(message: types.Message):
    await message.answer('Для ввода даты и времени воспользуйтесь кнопками под сообщением',
                         reply_markup=cancel_kb)


@dp.message_handler(state=GymnasticsStates.enter_gymnastics_date_text)
async def save_record(message: types.Message, state: FSMContext, user: User):
    text = message.text
    parsed_dt = naive_to_local(parse_datetime(text), user.timezone)
    if not parsed_dt:
        await message.answer('Дата и время введены некорректно, попробуйте еще раз',
                             reply_markup=cancel_kb)
        return

    await save(message, state, parsed_dt, user)


async def save(message, state: FSMContext, dt, user: User):
    await state.update_data(dt=dt)
    gymnastics_data = await state.get_data()
    await state.finish()

    gymnastics_record = GymnasticsRecord(gymnastics_data['quantity'], dt, token=user.token)
    await gymnastics_record.save()
    gymnastics_record_desc = gymnastics_record.format_output(user.timezone, with_date=True)
    await message.answer(hbold('Гимнастика успешно добавлена!\n\n👉 ') + gymnastics_record_desc,
                         reply_markup=start_kb)
