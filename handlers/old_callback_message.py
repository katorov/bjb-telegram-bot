from aiogram.types import CallbackQuery

from loader import dp


@dp.callback_query_handler(state=None)
@dp.callback_query_handler(state="*")
async def select_dt(call: CallbackQuery):
    print(call)
    await call.message.edit_reply_markup(None)
    await call.answer(text='Сообщение устарело', show_alert=True)
