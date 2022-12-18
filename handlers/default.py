from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
import db.models as models

from states import AppStates

from settings import bot
from utils import replace_in_message


async def start_command(update: types.ChatJoinRequest):
    user_in_db = await db.get_user_by_tg_id(update.from_user.id)
    if not user_in_db:
        user = models.UserModel(
            first_name=update.from_user.first_name or '',
            last_name=update.from_user.last_name or '',
            username=update.from_user.username or '',
            tg_id=update.from_user.id
        )
        await db.create_user(user)

    text = await db.get_start_message()
    name = update.from_user.full_name
    if not name:
        name = update.from_user.username
    text = replace_in_message(text, 'USER', name)

    await update.approve()
    await bot.send_message(chat_id=update.from_user.id, text=text, parse_mode=types.ParseMode.HTML)


