from aiogram import types

from db import models
from db import database as db


async def is_admin_filter(message: types.Message):
    return bool(await db.get_admin_by_tg_id(message.from_user.id))

async def is_manager_filter(message: types.Message):
    return bool(await db.get_manager_by_tg_id(message.from_user.id)) or bool(await db.get_admin_by_tg_id(message.from_user.id))
