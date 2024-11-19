import asyncio
from pathlib import Path
import logging

import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from pyrogram import types as pt

import db.database as db
import db.models as models

from states import AppStates

from settings import bot
from utils import replace_in_message
import keyboards as kb
    
from pyrogram import Client
import settings
import io

client_pool = []

logger = logging.getLogger(__name__)


async def send_start_message(msg, chat_id, user_record=None, delete_kb=False, msg_type='default', push_index=None, live=True):
    logger.info(f'entered with params: msg={msg} | chat_id={chat_id} | user_record={user_record} | delete_kb={delete_kb} | msg_type={msg_type} | push_index={push_index} live={live}')

    if not msg:

        if live is True:
            logger.warning(f'Message COMPLETELY is empty! msg={msg}, chat_id={chat_id}, user_record={user_record}, delete_kb={delete_kb}, msg_type={msg_type}, push_index={push_index}, live={live}')
        else:
            await bot.send_message(chat_id=chat_id, text='*пустое сообщение*')
        return 1
    
    data_keys = ['text', 'video_id', 'photos', 'video_note_id', 'voice_id', 'animation_id']
    if not any([msg['data'].get(key) for key in data_keys]):
        if live is True:
            logger.warning(f'Message is empty! msg={msg}, chat_id={chat_id}, user_record={user_record}, delete_kb={delete_kb}, msg_type={msg_type}, push_index={push_index}, live={live}')
        else:
            await bot.send_message(chat_id=chat_id, text='*пустое сообщение*')

        return 2
    
    if delete_kb:
        _kb = kb.ReplyKeyboardRemove()
    elif msg_type == 'default':
        _kb = kb.kb_mass_send(msg['buttons'])
    elif msg_type == 'push':
        if live is True:
            _kb = await kb.user_push_kb(msg['data']['button_text'], msg['channel_id'], push_index)
        else:
            _kb = await kb.user_push_mock_kb(msg['data']['button_text'])
    if msg['data']['text']:
        if user_record:
            _text = msg['data']['text'].replace('[NAME]', user_record['first_name']).replace('[SURNAME]', user_record['last_name']).replace('[USERNAME]', user_record['username']) 
        else:
            _text = msg['data']['text']
    else:
        _text = ''

    if msg['data']['video_note_id']:
        await bot.send_video_note(chat_id=chat_id, video_note=msg['data']['video_note_id'].split('.')[0], reply_markup=_kb)
    elif msg['data']['photos'] and len(msg['data']['photos']) == 1 and not msg['data']['video_id']:
        if _text:
            await bot.send_photo(chat_id=chat_id, photo=msg['data']['photos'][0].split('.')[0], caption=_text, parse_mode=types.ParseMode.HTML, reply_markup=_kb)
        else:
            await bot.send_photo(chat_id=chat_id, photo=msg['data']['photos'][0].split('.')[0], parse_mode=types.ParseMode.HTML, reply_markup=_kb)
    elif msg['data']['video_id'] and not msg['data']['photos']:
        if _text:
            await bot.send_video(chat_id=chat_id, video=msg['data']['video_id'], parse_mode=types.ParseMode.HTML, caption=_text, reply_markup=_kb)
        else:
            await bot.send_video(chat_id=chat_id, video=msg['data']['video_id'], parse_mode=types.ParseMode.HTML, reply_markup=_kb)


    elif msg['data']['photos'] or msg['data']['video_id']:
        media = types.MediaGroup()
        if msg['data']['photos']:
            for _i, p in enumerate(msg['data']['photos']):
                if _i == 0 and _text:
                    media.attach_photo(photo=p.split('.')[0], caption=_text, parse_mode=types.ParseMode.HTML)
                else:
                    media.attach_photo(photo=p.split('.')[0])
        if msg['data']['video_id']:
            media.attach_video(msg['data']['video_id'])
        await bot.send_media_group(chat_id, media=media)

        if msg_type == 'push':
            await bot.send_message(chat_id, text=_text or '.', reply_markup=_kb)
    elif msg['data']['animation_id']:
        if _text:
            await bot.send_animation(chat_id=chat_id, animation=msg['data']['animation_id'].split('.')[0], caption=_text, parse_mode=types.ParseMode.HTML, reply_markup=_kb)
        else:
            await bot.send_animation(chat_id=chat_id, animation=msg['data']['animation_id'].split('.')[0], reply_markup=_kb)
    elif msg['data']['voice_id']:
        if _text:
            await bot.send_voice(chat_id=chat_id, voice=msg['data']['voice_id'].split('.')[0], caption=_text, parse_mode=types.ParseMode.HTML, reply_markup=_kb)
        else:
            await bot.send_voice(chat_id=chat_id, voice=msg['data']['voice_id'].split('.')[0], reply_markup=_kb)
    elif _text:
        await bot.send_message(chat_id, text=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)

    if msg_type == "push" and live is True:
        for btn in msg['data']['button_text']:
            if btn['url'] == None:
                break
        else:
            pushes = await db.fetch_channel_pushes(msg['channel_id'])
            await asyncio.sleep(30)
            await send_start_message(pushes[push_index+1], chat_id, user_record, delete_kb=False, msg_type='push', push_index=push_index+1)



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
    
    user = await db.get_user(update.from_user.id, _channel_id)

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

        # asyncio.create_task(send_userbot_messages(update.from_user.id, _channel, name))
        if msg1:
            await asyncio.sleep(msg1['delay'])
            await send_start_message(msg1, update.from_user.id, user)
        if msg2:
            await asyncio.sleep(msg2['delay']) 
            await send_start_message(msg2, update.from_user.id, user)
        if msg3:
            await asyncio.sleep(msg3['delay'])
            usr = await db.get_user_by_tg_id(update.from_user.id)
            if not usr.get('notIsRobot'):
                await send_start_message(msg3, update.from_user.id, user)


async def user_send_message_command(message: types.Message):
    user = await db.get_user_by_tg_id(message.from_user.id)
    channel = await db.get_channel_by_id(user['channel_id'])
    if not user.get('notIsRobot'):
        await db.update_user_not_is_robot(message.from_user.id)

        msg4 = channel.get('msg_4')
        msg5 = channel.get('msg_5')
        msg6 = channel.get('msg_6')
        msg7 = channel.get('msg_7')

        if msg4:
            await asyncio.sleep(msg4['delay'])
            await send_start_message(msg4, message.from_user.id, user, delete_kb=True)
        if msg5:
            await asyncio.sleep(msg5['delay'])
            await send_start_message(msg5, message.from_user.id, user)
        if msg6:
            await asyncio.sleep(msg6['delay'])
            await send_start_message(msg6, message.from_user.id, user)
        if msg7:
            await asyncio.sleep(msg7['delay'])
            await send_start_message(msg7, message.from_user.id, user)


async def send_userbot_messages(user_id: int, channel, name):
    return
    global client_pool
    account = await db.fetch_account_by_id(int(channel['channel_id']))
    if not account:
        return

    app = None
    for client in client_pool:
        if client['name'] == f'client_{account["phone"]}':
            app = client['app']
    if not app:
        app = Client(
            f'client_{account["phone"]}',
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            app_version=settings.APP_VERSION,
            device_model=settings.DEVICE_MODEL,
            system_version=settings.SYSTEM_VERSION,
            lang_code=settings.LANG_CODE,
            proxy=account["proxy"],
            workdir=settings.PYROGRAM_SESSION_PATH
        )
        await app.start()
        client_pool.append({"name": f'client_{account["phone"]}', 'app': app})
    
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
    _text = msg['data']['text'].replace('USER', name) 
    if msg['data']['video_note_id']:
        await app.send_video_note(chat_id=chat_id, video_note=Path(settings.DOWNLOAD_PATH, msg['data']['video_note_id']))
    elif msg['data']['photos'] and len(msg['data']['photos']) == 1:
        if _text:
            await app.send_photo(chat_id=chat_id, photo=Path(settings.DOWNLOAD_PATH, msg['data']['photos'][0]), caption=_text)
        else:
            await app.send_photo(chat_id=chat_id, photo=Path(settings.DOWNLOAD_PATH, msg['data']['photos'][0]))
    elif msg['data']['photos'] or msg['data']['video_id']:
        media = []
        if msg['data']['photos']:
            for _i, p in enumerate(msg['data']['photos']):
                if _i == 0 and _text:
                    media.append(pt.InputMediaPhoto(media=Path(settings.DOWNLOAD_PATH, p), caption=_text))
                else:
                    media.append(pt.InputMediaPhoto(media=Path(settings.DOWNLOAD_PATH, p)))
        if msg['data']['video_id']:
            media.append(pt.InputMediaVideo(media=Path(settings.DOWNLOAD_PATH, msg['data']['video_id'])))
        await app.send_media_group(chat_id, media=media)
    elif msg['data']['animation_id']:
        if _text:
            await app.send_animation(chat_id=chat_id, animation=Path(settings.DOWNLOAD_PATH, msg['data']['animation_id']), caption=_text)
        else:
            await app.send_animation(chat_id=chat_id, animation=Path(settings.DOWNLOAD_PATH, msg['data']['animation_id']))
    elif msg['data']['voice_id']:
        if _text:
            await app.send_voice(chat_id=chat_id, voice=Path(settings.DOWNLOAD_PATH, msg['data']['voice_id']), caption=_text)
        else:
            await app.send_voice(chat_id=chat_id, voice=Path(settings.DOWNLOAD_PATH, msg['data']['voice_id']))
    elif _text:
        await app.send_message(chat_id, text=_text)


async def banned_handler(member: types.ChatMemberUpdated):
    status = True if member.new_chat_member.status == 'kicked' else False
    await db.update_user_banned(member.from_user.id, status)


async def unsub_handler(chat_member: types.ChatMemberUpdated):
    # breakpoint()
    # print(dict(chat_member))
    # chat_member.new_chat_member.status == 'left'
    if not (chat_member.new_chat_member.status == 'left'):
        return


    user_id = chat_member.from_user.id
    channel_tg_id = chat_member.chat.id

    channel = await db.get_channel_by_tg_id(channel_tg_id)

    user = await db.get_user(user_id, int(channel['channel_id']))

    pushes = await db.fetch_channel_pushes(channel['channel_id'])

    await send_start_message(pushes[0], user_id, user, delete_kb=False, msg_type='push', push_index=0)


async def next_push_handler(query: types.CallbackQuery):
    await query.answer()
    channel_id = int(query.data.split('_')[-2])
    push_index = int(query.data.split('_')[-1])

    user = await db.get_user(query.from_user.id, int(channel_id))

    pushes = await db.fetch_channel_pushes(channel_id)

    try:
        await send_start_message(pushes[push_index], query.from_user.id, user, delete_kb=False, msg_type='push', push_index=push_index)
    except IndexError:
        print(f'Ran out of pushes on channel {channel_id} at push_index={push_index}')
