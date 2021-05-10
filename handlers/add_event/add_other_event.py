import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from bjb_toolkit.datetime.datetime_parser import parse_datetime
from bjb_toolkit.datetime.timezone_utils import naive_to_local, get_local_now
from db_api import OtherEventRecord
from db_api import User
from handlers.states import OtherStates
from keyboards.callback_datas import event_callback, fast_datetime_callback
from keyboards.default import cancel_kb, start_kb
from keyboards.inline.fast_datetime_select import fast_datetime_kb
from loader import dp


@dp.callback_query_handler(event_callback.filter(name='Другое'), state="select_event")
async def enter_name(call: CallbackQuery, state: FSMContext):
    await OtherStates.first()
    await state.update_data(user_id=call.from_user.id)
    await call.message.edit_text(call.message.html_text + '\n' + 'Другое событие')

    answer = hbold('2. Введите название события')
    await call.message.answer(answer, reply_markup=cancel_kb)


@dp.message_handler(state=OtherStates.enter_other_category)
async def enter_description(message: types.Message, state: FSMContext):
    name = message.text
    if len(name) > 100:
        await message.answer('Название не должно быть длиннее 100 символов')
        return

    await OtherStates.next()
    await state.update_data(name=name)
    question = hbold('3. Введите описание события')
    await message.reply(question, reply_markup=cancel_kb)


@dp.message_handler(state=OtherStates.enter_other_description)
async def enter_dt(message: types.Message, state: FSMContext):
    desc = message.text
    if len(desc) > 200:
        await message.answer('Описание не должно быть длиннее 200 символов')
        return

    await OtherStates.next()
    await state.update_data(description=desc)
    question = hbold('4. Введите дату и время события')
    await message.reply(question, reply_markup=fast_datetime_kb)


@dp.callback_query_handler(fast_datetime_callback.filter(),
                           state=OtherStates.enter_other_date)
async def fast_select_dt(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User):
    selected_btn = callback_data['minutes']
    await call.message.edit_text(
        call.message.html_text + '\n' + callback_data['title']
    )

    if selected_btn == '-1':
        await OtherStates.enter_other_date_text.set()
        await call.answer()
        return

    selected_dt = get_local_now(user.timezone) - datetime.timedelta(minutes=int(selected_btn))
    await save(call.message, state, selected_dt, user)
    await call.answer()


@dp.message_handler(state=OtherStates.enter_other_date)
async def fast_select_dt_error(message: types.Message):
    await message.answer('Для ввода даты и времени воспользуйтесь кнопками под сообщением',
                         reply_markup=cancel_kb)


@dp.message_handler(state=OtherStates.enter_other_date_text)
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
    other_record_data = await state.get_data()
    await state.finish()

    other_record = OtherEventRecord(name=other_record_data['name'],
                                    description=other_record_data['description'],
                                    dt=other_record_data['dt'],
                                    token=user.token)
    await other_record.save()
    other_record_desc = other_record.format_output(user.timezone, with_date=True)
    await message.answer(hbold('Событие успешно добавлено!\n\n👉 ') + other_record_desc,
                         reply_markup=start_kb)
