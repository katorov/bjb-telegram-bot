from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callback_datas import quantity_callback


class QuantityKb:
    kb = None
    result = None

    @classmethod
    def get(cls, callback_data=None):
        modified = False
        if not cls.kb or not callback_data:
            modified = True
            cls.kb, cls.result = create_quantity_kb()
        elif callback_data['action'] != 'False':
            modified = True
            cls.kb, cls.result = create_quantity_kb(callback_data)

        return cls.kb, cls.result, modified


def create_quantity_kb(callback_data: dict = None):
    cur = callback_data.get('current_quantity') if callback_data else 'False'
    act = callback_data.get('action') if callback_data else 'False'

    new_cur = cur if cur != 'False' else ''

    continue_action = 'ok' if cur != 'False' else False
    continue_error = False if cur != 'False' else 'empty number'

    row1 = [
        InlineKeyboardButton(f'Введено {new_cur}', callback_data=quantity_callback.new(
            current_quantity=cur, action=False, error=False)),
        InlineKeyboardButton('Продолжить✅', callback_data=quantity_callback.new(
            current_quantity=cur, action=continue_action, error=continue_error)),
    ]

    row2 = [
        InlineKeyboardButton('1', callback_data=quantity_callback.new(
            current_quantity=new_cur + '1', action='digit', error=False)),
        InlineKeyboardButton('2', callback_data=quantity_callback.new(
            current_quantity=new_cur + '2', action='digit', error=False)),
        InlineKeyboardButton('3', callback_data=quantity_callback.new(
            current_quantity=new_cur + '3', action='digit', error=False)),
    ]

    row3 = [
        InlineKeyboardButton('4', callback_data=quantity_callback.new(
            current_quantity=new_cur + '4', action='digit', error=False)),
        InlineKeyboardButton('5', callback_data=quantity_callback.new(
            current_quantity=new_cur + '5', action='digit', error=False)),
        InlineKeyboardButton('6', callback_data=quantity_callback.new(
            current_quantity=new_cur + '6', action='digit', error=False)),
    ]

    row4 = [
        InlineKeyboardButton('7', callback_data=quantity_callback.new(
            current_quantity=new_cur + '7', action='digit', error=False)),
        InlineKeyboardButton('8', callback_data=quantity_callback.new(
            current_quantity=new_cur + '8', action='digit', error=False)),
        InlineKeyboardButton('9', callback_data=quantity_callback.new(
            current_quantity=new_cur + '9', action='digit', error=False)),
    ]

    after_zero_btn_error = '0 started' if cur == 'False' else False
    after_zero_btn_action = False if cur == 'False' else 'digit'
    after_zero_btn_quantity = new_cur + '0' if not after_zero_btn_error else False
    after_clear_action = False if cur == 'False' else 'clear'
    row5 = [
        InlineKeyboardButton(' ', callback_data=quantity_callback.new(
            current_quantity=cur, action=False, error=False)),
        InlineKeyboardButton('0', callback_data=quantity_callback.new(
            current_quantity=after_zero_btn_quantity, action=after_zero_btn_action, error=after_zero_btn_error)),
        InlineKeyboardButton('(очистить)', callback_data=quantity_callback.new(
            current_quantity=False, action=after_clear_action, error=False)),
    ]

    quantity_kb = InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4, row5])
    result = None if act != 'ok' else int(cur)
    return quantity_kb, result
