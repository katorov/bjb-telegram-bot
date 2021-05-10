from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hlink, hbold

from db_api import User
from db_api.utils import grant_access
from handlers.states import QiwiPaid
from keyboards.callback_datas import paid_callback
from keyboards.default import start_kb
from keyboards.inline.purchase import paid_kb
from loader import dp
from services.qiwi import Payment, NotEnoughMoney, PaymentNotFound


@dp.message_handler(Command('payment'))
async def start_payment(message: types.Message, user: User, state: FSMContext):
    amount = Payment.base_amount
    payment = Payment(user=user, amount=amount)

    answer = f"""
{hbold('Перейдите по ссылке ниже, внесите оплату и нажмите кнопку "Оплатил".')} 
Доступны платежи Visa/Mastercard/МИР.

💰 Сумма оплаты: {amount} руб.
👉 {hlink('Ссылка на оплату', url=payment.invoice)}
    """

    await QiwiPaid.waiting_for_payment.set()
    await state.update_data(payment=payment)
    await message.answer(answer, reply_markup=paid_kb)


@dp.callback_query_handler(paid_callback.filter(action='отмена'),
                           state=QiwiPaid.waiting_for_payment)
async def cancel_payment(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_reply_markup(None)
    await call.message.answer('Оплата отменена')
    await state.finish()


@dp.callback_query_handler(paid_callback.filter(action='оплачено'),
                           state=QiwiPaid.waiting_for_payment)
async def check_payment(call: types.CallbackQuery, state: FSMContext, user: User):
    state_data = await state.get_data()
    payment = state_data['payment']

    try:
        payment.check_payment()
    except NotEnoughMoney:
        answer = 'Вы оплатили не всю сумму'
        await call.message.answer(answer)
    except PaymentNotFound:
        answer = 'Оплата не найдена.'
        await call.message.answer(answer)
    else:
        await grant_access(user, is_paid=True)
        await call.message.edit_reply_markup(None)
        answer = hbold('Оплата принята, начните пользоваться ботом прямо сейчас!\n') + \
                 'Инструкция и справка по командам /help'
        await call.message.answer(answer, reply_markup=start_kb)
        await state.finish()

    await call.answer()
