import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold

from bjb_toolkit.analytics.graph_object_helper import get_buffer_image
from db_api import OtherEventRecord
from db_api import SummaryRecord
from db_api.utils import get_record_class, get_records_between_dates, \
    get_text_journal, get_excel_journal
from handlers.states import ShowJournalStates
from keyboards.callback_datas import calendar_callback, event_callback, periods_callback, \
    journal_action_callback
from keyboards.inline.calendar import CalendarKeyboard
from keyboards.inline.select_journal_category import select_journal_category_kb
from loader import dp
from services.throttling import rate_limit


@rate_limit(limit=1)
@dp.message_handler(Text(equals='Журнал', ignore_case=True), state='*')
async def select_journal_category(message: types.Message, state: FSMContext):
    await state.reset_data()
    await ShowJournalStates.select_category.set()

    answer = hbold('Выберите категорию для отображения журнала событий')
    await message.answer(answer, reply_markup=select_journal_category_kb)


@dp.callback_query_handler(event_callback.filter(), state=ShowJournalStates.select_category)
async def show_journal(call: types.CallbackQuery, state: FSMContext, callback_data: dict, user):
    category = callback_data['name']

    today = datetime.date.today()
    await ShowJournalStates.show_data.set()
    await state.update_data(category=category, day_from=today, day_to=today, name_btn='Сегодня')
    schema_class = get_record_class(category)

    answer = await get_text_journal(cls=schema_class, day_from=today, day_to=today, user=user)
    await call.message.edit_text(answer, reply_markup=CalendarKeyboard.default_calendar_kb())
    await call.answer()


@dp.callback_query_handler(periods_callback.filter(), state=ShowJournalStates.show_data)
async def enter_fast_date_btn(call: types.CallbackQuery, state: FSMContext, callback_data: dict,
                              user):
    state_data = await state.get_data()
    category = state_data.get('category')

    fmt_date = callback_data['fmt_date']
    from_day = callback_data['from_day']
    to_day = callback_data['to_day']
    name_btn = callback_data['name']

    from_day = datetime.datetime.strptime(from_day, fmt_date).date()
    to_day = datetime.datetime.strptime(to_day, fmt_date).date()

    await state.update_data(day_from=from_day, day_to=to_day, name_btn=name_btn)
    schema_class = get_record_class(category)

    answer = await get_text_journal(schema_class, day_from=from_day, day_to=to_day, user=user)
    await call.answer()
    await call.message.edit_text(answer, reply_markup=CalendarKeyboard.default_calendar_kb())


@rate_limit(limit=0.5)
@dp.callback_query_handler(journal_action_callback.filter(), state=ShowJournalStates.show_data)
async def action_buttons(call: types.CallbackQuery, state: FSMContext, callback_data: dict, user):
    action = callback_data.get('name')
    if action == 'cancel':
        await call.message.delete()
        await state.finish()
    elif action == 'back':
        await state.reset_data()
        await ShowJournalStates.select_category.set()

        answer = hbold('Выберите категорию для отображения журнала событий')
        await call.message.edit_text(answer, reply_markup=select_journal_category_kb)
    elif action == 'download':
        state_data = await state.get_data()
        record_class = get_record_class(state_data['category'])
        await get_excel_journal(
            record_class,
            day_from=state_data['day_from'],
            day_to=state_data['day_to'],
            callback_query=call,
            user=user
        )
    elif action == 'analytics':

        state_data = await state.get_data()
        day_from = state_data['day_from']
        day_to = state_data['day_to']
        name_btn = state_data['name_btn']
        record_class = get_record_class(state_data['category'])

        records = await get_records_between_dates(record_class,
                                                  day_from=day_from,
                                                  day_to=day_to,
                                                  user=user)

        count_records = len(records)

        if count_records == 0:
            await call.answer('За указанный период нет ни одной записи', cache_time=1,
                              show_alert=True)
        elif record_class == OtherEventRecord:
            await call.answer('Для данной категории аналитика недоступна', cache_time=1000)
        elif record_class == SummaryRecord:
            await call.answer('Для просмотра аналитики выберите категорию', cache_time=1000)
        else:
            caption, fig = await record_class.get_analytics(records, user.timezone,
                                                            name_btn=name_btn)
            await call.bot.send_photo(chat_id=call.message.chat.id,
                                      photo=get_buffer_image(fig),
                                      caption=caption,
                                      reply_markup=None)
    await call.answer()


@dp.callback_query_handler(calendar_callback.filter(action='none'),
                           state=ShowJournalStates.show_data)
async def update_calendar(call: types.CallbackQuery):
    await call.answer(cache_time=100)


@dp.callback_query_handler(calendar_callback.filter(action='prev_month'),
                           state=ShowJournalStates.show_data)
@dp.callback_query_handler(calendar_callback.filter(action='next_month'),
                           state=ShowJournalStates.show_data)
async def update_calendar(call: types.CallbackQuery, callback_data: dict):
    kb, _, _ = CalendarKeyboard.update(callback_data)
    await call.message.edit_reply_markup(kb)
    await call.answer()


@dp.callback_query_handler(calendar_callback.filter(action='select_day'),
                           state=ShowJournalStates.show_data)
async def update_journal(call: types.CallbackQuery, callback_data: dict, state: FSMContext, user):
    kb, day, upd_day = CalendarKeyboard.update(callback_data)
    if upd_day:
        await state.update_data(day_from=day, day_to=day)
        state_data = await state.get_data()

        schema_class = get_record_class(state_data.get('category'))
        text = await get_text_journal(schema_class, day_from=day, day_to=day, user=user)
        await call.message.edit_text(text=text, reply_markup=kb)
    await call.answer()


@dp.callback_query_handler(calendar_callback.filter(action='hide_calendar'),
                           state=ShowJournalStates.show_data)
async def hide_calendar(call: types.CallbackQuery):
    kb = CalendarKeyboard.default_calendar_kb()
    await call.message.edit_reply_markup(kb)
    await call.answer()


@dp.callback_query_handler(calendar_callback.filter(action='show_calendar'),
                           state=ShowJournalStates.show_data)
async def show_calendar(call: types.CallbackQuery):
    kb = CalendarKeyboard.keyboard if CalendarKeyboard.keyboard else CalendarKeyboard.get()
    await call.message.edit_reply_markup(kb)
    await call.answer()
