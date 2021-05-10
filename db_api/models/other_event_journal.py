import bjb_api
from aiogram.utils.markdown import hbold
from bjb_toolkit.datetime.datetime_parser import parse_json_dt
from bjb_toolkit.datetime.timezone_utils import naive_to_local, utc_to_local


class OtherEventRecord:
    EVENT_CATEGORY = 'Другие события'
    EXCEL_COLUMN_NAMES = ['Событие', 'Описание', 'Дата и время']
    LOGO_URL = 'http://i.piccy.info/i9/1a861efd399c86cb12f1f42b8fca7245/1616183205/2112/1421782/Drugoe_sobytye.png'

    def __init__(self, name, description, dt, token=None):
        self.id = None
        self.name = name
        self.description = description
        self.dt = dt
        self.token = token

    async def save(self):
        record = await bjb_api.journal.OtherEventRecord(self.token).create(
            name=self.name,
            description=self.description,
            dt=self.dt
        )
        self.id = record['id']

    @classmethod
    async def delete(cls, token, record_id):
        await bjb_api.journal.OtherEventRecord(token).delete(record_id)

    @classmethod
    async def get_list(cls, token, day_from, day_to, offset=None, limit=None):
        if not offset and not limit:
            records, _ = await bjb_api.journal.OtherEventRecord(token).get_list(
                dt_after=day_from,
                dt_before=day_to,
            )
        else:
            records, _ = await bjb_api.journal.OtherEventRecord(token).get_list(
                offset=offset,
                limit=limit,
            )
        food_records = [
            OtherEventRecord(r['name'], r['description'], parse_json_dt(r['dt']))
            for r in records
        ]
        return food_records

    def local_dt(self, timezone):
        return naive_to_local(self.dt, timezone)

    def format_output(self, timezone, with_date=False):
        name = self.name
        descr = self.description

        fmt_date = "%d/%m/%Y %H:%M"
        fmt_time = "%H:%M"
        fmt = fmt_date if with_date else fmt_time

        dt = utc_to_local(self.dt, timezone).strftime(fmt)

        f_output = f'{hbold(dt)}  {name} - {descr}\n'
        return f_output

    async def get_excel_columns(self):
        r = self
        columns = r.name, r.description, utc_to_local(r.dt).replace(tzinfo=None)
        return columns

    @classmethod
    async def get_analytics(cls, records, timezone, name_btn='период'):
        return None, None
