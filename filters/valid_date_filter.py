from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from bjb_toolkit.datetime.datetime_parser import parse_datetime


class IsValidDate(BoundFilter):

    async def check(self, query: types.InlineQuery):
        return parse_datetime(query.query)
