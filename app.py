from aiogram import executor

import bjb_api
import filters
import handlers
import middlewares
from db_api import db_gino
from loader import dp
from services.notify_admins import on_startup_notify
from services.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    bjb_api.init_session()
    db = await db_gino.on_startup()
    await db.gino.drop_all()
    await db.gino.create_all()
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)


async def on_shutdown(dispatcher):
    await bjb_api.close_session()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
