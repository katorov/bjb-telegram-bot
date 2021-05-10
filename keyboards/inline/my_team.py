from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import edit_my_team_callback


def my_team_keyboard(users):
    cb = edit_my_team_callback

    btns = []
    for user in users:
        btns.append(InlineKeyboardButton(text=user.full_name,
                                         callback_data=cb.new(action='select', user_id=user.id)))

    kb = InlineKeyboardMarkup()
    kb.add(*btns)

    return kb


def edit_team_member_kb(user_id):
    cb = edit_my_team_callback

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Назад',
                                 callback_data=cb.new(action='back', user_id=user_id)),

            InlineKeyboardButton(text='Удалить',
                                 callback_data=cb.new(action='delete', user_id=user_id))
        ]
    ])
    return kb
