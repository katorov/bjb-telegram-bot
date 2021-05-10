from aiogram import types

from bjb_toolkit.datetime.datetime_parser import parse_datetime
from bjb_toolkit.datetime.timezone_utils import utc_to_local
from db_api import SummaryRecord
from db_api.utils import get_record_class, get_records_between_dates, \
    get_offset_records
from filters.valid_date_filter import IsValidDate
from keyboards.inline.delete_record import delete_kb
from loader import dp


@dp.inline_handler(text="", state='*')
async def show_all_records(query: types.InlineQuery, user):
    limit = 50
    offset = int(query.offset) if query.offset else 0

    records = await get_offset_records(SummaryRecord, user, offset=offset, limit=limit)
    next_offset = offset + len(records) if records else ''

    results = get_inline_results(records, user.timezone, with_date=True)
    await query.answer(results=results, next_offset=str(next_offset), cache_time=0)


@dp.inline_handler(IsValidDate(), state='*')
async def show_selected_date_records(query: types.InlineQuery, user):
    selected_date = parse_datetime(query.query)
    records = await get_records_between_dates(SummaryRecord, user, selected_date, selected_date)
    results = get_inline_results(records, with_date=False)
    await query.answer(results=results, cache_time=3)


def get_inline_results(all_records, timezone, with_date=True):
    results = []
    for record in all_records:
        event_type = record.event_type
        dt = utc_to_local(record.dt, timezone)
        dt = dt.strftime('%d/%m/%y %H:%M') if with_date else dt.strftime('%H:%M')
        title = f'{dt}  {record.name}'
        description = record.description
        logo_url = get_record_class(event_type).LOGO_URL

        message_text = record.format_output(timezone, with_date=True)

        result = types.InlineQueryResultArticle(
            id=str(record.id),
            title=title,
            description=description,
            input_message_content=types.InputTextMessageContent(
                message_text=message_text
            ),
            reply_markup=delete_kb(record.event_id, record.event_type),
            thumb_url=logo_url
        )
        results.append(result)
    return results
