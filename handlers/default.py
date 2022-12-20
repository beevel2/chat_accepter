import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
import db.models as models

from states import AppStates

from settings import bot
from utils import replace_in_message
import keyboards as kb


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

    name = update.from_user.full_name
    if not name:
        name = update.from_user.username

    await update.approve()
    msg1 = await db.get_message('start_message_1')
    msg2 = await db.get_message('start_message_2')
    _kb1 = kb.kb_mass_send(msg1['buttons'])
    _kb2 = kb.kb_mass_send(msg2['buttons'])
    await bot.send_video_note(chat_id=update.from_user.id, video_note=msg1['file_id'], reply_markup=_kb1)
    if msg2['data']['video_note_id']:
        await bot.send_video_note(chat_id=update.from_user.id, video_note=msg2['data']['video_note_id'], reply_markup=_kb2)
    if msg2['data']['photos'] or msg2['data']['video_id']:
        media = types.MediaGroup()
        if msg2['data']['photos']:
            for p in msg2['data']['photos']:
                media.attach_photo(photo=p)
        if msg2['data']['video_id']:
            media.attach_video(msg2['data']['video_id'])
        await bot.send_media_group(update.from_user.id, media=media)
    _text = replace_in_message(msg2['data']['text'], 'USER', name) 
    if _text:
        await bot.send_message(update.from_user.id, text=_text, reply_markup=_kb2, parse_mode=types.ParseMode.HTML)

    await asyncio.sleep(60*5)

    msg3 = await db.get_message('start_message_3')
    _kb3 = kb.kb_mass_send(msg3['buttons'])

    if msg3['data']['video_note_id']:
        await bot.send_video_note(chat_id=update.from_user.id, video_note=msg3['data']['video_note_id'], reply_markup=_kb2)
    if msg3['data']['photos'] or msg3['data']['video_id']:
        media = types.MediaGroup()
        if msg3['data']['photos']:
            for p in msg3['data']['photos']:
                media.attach_photo(photo=p)
        if msg3['data']['video_id']:
            media.attach_video(msg3['data']['video_id'])
        await bot.send_media_group(update.from_user.id, media=media)
    _text = replace_in_message(msg3['data']['text'], 'USER', name) 
    if _text:
        await bot.send_message(update.from_user.id, text=_text, reply_markup=_kb3, parse_mode=types.ParseMode.HTML)
