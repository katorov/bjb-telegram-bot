from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from db_api import User


class IsDeepLink(BoundFilter):
    async def check(self, message: types.Message, *args) -> bool:
        deep_link = message.get_args()

        if not deep_link:
            return False

        return True


class IsCorrectDeepLink(BoundFilter):
    async def check(self, message: types.Message, *args) -> bool:
        deep_link = message.get_args()

        if not deep_link:
            return False

        user = await User.query.where(User.invite_link == deep_link).gino.first()
        if not user:
            return False

        return True
