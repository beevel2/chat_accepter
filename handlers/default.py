import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
import db.models as models

from states import AppStates

from settings import bot
from utils import replace_in_message
import keyboards as kb

from pyrogram import Client
import settings

async def send_start_message(msg, chat_id, name, delete_kb=False):
    if delete_kb:
        _kb = kb.ReplyKeyboardRemove()
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
    _channel = await db.get_channel_by_tg_id(update.chat.id)
    if _channel:
        _channel_id = _channel['channel_id']
    else:
        return
    user_in_db = await db.get_user(update.from_user.id, _channel_id)
    if not user_in_db:
        user = models.UserModel(
            first_name=update.from_user.first_name or '',
            last_name=update.from_user.last_name or '',
            username=update.from_user.username or '',
            tg_id=update.from_user.id,
            channel_id=_channel_id,
        )
        await db.create_user(user)

    name = update.from_user.full_name
    if not name:
        name = update.from_user.username

    if _channel:
        link_name = _channel['link_name']
        if str(link_name) == '0' or str(link_name) == update.invite_link.name:
            if _channel['approve'] is True:
                await update.approve()
                await db.increment_accepted(_channel_id)
            else:
                await db.increment_pending(_channel_id)
        else:
            await db.increment_pending(_channel_id)

    if _channel:
        msg1 = _channel.get('msg_1')
        msg2 = _channel.get('msg_2')
        msg3 = _channel.get('msg_3')

        asyncio.create_task(send_userbot_messages(update.from_user.id, _channel, name))
        if msg1:
            await asyncio.sleep(msg1['delay'])
            await send_start_message(msg1, update.from_user.id, name)
        if msg2:
            await asyncio.sleep(msg2['delay']) 
            await send_start_message(msg2, update.from_user.id, name)
        usr = await db.get_user_by_tg_id(update.from_user.id)
        if not usr.get('notIsRobot'):
            if msg3:
                await asyncio.sleep(msg3['delay'])
                await send_start_message(msg3, update.from_user.id, name)


async def user_send_message_command(message: types.Message):
    user = await db.get_user_by_tg_id(message.from_user.id)
    channel = await db.get_channel_by_id(user['channel_id'])
    if not user.get('notIsRobot'):
        await db.update_user_not_is_robot(message.from_user.id)

        msg4 = channel.get('msg_4')
        msg5 = channel.get('msg_5')
        msg6 = channel.get('msg_6')
        msg7 = channel.get('msg_7')

        name = message.from_user.full_name
        if not name:
            name = message.from_user.username

        if msg4:
            await asyncio.sleep(msg4['delay'])
            await send_start_message(msg4, message.from_user.id, name, delete_kb=True)
        if msg5:
            await asyncio.sleep(msg5['delay'])
            await send_start_message(msg5, message.from_user.id, name)
        if msg6:
            await asyncio.sleep(msg6['delay'])
            await send_start_message(msg6, message.from_user.id, name)
        if msg7:
            await asyncio.sleep(msg7['delay'])
            await send_start_message(msg7, message.from_user.id, name)


async def send_userbot_messages(user_id: int, channel, name):
    account = await db.fetch_account_by_id(int(channel['channel_id']))
    print(account)
    if not account:
        return

    async with Client(f'client_{account["phone"]}', workdir=settings.PYROGRAM_SESSION_PATH) as app:
    
        requests = app.get_chat_join_requests(channel['tg_id'])
        async for request in requests:
            pass
        async for member in app.get_chat_members(channel['tg_id']):
            pass
        if channel.get('msg_u_1'):
            await asyncio.sleep(channel['msg_u_1']['delay'])
            await send_admin_message(channel['msg_u_1'], user_id, name, app)

        if channel.get('msg_u_2'):
            await asyncio.sleep(channel['msg_u_2']['delay'])
            await send_admin_message(channel['msg_u_2'], user_id, name, app)
        
        if channel.get('msg_u_3'):
            await asyncio.sleep(channel['msg_u_3']['delay'])
            await send_admin_message(channel['msg_u_3'], user_id, name, app)

        if channel.get('msg_u_4'):
            await asyncio.sleep(channel['msg_u_4']['delay'])
            await send_admin_message(channel['msg_u_4'], user_id, name, app)


async def send_admin_message(msg, chat_id, name, app, delete_kb=False):
    _text = replace_in_message(msg['data']['text'], 'USER', name) 
    if msg['data']['video_note_id']:
        await app.send_video_note(chat_id=chat_id, video_note=msg['data']['video_note_id'])
    elif msg['data']['photos'] and len(msg['data']['photos']) == 1:
        if _text:
            await app.send_photo(chat_id=chat_id, photo=msg['data']['photos'][0], caption=_text)
        else:
            await app.send_photo(chat_id=chat_id, photo=msg['data']['photos'][0])
    elif msg['data']['photos'] or msg['data']['video_id']:
        media = types.MediaGroup()
        if msg['data']['photos']:
            for _i, p in enumerate(msg['data']['photos']):
                if _i == 0 and _text:
                    media.attach_photo(photo=p, caption=_text)
                else:
                    media.attach_photo(photo=p)
        if msg['data']['video_id']:
            media.attach_video(msg['data']['video_id'])
        await app.send_media_group(chat_id, media=media)
    elif msg['data']['animation_id']:
        if _text:
            await app.send_animation(chat_id=chat_id, animation=msg['data']['animation_id'], caption=_text)
        else:
            await app.send_animation(chat_id=chat_id, animation=msg['data']['animation_id'])
    elif msg['data']['voice_id']:
        if _text:
            await app.send_voice(chat_id=chat_id, voice=msg['data']['voice_id'], caption=_text)
        else:
            await app.send_voice(chat_id=chat_id, voice=msg['data']['voice_id'])
    elif _text:
        await app.send_message(chat_id, text=_text)


async def banned_handler(member: types.ChatMemberUpdated):
    status = True if member.new_chat_member.status == 'kicked' else False
    await db.update_user_banned(member.from_user.id, status)
