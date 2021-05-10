from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import paid_callback

paid_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Оплатил', callback_data=paid_callback.new(action='оплачено')),
        InlineKeyboardButton('Отмена', callback_data=paid_callback.new(action='отмена'))
    ]
])
