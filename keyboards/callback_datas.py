from aiogram.utils.callback_data import CallbackData

event_callback = CallbackData('event', 'name')

journal_event_callback = CallbackData('event', 'name')

journal_action_callback = CallbackData('action', 'name')

food_category_callback = CallbackData('food_category', 'name')

quantity_callback = CallbackData('quantity', 'current_quantity', 'action', 'error')

toilet_callback = CallbackData('toilet', 'cat')

calendar_callback = CallbackData('calendar',
                                 'action', 'year', 'month', 'day',
                                 'showed_year', 'showed_month')

periods_callback = CallbackData('periods', 'from_day', 'to_day', 'fmt_date', 'name')

fast_datetime_callback = CallbackData('fast_datetime', 'minutes', 'title')

paid_callback = CallbackData('paid', 'action')

edit_my_team_callback = CallbackData('edit_my_team', 'action', 'user_id')

delete_record_callback = CallbackData('delete_record', 'action', 'record_id', 'event_type')