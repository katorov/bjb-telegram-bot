import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from bjb_toolkit.datetime.datetime_parser import parse_datetime
from bjb_toolkit.datetime.timezone_utils import naive_to_local, get_local_now
from db_api import FoodRecord
from db_api import User
from handlers.states import FoodStates
from keyboards.callback_datas import event_callback, food_category_callback, quantity_callback, \
    fast_datetime_callback
from keyboards.default import start_kb, cancel_kb
from keyboards.inline.fast_datetime_select import fast_datetime_kb
from keyboards.inline.quantity import QuantityKb
from keyboards.inline.select_food_category import select_food_category_kb
from loader import dp


@dp.callback_query_handler(event_callback.filter(name='Питание'), state="select_event")
async def select_food_category(call: CallbackQuery, state: FSMContext, user):
    await FoodStates.first()
    await state.update_data(user_id=user.id)
    await call.message.edit_text(call.message.html_text + '\n' + 'Питание', reply_markup=None)

    answer = hbold('2. Выберите нужную категорию')
    await call.message.answer(answer, reply_markup=select_food_category_kb)


@dp.message_handler(state=FoodStates.enter_food_category)
async def select_food_category_error(message: types.Message):
    answer = 'Для выбора категории питания нужно нажать на кнопку'
    await message.answer(answer)


@dp.callback_query_handler(food_category_callback.filter(name='Пища'),
                           state=FoodStates.enter_food_category)
async def enter_food_category_name(call: CallbackQuery, state: FSMContext):
    await FoodStates.enter_food_category_name.set()
    await state.update_data(category='Пища'[0].lower())
    await call.answer()
    await call.message.edit_text(call.message.html_text + '\n' + 'Пища', reply_markup=None)
    await call.message.answer(hbold('2.1. Введите название пищи'), reply_markup=cancel_kb)


@dp.message_handler(state=FoodStates.enter_food_category_name)
async def select_food_quantity_2(message: types.Message, state: FSMContext):
    subcategory_name = message.text
    if len(subcategory_name) > 100:
        await message.answer('Название пищи не должно быть длиннее 100 символов')
    else:
        await state.update_data(name=message.text)
        await FoodStates.enter_food_quantity.set()
        answer = hbold('3. Введите количество (г)')

        kb, _, _ = QuantityKb.get()
        await message.reply(answer, reply_markup=kb)


@dp.callback_query_handler(food_category_callback.filter(name='Молоко'),
                           state=FoodStates.enter_food_category)
@dp.callback_query_handler(food_category_callback.filter(name='Вода'),
                           state=FoodStates.enter_food_category)
async def select_food_quantity(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(category=callback_data['name'][0].lower())
    await FoodStates.enter_food_quantity.set()
    await call.message.edit_text(call.message.html_text + '\n' + callback_data.get('name'))
    answer = hbold('3. Введите количество (мл)')

    kb, _, _ = QuantityKb.get()
    await call.message.answer(answer, reply_markup=kb)


@dp.message_handler(state=FoodStates.enter_food_quantity)
async def select_food_quantity_error(message: types.Message):
    answer = 'Для ввода количества воспользуйтесь кнопками под сообщением'
    await message.answer(answer)


@dp.callback_query_handler(quantity_callback.filter(), state=FoodStates.enter_food_quantity)
async def select_dt(call: CallbackQuery, callback_data: dict, state: FSMContext):
    kb, result, modified = QuantityKb.get(callback_data)
    if result:
        await state.update_data(quantity=int(callback_data['current_quantity']))
        await FoodStates.enter_food_date.set()
        await call.message.edit_text(call.message.html_text + '\n' + f'{result} мл')
        answer = hbold('4. Введите дату и время')
        await call.message.answer(answer, reply_markup=fast_datetime_kb)
    elif modified:
        await call.message.edit_reply_markup(kb)
    if callback_data['error'] == '0 started':
        await call.answer(text='Число не дожно начинаться с нуля', show_alert=True)
    if callback_data['error'] == 'empty number':
        await call.answer(text='Число не может быть пустым', show_alert=True)

    await call.answer()


@dp.callback_query_handler(fast_datetime_callback.filter(), state=FoodStates.enter_food_date)
async def fast_select_dt(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User):
    selected_btn = callback_data['minutes']
    await call.message.edit_text(
        call.message.html_text + '\n' + callback_data['title']
    )

    if selected_btn == '-1':
        await FoodStates.enter_food_date_text.set()
        await call.answer()
        return

    selected_dt = get_local_now(user.timezone) - datetime.timedelta(minutes=int(selected_btn))
    await save(call.message, state, selected_dt, user)
    await call.answer()


@dp.message_handler(state=FoodStates.enter_food_date)
async def fast_select_dt_error(message: types.Message):
    await message.answer(hbold('Для ввода даты и времени воспользуйтесь кнопками под сообщением'),
                         reply_markup=cancel_kb)


@dp.message_handler(state=FoodStates.enter_food_date_text)
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
    food_data = await state.get_data()
    food_record = FoodRecord(
        category=food_data['category'],
        name=food_data.get('name', ''),
        quantity=food_data['quantity'],
        dt=food_data['dt'],
        token=user.token
    )
    await food_record.save()
    food_record_desc = food_record.format_output(user.timezone, with_date=True)
    await state.finish()

    await message.answer('Питание успешно добавлено в журнал!\n\n👉' + food_record_desc,
                         reply_markup=start_kb)
