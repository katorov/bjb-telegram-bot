from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import event_callback, food_category_callback

categories = ['Молоко', 'Вода', 'Пища']
select_food_category_btns = [
    InlineKeyboardButton(
        text=category,
        callback_data=food_category_callback.new(name=category))
    for category in categories
]
select_food_category_kb = InlineKeyboardMarkup(inline_keyboard=[
    [*select_food_category_btns[:2]],
    [*select_food_category_btns[2:]]
])