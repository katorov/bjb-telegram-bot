import bjb_api
from aiogram.utils.markdown import hbold
from bjb_toolkit.analytics.journal_analytics import get_food_analytics
from bjb_toolkit.datetime.datetime_parser import parse_json_dt
from bjb_toolkit.datetime.timezone_utils import naive_to_local, utc_to_local


class FoodRecord:
    EVENT_CATEGORY = 'Питание'
    EXCEL_COLUMN_NAMES = ['Пища', 'Количество, гр', 'Дата и время']
    LOGO_URL = 'http://i.piccy.info/i9/ca1f5ac9d6aa411137ffe16b03dd5308/1616183046/3556/1421782/Pytanye_2.png'

    MILK, WATER, NUTRITION = 'м', 'в', 'п'
    FOOD_TYPE_CHOICES = {
        MILK: 'Молоко',
        WATER: 'Вода',
        NUTRITION: 'Пища',
    }

    def __init__(self, category, quantity, dt, name=None, token=None):
        self.id = None
        self.category = category
        self.name = name
        self.quantity = quantity
        self.dt = dt
        self.token = token

    @property
    def full_category(self):
        return self.name if self.name else self.FOOD_TYPE_CHOICES[self.category]

    async def save(self):
        record = await bjb_api.journal.FoodRecord(self.token).create(
            category=self.category,
            name=self.name,
            quantity=self.quantity,
            dt=self.dt
        )
        self.id = record['id']

    @classmethod
    async def delete(cls, token, record_id):
        await bjb_api.journal.FoodRecord(token).delete(record_id)

    @classmethod
    async def get_list(cls, token, day_from, day_to, offset=None, limit=None):
        if not offset and not limit:
            records, _ = await bjb_api.journal.FoodRecord(token).get_list(
                dt_after=day_from,
                dt_before=day_to,
            )
        else:
            records, _ = await bjb_api.journal.FoodRecord(token).get_list(
                offset=offset,
                limit=limit,
            )
        food_records = [
            FoodRecord(r['category'], r['quantity'], parse_json_dt(r['dt']), r['name'])
            for r in records
        ]
        return food_records

    def local_dt(self, timezone):
        return naive_to_local(self.dt, timezone)

    def format_output(self, timezone, with_date=False):
        full_category = self.full_category
        quantity = self.quantity

        fmt_date = "%d/%m/%Y %H:%M"
        fmt_time = "%H:%M"
        fmt = fmt_date if with_date else fmt_time
        dt = utc_to_local(self.dt, timezone).strftime(fmt)

        f_output = f'{hbold(dt)}  {full_category} - {quantity}гр\n'
        return f_output

    async def get_excel_columns(self):
        r = self
        columns = r.full_category, r.quantity, utc_to_local(r.dt).replace(tzinfo=None)
        return columns

    @classmethod
    async def get_analytics(cls, records, timezone, name_btn='период'):
        fig, caption = get_food_analytics(records, timezone, period_name=name_btn)
        return caption, fig
