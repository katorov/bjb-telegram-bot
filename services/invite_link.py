import time

from aiogram.utils.deep_linking import get_start_link

from db_api import User


async def generate_invite_link(user: User):
    user_id = user.id
    current_time = time.time()

    uniq_sequence = str(hash((user_id, current_time)))
    await user.update(invite_link=uniq_sequence).apply()

    invite_link = await get_start_link(payload=uniq_sequence)
    return invite_link


async def get_user_from_deeplink(deep_link: str) -> User:
    user = await User.query.where(User.invite_link == deep_link).gino.first()
    return user


async def delete_invite_link(user: User):
    await user.update(invite_link='').apply()
