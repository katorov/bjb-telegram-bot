import calendar
import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.callback_datas import calendar_callback, periods_callback, journal_action_callback


class CalendarKeyboard:
    keyboard = None

    selected_date = datetime.date.today()
    showed_month = selected_date.month
    showed_year = selected_date.year

    callback = calendar_callback
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    months_names = ['ЯНВ', 'ФЕВ', 'МАР', 'АПР', 'МАЙ', 'ИЮН',
                    'ИЮЛ', 'АВГ', 'СЕН', 'ОКТ', 'НОЯ', 'ДЕК']

    @classmethod
    def get(cls, date=None):
        cls.selected_date = date if date else datetime.date.today()
        cls.showed_month = cls.selected_date.month
        cls.showed_year = cls.selected_date.year
        cls.keyboard = cls.create_keyboard()
        return cls.keyboard

    @classmethod
    def update(cls, callback_data):
        y, m, d = _get_y_m_d(callback_data)
        day = datetime.date(year=y, month=m, day=d)
        update_day = cls.selected_date != day
        if update_day:
            cls.selected_date = day

        action = callback_data['action']
        if action in ('next_month', 'prev_month'):
            delta_month = 1 if action == 'next_month' else -1
            cls.showed_year, cls.showed_month = _get_new_y_m(
                int(callback_data['showed_year']),
                int(callback_data['showed_month']),
                delta_month
            )
            cls.keyboard = cls.create_keyboard()

        return cls.keyboard, cls.selected_date, update_day

    @classmethod
    def create_keyboard(cls):
        weekdays = cls.weekdays
        cb = cls.callback
        date = cls.selected_date
        calendar_instance = calendar.Calendar()

        # Текущая выбранная дата
        y, m, d = date.year, date.month, date.day

        # Отображаемый месяц и год
        showed_y, showed_m = cls.showed_year, cls.showed_month
        month_name = cls.months_names[showed_m - 1]

        navigation_row = [
            InlineKeyboardButton(
                '◄',
                callback_data=cb.new("prev_month", y, m, d, showed_y, showed_m)
            ),
            InlineKeyboardButton(
                f'{month_name}, {showed_y}',
                callback_data=cb.new("none", y, m, d, showed_y, showed_m)
            ),
            InlineKeyboardButton(
                '►',
                callback_data=cb.new("next_month", y, m, d, showed_y, showed_m)
            ),
        ]

        names_days_row = [
            InlineKeyboardButton(
                weekdays[i],
                callback_data=cb.new("none", y, m, d, showed_y, showed_m)
            ) for i in range(7)
        ]

        days_rows = []
        for week in calendar_instance.monthdatescalendar(showed_y, showed_m):
            days_row = []
            for day in week:
                day_btn_text = ' ' if day.month != showed_m else str(day.day)
                day_btn_action = "none" if day.month != showed_m else "select_day"

                day_btn = InlineKeyboardButton(
                    day_btn_text,
                    callback_data=cb.new(day_btn_action, showed_y, showed_m, day.day,
                                         showed_y, showed_m)
                )
                days_row.append(day_btn)
            days_rows.append(days_row)

        continue_row = [
            InlineKeyboardButton(
                'Свернуть календарь',
                callback_data=cb.new("hide_calendar", y, m, d, showed_y, showed_m)
            )
        ]

        all_rows = [navigation_row, names_days_row] + days_rows + [continue_row]
        return InlineKeyboardMarkup(inline_keyboard=all_rows)

    @classmethod
    def default_calendar_kb(cls):
        date = cls.selected_date
        showed_y, showed_m = cls.showed_year, cls.showed_month

        c = journal_action_callback

        show_btn = InlineKeyboardButton('Открыть календарь 🗓', callback_data=cls.callback.new(
            "show_calendar", date.year, date.month, date.day, showed_y, showed_m))
        back_btn = InlineKeyboardButton('⬅', callback_data=c.new('back'))
        cancel_btn = InlineKeyboardButton('❌', callback_data=c.new('cancel'))
        analytics_btn = InlineKeyboardButton('📊', callback_data=c.new('analytics'))
        download_btn = InlineKeyboardButton('📎', callback_data=c.new('download'))

        periods = ['1:Сегодня', '2:2 дня', '3:3 дня',
                   '5:5 дней', '7:7 дней', '14:14 дней',
                   '31:Месяц', '183:Пол года', '365:Год']
        fmt_date = '%d/%m/%Y'

        fast_btns = []
        for period in periods:
            day_count, title = period.split(':')
            to_day = datetime.date.today()
            from_day = to_day - datetime.timedelta(int(day_count) - 1)
            btn = InlineKeyboardButton(
                text=title,
                callback_data=periods_callback.new(
                    from_day=from_day.strftime(fmt_date),
                    to_day=to_day.strftime(fmt_date),
                    fmt_date=fmt_date,
                    name=title
                )
            )
            fast_btns.append(btn)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [show_btn],
            [*fast_btns[:3]],
            [*fast_btns[3:6]],
            [*fast_btns[6:]],
            [back_btn, analytics_btn, download_btn, cancel_btn],
        ])
        return kb


def _get_y_m_d(callback_data: dict):
    """Returned [year, month, day] from callback_data"""
    return map(int, [callback_data['year'], callback_data['month'], callback_data['day']])


def _get_new_y_m(year, month, delta_month):
    """Returned (year, month) after change month"""
    if month == 12 and delta_month == 1:
        year += 1
        month = 1
    elif month == 1 and delta_month == -1:
        year -= 1
        month = 12
    else:
        month += delta_month
    return year, month
