import logging

from aiogram import Dispatcher

from settings.config import ADMINS


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, text='Бот успешно запущен!')
        except Exception as error:
            logging.exception(error)
