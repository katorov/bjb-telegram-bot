from aiogram import types


async def set_default_commands(dp):
    """Установить команды бота по умолчанию для быстрого доступа из чата"""
    await dp.bot.set_my_commands([
        types.BotCommand("help", "Помощь"),
        types.BotCommand("cancel", "Отмена"),
        types.BotCommand("team", "Моя команда"),
        types.BotCommand("invite", "Пригласить в команду"),
    ])
