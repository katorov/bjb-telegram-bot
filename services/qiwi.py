import datetime

import pyqiwi

from db_api import User
from settings.config import QIWI_TOKEN, QIWI_WALLET, QIWI_PUBKEY, BASE_AMOUNT

wallet = pyqiwi.Wallet(token=QIWI_TOKEN, number=QIWI_WALLET)


class NotEnoughMoney(Exception):
    pass


class PaymentNotFound(Exception):
    pass


class Payment:
    base_amount = BASE_AMOUNT

    def __init__(self, user: User, amount=None):
        self.user = user
        self.amount = amount if amount else self.__class__.base_amount
        self.payment_id = self.create()

    def create(self):
        user = self.user
        payment_id = f'baby_journal_bot_{user.id}'
        return payment_id

    def check_payment(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(14)

        transactions = wallet.history(start_date=start_date, rows=50).get('transactions')
        for transaction in transactions:
            if transaction.comment and (self.payment_id in transaction.comment):
                if float(transaction.total.amount) >= float(self.amount):
                    return True
                else:
                    raise NotEnoughMoney()
        else:
            raise PaymentNotFound()

    @property
    def invoice(self):
        link = "https://oplata.qiwi.com/create?publicKey={pubkey}&amount={amount}&comment={comment}"
        return link.format(pubkey=QIWI_PUBKEY, amount=self.amount, comment=self.payment_id)
