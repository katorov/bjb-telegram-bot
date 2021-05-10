import bjb_api
from aiogram.utils.markdown import hbold
from bjb_toolkit.analytics.journal_analytics import get_sleep_analytics
from bjb_toolkit.datetime.datetime_parser import hh_mm_printer, parse_json_dt
from bjb_toolkit.datetime.timezone_utils import naive_to_local, utc_to_local


class SleepRecord:
    EVENT_CATEGORY = 'Сон'
    EXCEL_COLUMN_NAMES = ['Длительность', 'Дата и время начала сна']
    LOGO_URL = 'http://i.piccy.info/i9/1e4c4e0eff50e8f5145e4d421caa9252/1616183186/2818/1421782/Son.png'

    def __init__(self, duration, dt, token=None):
        self.id = None
        self.duration = duration
        self.dt = dt
        self.token = token

    async def save(self):
        record = await bjb_api.journal.SleepRecord(self.token).create(
            duration=self.duration,
            dt=self.dt
        )
        self.id = record['id']

    @classmethod
    async def delete(cls, token, record_id):
        await bjb_api.journal.SleepRecord(token).delete(record_id)

    @classmethod
    async def get_list(cls, token, day_from, day_to, offset=None, limit=None):
        if not offset and not limit:
            records, _ = await bjb_api.journal.SleepRecord(token).get_list(
                dt_after=day_from,
                dt_before=day_to,
            )
        else:
            records, _ = await bjb_api.journal.SleepRecord(token).get_list(
                offset=offset,
                limit=limit,
            )
        return [SleepRecord(r['duration'], parse_json_dt(r['dt'])) for r in records]

    def local_dt(self, timezone):
        return naive_to_local(self.dt, timezone)

    def format_output(self, timezone, with_date=False):
        duration = hh_mm_printer(self.duration)

        fmt_date = "%d/%m/%Y %H:%M"
        fmt_time = "%H:%M"
        fmt = fmt_date if with_date else fmt_time

        dt = utc_to_local(self.dt, timezone).strftime(fmt)

        f_output = f'{hbold(dt)}  {duration}\n'
        return f_output

    async def get_excel_columns(self):
        r = self
        columns = r.duration, utc_to_local(r.dt).replace(tzinfo=None)
        return columns

    @classmethod
    async def get_analytics(cls, records, timezone, name_btn='период'):
        fig, caption = get_sleep_analytics(records, timezone, period_name=name_btn)
        return caption, fig
