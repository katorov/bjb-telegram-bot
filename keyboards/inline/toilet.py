from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import toilet_callback

toilet_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('1 (мало)', callback_data=toilet_callback.new('1'))],
    [InlineKeyboardButton('2 (как обычно)', callback_data=toilet_callback.new('2'))],
    [InlineKeyboardButton('3 (много)', callback_data=toilet_callback.new('3'))],
    [InlineKeyboardButton('4 (реально шок)', callback_data=toilet_callback.new('4'))]
])