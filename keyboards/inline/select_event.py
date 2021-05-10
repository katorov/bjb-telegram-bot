from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import event_callback

events = ['Питание', 'Прогулка', 'Туалет', 'Сон', 'Гимнастика', 'Другое', ]

select_event_btns = [
    InlineKeyboardButton(text=event, callback_data=event_callback.new(event)) for event in events
]
select_event_kb = InlineKeyboardMarkup(inline_keyboard=[
    [*select_event_btns[:3]],
    [*select_event_btns[3:]]
])