import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from bjb_toolkit.datetime.datetime_parser import parse_datetime
from bjb_toolkit.datetime.timezone_utils import naive_to_local, get_local_now
from db_api import SleepRecord
from db_api import User
from handlers.states import SleepStates
from keyboards.callback_datas import event_callback, fast_datetime_callback
from keyboards.default import start_kb, cancel_kb
from keyboards.inline.fast_datetime_select import long_fast_datetime_kb
from loader import dp


@dp.callback_query_handler(event_callback.filter(name='Сон'), state="select_event")
async def select_sleep(call: CallbackQuery, state: FSMContext):
    await SleepStates.first()
    await state.update_data(user_id=call.from_user.id)
    await call.message.edit_text(call.message.html_text + '\n' + 'Сон')

    answer = hbold('2. Укажите дату и время начала сна')
    await call.message.answer(answer, reply_markup=long_fast_datetime_kb)


@dp.callback_query_handler(fast_datetime_callback.filter(),
                           state=SleepStates.enter_sleep_start_dt)
async def fast_start_dt(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User):
    selected_btn = int(callback_data['minutes'])
    selected_dt = get_local_now(user.timezone) - datetime.timedelta(minutes=selected_btn)

    if selected_btn == -1:
        await SleepStates.enter_sleep_start_dt_text.set()
        await call.answer()
        await call.message.edit_text(
            call.message.html_text + '\n' + callback_data['title']
        )
        return

    await call.message.edit_text(
        f"{call.message.html_text}\n"
        f"{selected_dt.strftime('%d/%m/%Y %H:%M')} ({callback_data['title']})"
    )
    await state.update_data(start_dt=selected_dt)
    await SleepStates.enter_sleep_end_dt.set()
    await call.answer()

    answer = hbold('3. Укажите дату и время окончания сна')
    await call.message.answer(answer, reply_markup=long_fast_datetime_kb)


@dp.callback_query_handler(fast_datetime_callback.filter(),
                           state=SleepStates.enter_sleep_end_dt)
async def fast_end_dt(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User):
    selected_btn = int(callback_data['minutes'])
    selected_dt = get_local_now(user.timezone) - datetime.timedelta(minutes=selected_btn)
    state_data = await state.get_data()
    start_dt = state_data['start_dt']

    if selected_btn == -1:
        await SleepStates.enter_sleep_end_dt_text.set()
        await call.answer()
        await call.message.edit_text(
            call.message.html_text + '\n' + callback_data['title']
        )
        return

    if selected_dt <= start_dt:
        await call.answer('Время окончания сна не может быть раньше, чем начало сна',
                          show_alert=True)
        return

    await call.message.edit_text(
        f"{call.message.html_text}\n"
        f"{selected_dt.strftime('%d/%m/%Y %H:%M')} ({callback_data['title']})"
    )

    await call.answer()
    await save(call.message, state, selected_dt, user)


@dp.message_handler(state=SleepStates.enter_sleep_start_dt)
@dp.message_handler(state=SleepStates.enter_sleep_end_dt)
async def select_sleep_quantity_error(message: types.Message):
    answer = 'Для ввода даты и времени воспользуйтесь кнопками под сообщением'
    await message.answer(answer)


@dp.message_handler(state=SleepStates.enter_sleep_start_dt_text)
async def start_dt_text(message: types.Message, state: FSMContext, user: User):
    text = message.text
    parsed_dt = naive_to_local(parse_datetime(text), user.timezone)
    if not parsed_dt:
        await message.answer(hbold('Дата и время введены некорректно, попробуйте еще раз'),
                             reply_markup=cancel_kb)
        return

    await state.update_data(start_dt=parsed_dt)
    await SleepStates.enter_sleep_end_dt.set()

    answer = hbold('3. Укажите дату и время окончания сна')
    await message.answer(answer, reply_markup=long_fast_datetime_kb)


@dp.message_handler(state=SleepStates.enter_sleep_end_dt_text)
async def end_dt_text(message: types.Message, state: FSMContext, user: User):
    text = message.text
    parsed_dt = naive_to_local(parse_datetime(text), user.timezone)
    if not parsed_dt:
        await message.answer(hbold('Дата и время введены некорректно, попробуйте еще раз'),
                             reply_markup=cancel_kb)
        return
    await save(message, state, parsed_dt, user)


async def save(message, state: FSMContext, dt, user):
    await state.update_data(end_dt=dt)
    state_data = await state.get_data()
    await state.finish()

    dt = state_data['start_dt']
    quantity = (state_data['end_dt'] - state_data['start_dt']).seconds // 60

    if state_data['end_dt'].date() > state_data['start_dt'].date():
        next_day = dt + datetime.timedelta(1)
        next_day = next_day.replace(hour=0, minute=0, second=0, microsecond=0)

        quantity_before_night = (next_day - dt).seconds // 60
        quantity_after_night = (state_data['end_dt'] - next_day).seconds // 60

        sleep_record_1 = SleepRecord(quantity_before_night, dt, token=user.token)
        sleep_record_2 = SleepRecord(quantity_after_night, next_day, token=user.token)

        await sleep_record_1.save()
        await sleep_record_2.save()

        sleep_record_1_desc = sleep_record_1.format_output(with_date=True, timezone=user.timezone)
        sleep_record_2_desc = sleep_record_2.format_output(with_date=True, timezone=user.timezone)

        text_answer = hbold('Сон успешно добавлен!\n\n👉 ') + sleep_record_1_desc
        text_answer += '👉 ' + sleep_record_2_desc

        await message.answer(text_answer, reply_markup=start_kb)
        return

    sleep_record = SleepRecord(quantity, dt, token=user.token)
    await sleep_record.save()
    sleep_record_desc = sleep_record.format_output(with_date=True, timezone=user.timezone)
    await message.answer(hbold('Сон успешно добавлен!\n\n👉 ') + sleep_record_desc,
                         reply_markup=start_kb)
