from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import delete_record_callback


def delete_kb(event_id, event_type):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton('Удалить', callback_data=delete_record_callback.new(
                action='delete', record_id=event_id, event_type=event_type
            )),
            InlineKeyboardButton('Отмена', callback_data=delete_record_callback.new(
                action='cancel', record_id='-', event_type='-'
            ))
        ]
    ])
    return kb
