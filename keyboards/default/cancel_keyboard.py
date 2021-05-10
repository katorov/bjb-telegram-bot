from aiogram import types

cancel_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
cancel_kb.add('/cancel')
