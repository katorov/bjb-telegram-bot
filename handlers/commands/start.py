from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.markdown import hbold

from db_api import User
from db_api.utils import is_user_with_access
from filters import IsDeepLink, IsCorrectDeepLink
from keyboards.default import start_kb
from loader import dp
from services.invite_link import get_user_from_deeplink, delete_invite_link
from services.qiwi import Payment
from settings import strings


@dp.message_handler(CommandStart(), IsCorrectDeepLink(), state='*')
async def start_command_with_correct_deeplink(message: types.Message, state: FSMContext,
                                              user: User):
    await state.reset_state()

    if user.admin_access:
        text = 'Вам не нужно приглашение, т.к. Вы уже являетесь полноправным администратором'
        await message.answer(text=text, reply_markup=start_kb)
        return

    deep_link = message.get_args()
    inviter = await get_user_from_deeplink(deep_link)
    await delete_invite_link(inviter)
    await user.update(team_owner=inviter.id).apply()

    answer = hbold(f'{user.first_name}, добро пожаловать! \n')
    answer += f'Вы успешно добавлены в команду пользователя {inviter.full_name}\n\n'
    answer += 'Подробнее о боте /start\n'
    answer += 'Справка по командам /help'

    await message.answer(text=answer, reply_markup=start_kb)

    inviter_answer = f'{hbold(inviter.full_name)}, к Вашей команде присоединился пользователь ' \
                     f'{hbold(user.full_name)} по ссылке-приглашению. \n' \
                     f'Теперь ему доступны все команды бота.'
    await message.bot.send_message(chat_id=inviter.chat_id, text=inviter_answer,
                                   reply_markup=start_kb)


@dp.message_handler(CommandStart(), IsDeepLink(), state='*')
async def start_command_with_uncorrect_deeplink(message: types.Message, state: FSMContext, user):
    await state.reset_state()
    answer = 'Вы перешли по ссылке-приглашению, которая указана неверна или устарела.\n' \
             'Запросите новую ссылку у того, кто Вас пригласил.\n\n' \
             'Подробнее о боте /start\n '
    await message.answer(text=answer, reply_markup=None)


@dp.message_handler(CommandStart(), state='*')
async def start_command(message: types.Message, state: FSMContext, user):
    await state.reset_state()
    await message.answer(strings.START_GREETING.format(name=user.first_name), reply_markup=start_kb)

    if not is_user_with_access(user):
        answer = strings.START_PAYMENT.format(price=Payment.base_amount)
        await message.answer(answer, reply_markup=None)
