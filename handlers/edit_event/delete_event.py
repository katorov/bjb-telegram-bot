from aiogram import types

from keyboards.callback_datas import delete_record_callback
from loader import dp
from db_api.utils import delete_record
from db_api import User


@dp.callback_query_handler(delete_record_callback.filter(action='delete'), state='*')
async def delete(call: types.CallbackQuery, callback_data: dict, user: User):
    event_id = int(callback_data.get('record_id'))
    event_type = callback_data.get('event_type')
    is_deleted = await delete_record(event_id, event_type, token=user.token)

    if is_deleted:
        answer = '<i>(Запись удалена)</i>'
        notification = 'Запись успешно удалена'
    else:
        answer = '<i>(Запись не найдена)</i>'
        notification = 'Не удалось найти запись, возможно она удалена'
    await dp.bot.edit_message_text(inline_message_id=call.inline_message_id,
                                   text=answer, reply_markup=None)
    await call.answer(text=notification)


@dp.callback_query_handler(delete_record_callback.filter(action='cancel'), state='*')
async def cancel(call: types.CallbackQuery, callback_data: dict, user: User):
    answer = '<i>(Удаление записи отменено)</i>'
    await dp.bot.edit_message_text(inline_message_id=call.inline_message_id,
                                   text=answer, reply_markup=None)

    notification = 'Удаление записи отменено'
    await call.answer(text=notification)
