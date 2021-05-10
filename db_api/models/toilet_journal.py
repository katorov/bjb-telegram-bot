import bjb_api
from aiogram.utils.markdown import hbold
from bjb_toolkit.analytics.journal_analytics import get_toilet_analytics
from bjb_toolkit.datetime.datetime_parser import parse_json_dt
from bjb_toolkit.datetime.timezone_utils import naive_to_local, utc_to_local


class ToiletRecord:
    EVENT_CATEGORY = 'Туалет'
    EXCEL_COLUMN_NAMES = ['Категория, баллы', 'Дата и время']
    LOGO_URL = 'http://i.piccy.info/i9/d4048600bee03c529fcff6803eb9b076/1616183160/2556/1421782/Tualet.png'

    def __init__(self, category, dt, token=None):
        self.id = None
        self.category = category
        self.dt = dt
        self.token = token

    async def save(self):
        records = await bjb_api.journal.ToiletRecord(self.token).create(
            category=self.category,
            dt=self.dt
        )
        self.id = records['id']

    @classmethod
    async def delete(cls, token, record_id):
        await bjb_api.journal.ToiletRecord(token).delete(record_id)

    @classmethod
    async def get_list(cls, token, day_from, day_to, offset=None, limit=None):
        if not offset and not limit:
            records, _ = await bjb_api.journal.ToiletRecord(token).get_list(
                dt_after=day_from,
                dt_before=day_to,
            )
        else:
            records, _ = await bjb_api.journal.ToiletRecord(token).get_list(
                offset=offset,
                limit=limit,
            )
        return [ToiletRecord(r['category'], parse_json_dt(r['dt'])) for r in records]

    def local_dt(self, timezone):
        return naive_to_local(self.dt, timezone)

    def format_output(self, timezone, with_date=False):
        category = self.category

        fmt_date = "%d/%m/%Y %H:%M"
        fmt_time = "%H:%M"
        fmt = fmt_date if with_date else fmt_time

        dt = utc_to_local(self.dt, timezone).strftime(fmt)

        f_output = f'{hbold(dt)}  {category} балл(а)\n'
        return f_output

    async def get_excel_columns(self):
        r = self
        columns = r.category, utc_to_local(r.dt).replace(tzinfo=None)
        return columns

    @classmethod
    async def get_analytics(cls, records, timezone, name_btn='период'):
        fig, caption = get_toilet_analytics(records, timezone, period_name=name_btn)
        return caption, fig
