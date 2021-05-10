from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import fast_datetime_callback

datetimes = [
    ['Сейчас', 0],
    ['10 мин назад', 10],
    ['20 мин назад', 20],
    ['30 мин назад', 30],
    ['1 час назад', 60],
    ['2 часа назад', 120],
    ['Ввести вручную', -1]
]

fast_datetime_btns = [
    InlineKeyboardButton(text=dt, callback_data=fast_datetime_callback.new(minutes=m, title=dt))
    for dt, m in datetimes
]
fast_datetime_kb = InlineKeyboardMarkup(inline_keyboard=[
    [*fast_datetime_btns[:3]],
    [*fast_datetime_btns[3:6]],
    [fast_datetime_btns[-1]]
])


long_datetimes = [
    ['Сейчас', 0],
    ['-10 мин', 10],
    ['-20 мин', 20],
    ['-30 мин', 30],
    ['-1 час', 60],
    ['-2 часа', 120],
    ['-3 часа', 180],
    ['-4 часа', 240],
    ['-5 часов', 300],
    ['-6 часов', 360],
    ['-7 часов', 420],
    ['-8 часов', 480],
    ['Ввести вручную', -1]
]

long_fast_datetime_btns = [
    InlineKeyboardButton(text=dt, callback_data=fast_datetime_callback.new(minutes=m, title=dt))
    for dt, m in long_datetimes
]
long_fast_datetime_kb = InlineKeyboardMarkup(inline_keyboard=[
    [*long_fast_datetime_btns[:4]],
    [*long_fast_datetime_btns[4:8]],
    [*long_fast_datetime_btns[8:12]],
    [long_fast_datetime_btns[-1]]
])