import io
import pandas as pd


async def dataframe_to_excel(dataframe, file_name, **kwargs):
    engine = kwargs.get('engine', 'xlsxwriter')
    datetime_format = kwargs.get('datetime_format', 'YYYY-MM-DD HH:MM:SS')
    sheet_name = kwargs.get('sheet_name', 'Выгрузка')

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine=engine, datetime_format=datetime_format) as writer:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()

    file = io.BytesIO(out.getvalue())
    file.name = file_name
    return file


async def send_file(bot, chat_id, file):
    await bot.send_document(chat_id, file)


async def send_xlsx_from_df(dataframe, file_name, callback_query):
    bot = callback_query.bot
    chat_id = callback_query.message.chat.id
    file = await dataframe_to_excel(dataframe, file_name)
    await send_file(bot, chat_id, file)
