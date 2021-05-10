import bjb_api
from aiogram.utils.markdown import hbold
from bjb_toolkit.datetime.datetime_parser import parse_json_dt
from bjb_toolkit.datetime.timezone_utils import naive_to_local, utc_to_local
from dateutil.parser import parse as parse_json_dt


class SummaryRecord:
    EVENT_CATEGORY = 'Все события'
    EXCEL_COLUMN_NAMES = ['Событие', 'Описание', 'Дата и время']

    FOOD, WALK, GYMNASTICS, OTHER_EVENT, SLEEP, TOILET = 'еда', 'прг', 'гим', 'др', 'сон', 'тлт'
    EVENT_TYPE_CHOICES = {
        FOOD: 'Питание',
        WALK: 'Прогулка',
        GYMNASTICS: 'Гимнастика',
        OTHER_EVENT: 'Другое событие',
        SLEEP: 'Сон',
        TOILET: 'Туалет',
    }

    def __init__(self, id, name, description, event_id, event_type, dt, token=None):
        self.id = id
        self.name = name
        self.description = description
        self.event_id = event_id
        self.event_type = self.EVENT_TYPE_CHOICES[event_type]
        self.dt = dt
        self.token = token

    @classmethod
    async def get_list(cls, token, day_from=None, day_to=None, offset=None, limit=None):
        if not offset and not limit:
            records, _ = await bjb_api.journal.SummaryRecord(token).get_list(
                dt_after=day_from,
                dt_before=day_to,
            )
        else:
            records, _ = await bjb_api.journal.SummaryRecord(token).get_list(
                offset=offset,
                limit=limit,
            )
        summary_records = [
            SummaryRecord(r['id'], r['name'], r['description'], r['event_id'], r['event_type'],
                          parse_json_dt(r['dt']))
            for r in records
        ]
        return summary_records

    def local_dt(self, timezone):
        return naive_to_local(self.dt, timezone)

    def format_output(self, timezone, with_date=False):
        name = self.name
        description = self.description

        fmt_date = "%d/%m/%Y %H:%M"
        fmt_time = "%H:%M"
        fmt = fmt_date if with_date else fmt_time

        dt = utc_to_local(self.dt, timezone).strftime(fmt)

        f_output = f'{hbold(dt)}  {name} - {description}\n'
        return f_output

    async def get_excel_columns(self):
        r = self
        columns = r.name, r.description, utc_to_local(r.dt).replace(tzinfo=None)
        return columns

    @classmethod
    async def get_analytics(cls, records, timezone, name_btn='период'):
        return None
