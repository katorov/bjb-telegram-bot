from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hbold

from db_api import User
from db_api.utils import get_team_members, get_user, delete_team_member
from keyboards.callback_datas import edit_my_team_callback
from keyboards.inline.my_team import my_team_keyboard, edit_team_member_kb
from loader import dp
from services.throttling import rate_limit


@rate_limit(1)
@dp.message_handler(commands='team', state='*')
async def command_team(message: types.Message, user: User, state: FSMContext):
    await state.finish()
    await show_team(message, user, edit_message=False)


@dp.callback_query_handler(edit_my_team_callback.filter(action='select'))
async def select_member(call: types.CallbackQuery, callback_data: dict):
    member_id = callback_data.get('user_id')
    member = await get_user(member_id)

    answer = f'Вы уверены, что хотите удалить {member.full_name} из команды?'
    await call.message.edit_text(answer, reply_markup=edit_team_member_kb(member.id))
    await call.answer()


@dp.callback_query_handler(edit_my_team_callback.filter(action='back'))
async def go_back(call: types.CallbackQuery, callback_data: dict, user: User):
    await show_team(call.message, user, edit_message=True)
    await call.answer()


@dp.callback_query_handler(edit_my_team_callback.filter(action='delete'))
async def del_member(call: types.CallbackQuery, callback_data: dict, user: User):
    member = await get_user(callback_data.get('user_id'))
    await delete_team_member(member)

    await call.message.edit_text(f'{member.full_name} удален из Вашей команды')
    await call.answer()


async def show_team(message: types.Message, user: User, edit_message=False):
    team_members = await get_team_members(user)
    kb = None
    add_member_text = '✅ Для добавления нового участника в команду ' \
                      'получите одноразовую ссылку-приглашение \n' \
                      f'{hbold("Сгенерировать ссылку /invite")}\n\n'
    delete_member_text = f'❌ Для {hbold("удаления")} участника из команды ' \
                         f'выберите его из списка ниже'

    if not user.admin_access:
        answer = '❕ Управлять командой может только администратор команды.'
    elif len(team_members) == 0:
        answer = f'👨‍👩‍👦 {hbold("В вашей команде только Вы.")}\n\n'
        answer += add_member_text
    else:
        answer = f'👨‍👩‍👦 {hbold("В вашей команде участников: " + str(len(team_members) + 1))}\n\n'
        answer += add_member_text
        answer += delete_member_text
        kb = my_team_keyboard(team_members)

    if not edit_message:
        await message.answer(answer, reply_markup=kb)
    else:
        await message.edit_text(answer, reply_markup=kb)
