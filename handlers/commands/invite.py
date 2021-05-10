from aiogram import types

from db_api import User
from loader import dp
from services.invite_link import generate_invite_link
from services.throttling import rate_limit


@rate_limit(1)
@dp.message_handler(commands='invite', state='*')
async def get_one_time_invite_link(message: types.Message, user: User):
    if not user.admin_access:
        answer = '❕ Приглашать новых участников может только администратор команды.'
    else:
        link = await generate_invite_link(user)
        answer = f"Для вступления в команду приглашенный пользователь должен перейти по ссылке:\n" \
                 f"{link}"

    await message.answer(answer, disable_notification=True)
