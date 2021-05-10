import datetime

import pandas as pd
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold
from aiohttp import ClientResponseError
from asyncpg import UniqueViolationError
from sqlalchemy import and_

import bjb_api
from db_api import (
    FoodRecord, GymnasticsRecord, OtherEventRecord,
    SleepRecord, SummaryRecord, ToiletRecord, WalkRecord,
    User
)
from services.excel import send_xlsx_from_df
from services.generate_password import generate_random_password


async def get_user(user_id):
    return await User.query.where(User.id == int(user_id)).gino.first()


async def create_user(user_id, first_name, last_name='', token='',
                      admin_access=False, team_access=False) -> User:
    if not last_name:
        last_name = ''
    user = User(
        id=user_id,
        first_name=first_name,
        last_name=last_name,
        token=token,
        admin_access=admin_access,
        team_access=team_access
    )
    try:
        await user.create()
    except UniqueViolationError:
        user = await User.get(user_id)
    return user


async def get_or_create_user(from_user):
    user = await get_user(from_user.id)

    if not user:
        user_id = from_user.id
        first_name = from_user.first_name
        last_name = from_user.last_name if from_user.last_name else ''
        user = await create_user(user_id, first_name, last_name)

    return user


def get_record_class(record_type: str):
    mapper = {
        'питание': FoodRecord,
        'прогулка': WalkRecord,
        'туалет': ToiletRecord,
        'сон': SleepRecord,
        'гимнастика': GymnasticsRecord,
        'другое событие': OtherEventRecord,
        'все события': SummaryRecord,
    }
    return mapper.get(record_type.lower())


async def is_user_with_access(user: User):
    return user.admin_access or user.team_access


async def grant_access(user: User, is_paid=False):
    """Предоставить пользователю доступ к боту"""
    password = generate_random_password()
    await bjb_api.auth.User().register(
        username=user.id,
        password=password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_paid=is_paid,
        team=user.id,
    )
    access_token, _ = await bjb_api.auth.JWT().create(user.id, password)
    await user.update(token=access_token, team_access=True, admin_access=is_paid).apply()


async def get_team_members(user: User):
    query = and_(User.team_owner == user.team_owner, User.id != user.id)
    users = await User.query.where(query).gino.all()
    return users


async def delete_team_member(user: User):
    await user.update(team_owner=None).apply()


async def delete_record(event_id, event_type, token):
    RecordClass = get_record_class(event_type)
    try:
        await RecordClass.delete(token, str(event_id))
    except ClientResponseError:
        return False
    return True


async def get_records_between_dates(cls, user: User, day_from: datetime.date,
                                    day_to: datetime.date):
    records = await cls.get_list(user.token, day_from, day_to)
    return records


async def get_offset_records(cls, user: User, offset, limit):
    records = await cls.get_list(user.token, offset=offset, limit=limit)
    return records


async def get_text_journal(cls, day_from: datetime.date, day_to: datetime.date, user):
    title = day_from.strftime("%d/%m/%Y")
    if day_from != day_to:
        title += ' - ' + day_to.strftime("%d/%m/%Y")
    elif day_from == datetime.date.today():
        title = 'Сегодня ' + title
    answer = f'📄 {hbold(cls.EVENT_CATEGORY)}: {title}\n\n'

    records = await cls.get_list(token=user.token, day_from=day_from, day_to=day_to)

    with_date = not (day_to == day_from)
    if not records:
        answer += 'Нет записей'
    for record in records[:80]:
        answer += record.format_output(with_date=with_date, timezone=user.timezone)

    if len(records) > 80:
        answer += '\n\n И другие... \n' \
                  'Для полного просмотра выгрузите журнал в Excel'
    return answer


async def get_excel_journal(cls, callback_query: CallbackQuery, user: User,
                            day_from: datetime.date, day_to: datetime.date = None):
    records = await get_records_between_dates(cls, user=user, day_from=day_from, day_to=day_to)

    title = 'Журнал за ' + day_from.strftime("%d.%m.%Y")
    if day_from != day_to:
        title += ' - ' + day_to.strftime("%d.%m.%Y")
    title += f' ({cls.EVENT_CATEGORY}).xlsx'

    output_records = []
    for r in records:
        output_record = await r.get_excel_columns()
        output_records.append(output_record)

    df = pd.DataFrame(output_records, columns=cls.EXCEL_COLUMN_NAMES)
    await send_xlsx_from_df(df, title, callback_query)
