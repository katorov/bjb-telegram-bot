from aiogram.dispatcher.filters.state import StatesGroup, State


class FoodStates(StatesGroup):
    enter_food_category = State()
    enter_food_category_name = State()
    enter_food_quantity = State()
    enter_food_date = State()
    enter_food_date_text = State()


class ToiletStates(StatesGroup):
    enter_toilet_quantity = State()
    enter_toilet_date = State()
    enter_toilet_date_text = State()


class WalkStates(StatesGroup):
    enter_walk_quantity = State()
    enter_walk_date = State()
    enter_walk_date_text = State()


class SleepStates(StatesGroup):
    enter_sleep_start_dt = State()
    enter_sleep_start_dt_text = State()
    enter_sleep_end_dt = State()
    enter_sleep_end_dt_text = State()


class GymnasticsStates(StatesGroup):
    enter_gymnastics_quantity = State()
    enter_gymnastics_date = State()
    enter_gymnastics_date_text = State()


class OtherStates(StatesGroup):
    enter_other_category = State()
    enter_other_description = State()
    enter_other_date = State()
    enter_other_date_text = State()


class ShowJournalStates(StatesGroup):
    select_category = State()
    show_data = State()


class QiwiPaid(StatesGroup):
    waiting_for_payment = State()
