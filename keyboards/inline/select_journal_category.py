from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callback_datas import event_callback

all_events_name = 'ВСЕ СОБЫТИЯ'
events = ['Питание', 'Прогулка', 'Туалет', 'Сон', 'Гимнастика', 'Другое', all_events_name]

select_journal_category_btns = [
    InlineKeyboardButton(text=event, callback_data=event_callback.new(event)) for event in events
]
select_journal_category_kb = InlineKeyboardMarkup(inline_keyboard=[
    [*select_journal_category_btns[:3]],
    [*select_journal_category_btns[3:-1]],
    [select_journal_category_btns[-1]],
])