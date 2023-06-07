import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
import db.models as models

from states import AppStates

from settings import bot
from utils import replace_in_message
import keyboards as kb


async def send_start_message(msg, chat_id, name, delete_kb=False):
    if delete_kb:
        _kb = None
    else:
        _kb = kb.kb_mass_send(msg['buttons'])
    _text = replace_in_message(msg['data']['text'], 'USER', name) 
    if msg['data']['video_note_id']:
        await bot.send_video_note(chat_id=chat_id, video_note=msg['data']['video_note_id'], reply_markup=_kb)
    elif msg['data']['photos'] and len(msg['data']['photos']) == 1:
        if _text:
            await bot.send_photo(chat_id=chat_id, photo=msg['data']['photos'][0], caption=_text, parse_mode=types.ParseMode.HTML, reply_markup=_kb)
        else:
            await bot.send_photo(chat_id=chat_id, photo=msg['data']['photos'][0], parse_mode=types.ParseMode.HTML, reply_markup=_kb)
    elif msg['data']['photos'] or msg['data']['video_id']:
        media = types.MediaGroup()
        if msg['data']['photos']:
            for _i, p in enumerate(msg['data']['photos']):
                if _i == 0 and _text:
                    media.attach_photo(photo=p, caption=_text, parse_mode=types.ParseMode.HTML)
                else:
                    media.attach_photo(photo=p)
        if msg['data']['video_id']:
            media.attach_video(msg['data']['video_id'])
        await bot.send_media_group(chat_id, media=media)
    elif msg['data']['animation_id']:
        if _text:
            await bot.send_animation(chat_id=chat_id, animation=msg['data']['animation_id'], caption=_text, parse_mode=types.ParseMode.HTML, reply_markup=_kb)
        else:
            await bot.send_animation(chat_id=chat_id, animation=msg['data']['animation_id'], reply_markup=_kb)
    elif msg['data']['voice_id']:
        if _text:
            await bot.send_voice(chat_id=chat_id, voice=msg['data']['voice_id'], caption=_text, parse_mode=types.ParseMode.HTML, reply_markup=_kb)
        else:
            await bot.send_voice(chat_id=chat_id, voice=msg['data']['voice_id'], reply_markup=_kb)
    elif _text:
        await bot.send_message(chat_id, text=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)


async def start_command(update: types.ChatJoinRequest):
    _channel_id = -1
    _channel = await db.get_channel_by_link_name(update.invite_link.name)
    if _channel:
        _channel_id = _channel['channel_id']
    user_in_db = await db.get_user_by_tg_id(update.from_user.id)
    if not user_in_db:
        user = models.UserModel(
            first_name=update.from_user.first_name or '',
            last_name=update.from_user.last_name or '',
            username=update.from_user.username or '',
            tg_id=update.from_user.id,
            channel_id=_channel_id
        )
        await db.create_user(user)

    name = update.from_user.full_name
    if not name:
        name = update.from_user.username

    await update.approve()

    if _channel:
        msg1 = _channel['msg_1']
        msg2 = _channel['msg_2']
        msg3 = _channel['msg_3']

        if msg1:
            await send_start_message(msg1, update.from_user.id, name)
        await asyncio.sleep(60 * 1)
        if msg2:
            await send_start_message(msg2, update.from_user.id, name)
        await asyncio.sleep(60 * 1)
        usr = await db.get_user_by_tg_id(update.from_user.id)
        if not usr['notIsRobot']:
            if msg3:
                await send_start_message(msg3, update.from_user.id, name)


async def user_send_message_command(message: types.Message):
    user = await db.get_user_by_tg_id(message.from_user.id)
    channel = await db.get_channel_by_id(user['channel_id'])
    if not user['notIsRobot']:
        await db.update_user_not_is_robot(message.from_user.id)

        msg4 = channel['msg_4']
        msg5 = channel['msg_5']
        msg6 = channel['msg_6']
        msg7 = channel['msg_7']

        name = message.from_user.full_name
        if not name:
            name = message.from_user.username
        if msg4:
            await send_start_message(msg4, message.from_user.id, name, delete_kb=True)
        await asyncio.sleep(60 * 2)
        if msg5:
            await send_start_message(msg5, message.from_user.id, name, delete_kb=True)
        await asyncio.sleep(60 * 1)
        if msg6:
            await send_start_message(msg6, message.from_user.id, name)
        await asyncio.sleep(60 * 1)
        if msg7:
            await send_start_message(msg7, message.from_user.id, name)

