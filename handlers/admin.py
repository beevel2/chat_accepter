import asyncio
from typing import List, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

import db.database as db
import db.models as models
from states import AppStates
from settings import bot
import settings
import keyboards as kb
import scheduler

from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PasswordHashInvalid
from utils import download_file

import logging

clients_dicts = {}

async def start_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    
    await state.reset_state()
    await state.reset_data()

    # await db.get_btn_robot_text()

    await message.answer('Выберите команду!', reply_markup=kb.kb_admin)



async def add_account_step1_command(
    query: types.CallbackQuery,
    state: FSMContext,
):
    await query.answer()
    channel_id = int(query.data.split('_')[-1])
    page = int(query.data.split('_')[-2])
    await state.update_data(
        {
            'acc_id': channel_id
        }
    )
    markup = await kb.make_back_to_channel_menu_kb(channel_id, page)
    await state.update_data(markup=markup)
    await state.set_state(AppStates.STATE_WAIT_PROXY)
    await query.message.edit_text(text='Введите Proxy SOCKS5 в формате: ip:port:login:password.',
                                  reply_markup=markup)


async def add_account_step2_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):

    _proxy_data = message.text.split(':')

    _proxy_dict = dict(
        scheme="socks5", 
        hostname=_proxy_data[0],
        port=int(_proxy_data[1]),
        username=_proxy_data[2],
        password=_proxy_data[3]
    )
    data = await state.get_data()
    markup = data['markup']
    await state.update_data(
        {
            'proxy': _proxy_dict
        }
    )
    await state.set_state(AppStates.STATE_WAIT_PHONE)

    await message.answer('Введите номер телефона аккаунта.',
                         reply_markup=markup)



async def add_account_step3_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):

    state_data = await state.get_data()

    acc_in_db = await db.get_account_by_phone(message.text)

    if acc_in_db:
        await message.reply(f'Аккаунт с номером {message.text} - уже добавлен! Привязать его и к этому каналу?',
                            reply_markup=kb.retie_kb)
        await state.update_data(phone=message.text)
        return

    try:
        client = Client(
            f'client_{message.text}',
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            app_version=settings.APP_VERSION,
            device_model=settings.DEVICE_MODEL,
            system_version=settings.SYSTEM_VERSION,
            lang_code=settings.LANG_CODE,
            proxy=state_data['proxy'],
            workdir=settings.PYROGRAM_SESSION_PATH
        )

        await client.connect()
        sCode = await client.send_code(message.text)

        await state.update_data(
            {
                'phone': message.text,
                'phone_hash_code': sCode.phone_code_hash
            }
        )
        await state.set_state(AppStates.STATE_WAIT_AUTH_CODE)

        clients_dicts[message.from_id] = client

        markup = state_data['markup']
        await message.answer('Введите код для авторизации',
                             reply_markup=markup)
    except Exception as e:
        await message.answer('Ошибка авторизации аккаунта, проверьте данные и попробуйте ещё раз. Если все данные верны, а ошибка остается - свяжитесь с администратором')
        await message.answer(f'Ошибка: {e}')


async def retie_account(
    query: types.CallbackQuery,
    state: FSMContext):

    await query.answer()
    data = await satate.get_data()
    markup = data['markup']
    if query.data.endswith('no'):
        await state.reset_state()
        await query.message.edit_text(text='Добавление отменено, повторите действия',
                                      reply_markup=markup)
    else:
        data = await state.get_data()
        phone = data['phone']
        acc_id = data['acc_id']
        await db.retie_account(phone, acc_id)
        await state.reset_state()
        await query.message.edit_text(text='Аккаунт привязан!',
                                      reply_markup=markup)


async def add_account_step4_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    data = await state.get_data()
    await state.update_data({'code': message.text})
    await state.set_state(AppStates.STATE_WAIT_2FA)
    await message.answer('Введите пароль 2FA (Если пароль отсутствует введите 0)',
                         reply_markup = data['markup'])


async def add_account_step5_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):

    try:
        state_data = await state.get_data()
        client = clients_dicts[message.from_id]
        try:
            print('BEFORE SING_IN')
            await client.sign_in(
                state_data['phone'],
                state_data['phone_hash_code'],
                state_data['code']
            )
            print('BEFORE_2FA')
        except SessionPasswordNeeded:
            await client.check_password(message.text)
            await client.sign_in(
                state_data['phone'],
                state_data['phone_hash_code'],
                state_data['code']
            )
        me = await client.get_me()
        try:
            await client.disconnect()
        except Exception:
            print('error disconnect')
        del clients_dicts[message.from_id]
        acc_id = state_data['acc_id']
        await db.create_account(state_data['phone'], me.id, state_data['proxy'], acc_id)
        markup = state_data['markup']
        await message.reply(f'Аккаунт {acc_id} успешно авторизован.',
                            reply_markup=markup)
        await state.reset_data()
        await state.reset_state()
    except PasswordHashInvalid as e:
        state_data = await state.get_data()
        await message.answer('Ошибка авторизации аккаунта, проверьте данные и попробуйте ещё раз. Если все данные верны, а ошибка остается - свяжитесь с администратором',
            reply_markup=state_data.markup)
        await message.answer(f'Введен неверный код авторизации,пожалуйста повторите ввод.')
    except Exception as e:
        state_data = await state.get_data()
        await message.answer('Ошибка авторизации аккаунта, проверьте данные и попробуйте ещё раз. Если все данные верны, а ошибка остается - свяжитесь с администратором',
                            reply_markup=state_data.markup)
        await message.answer(f'Ошибка: {e}')
        await state.reset_data()
        await state.reset_state()


async def del_account(
    query: types.CallbackQuery,
    state: FSMContext):
    await db.del_account(int(query.data.split('_')[-1]))
    await query.answer('Аккаунт удален!')
    query.data = f'channel_{query.data.split("_")[-2]}_{query.data.split("_")[-1]}'


async def edit_start_message_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    _channel_id = message.text.split('_')[-1]
    _mes_num = message.text.split('_')[-2]
    _channel_in_db = await db.get_channel_by_id(int(_channel_id))
    if not _channel_in_db:
        await message.answer(f'Канал ID: {_channel_id} - не найден!')
        return
    if _mes_num.isdigit and int(_mes_num) in [1, 2, 3]:
        await state.set_state(AppStates.STATE_MESSAGE2_MESSAGE)
        await state.update_data({'message': int(_mes_num), 'channel_id': int(_channel_id)})
        await message.answer('Отправьте сообщение!123')


async def get_message_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool,
        album: Optional[List[types.Message]] = None
):
    if not is_admin:
        return
    data = {
        'text': '',
        'photos': [],
        'video_id': None,
        'video_note_id': None,
        'animation_id': None,
        'voice_id': None
    }
    try:
        data['text'] = message.html_text
    except Exception:
        pass
    if album:
        data['photos'] = [p.photo[-1].file_id for p in album if p.photo]
        if len(data['photos']) == 0 and len(album) == 1:
            if album[0].content_type == 'animation':
                data['animation_id'] = album[0].animation.file_id
            elif album[0].content_type == 'video':
                data['video_id'] = album[0].video.file_id
            elif album[0].content_type == 'video_note':
                data['video_note_id'] = album[0].video_note.file_id
            elif album[0].content_type == 'voice':
                data['voice_id'] = album[0].voice.file_id
    elif message.video:
        data['video_id'] = message.video.file_id
    elif message.video_note:
        data['video_note_id'] = message.video_note.file_id
    elif message.animation:
        data['animation'] = message.animation.file_id
    elif message.voice:
        data['voice_id'] = message.voice.file_id
    await state.update_data({'data': data})
    await state.set_state(AppStates.STATE_MESSAGE_BUTTONS)
    await message.answer('Введите кнопки')


async def get_buttons_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    buttons = []
    if message.text != '0':
        for s in message.text.split('\n'):
            if len(s.split('-')) < 2: continue
            _text = s.split('-')[0]
            _url = '-'.join(s.split('-')[1:])
            buttons.append({
                "text": _text.strip(),
                "url": _url.strip()
            })
    _state = await state.get_data()
    num_msg = _state['message']

    data = {
        'data': _state['data'],
        'buttons': buttons
    }

    await db.update_channel_data(_state['channel_id'], f"message_{_state['message']}", data)

    await state.reset_data()
    await state.reset_state()

    await message.answer('Сообщение принято! ✅')


async def edit_start_message_confirm_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    text = message.html_text
    await db.edit_start_message(text)
    await state.reset_state()


async def mass_send_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    _channel_id = message.text.split('_')[-1]
    _channel_in_db = await db.get_channel_by_id(int(_channel_id))
    if not _channel_in_db:
        await message.answer(f'Канал ID: {_channel_id} - не найден!')
        return
    await state.set_state(AppStates.STATE_MASS_SEND_MESSAGE)
    await state.update_data({'channel_id': int(_channel_id)})
    await message.answer('Введите сообщение для рассылки')


async def mass_send_process_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    _state = await state.get_state()
    success_send = 0
    try:
        if _state == AppStates.STATE_MASS_SEND_MESSAGE:
            _t = None
            try:
                _t = message.html_text
            except Exception:
                pass
            await state.update_data(
                {
                    "photo_id": message.photo[0].file_id if message.photo else None,
                    "video_id": message.video.file_id if message.video else None,
                    "video_note_id": message.video_note.file_id if message.video_note else None,
                    "animation_id": message.animation.file_id if message.animation else None,
                    "voice_id": message.voice.file_id if message.voice else None,
                    "text": _t
                }
            )
            text = "Введите кнопки"
            await message.answer(text)
            await state.set_state(AppStates.STATE_MASS_SEND_BUTTONS)
        elif _state == AppStates.STATE_MASS_SEND_BUTTONS:
            _state_data = await state.get_data()
            buttons = []
            if message.text != '0':
                for s in message.text.split('\n'):
                    if len(s.split('-')) < 2: continue
                    _text = s.split('-')[0]
                    _url = '-'.join(s.split('-')[1:])
                    buttons.append({
                        "text": _text.strip(),
                        "url": _url.strip()
                    })
            await message.answer('Рассылка запущена!')
            user_ids = await db.get_id_all_users(_state_data['channel_id'])
            for _user in user_ids:
                _kb = kb.kb_mass_send(buttons) if buttons else None
                try:
                    await asyncio.sleep(0.5)
                    if _state_data['photo_id']:
                        await bot.send_photo(
                            _user,
                            _state_data['photo_id'],
                            caption=_state_data['text'],
                            parse_mode=types.ParseMode.HTML,
                            reply_markup=_kb
                        )
                    elif _state_data['video_id']:
                        await bot.send_video(
                            _user,
                            _state_data['video_id'],
                            caption=_state_data['text'],
                            parse_mode=types.ParseMode.HTML,
                            reply_markup=_kb
                        )
                    elif _state_data['video_note_id']:
                        await bot.send_video_note(
                            _user,
                            _state_data['video_note_id'],
                            caption=_state_data['text'],
                            parse_mode=types.ParseMode.HTML,
                            reply_markup=_kb
                        )
                    elif _state_data['animation_id']:
                        await bot.send_animation(
                            _user,
                            _state_data['animation_id'],
                            caption=_state_data['text'],
                            parse_mode=types.ParseMode.HTML,
                            reply_markup=_kb
                        )
                    elif _state_data['voice_id']:
                        await bot.send_voice(
                            _user,
                            _state_data['voice_id'],
                            caption=_state_data['text'],
                            parse_mode=types.ParseMode.HTML,
                            reply_markup=_kb
                        )
                    else:
                        await bot.send_message(
                            _user,
                            text=_state_data['text'],
                            parse_mode=types.ParseMode.HTML,
                            reply_markup=_kb
                        )
                    success_send += 1
                except Exception as e:
                    print(f"ERROR MASS SEND: {e}")
                
            text = "Рассылка закончена"
            await message.answer(text)
            await message.answer(f"Успешно отправлено {success_send} из {len(user_ids)} сообщений")


            await state.reset_data()
            await state.reset_state()
    except Exception as e:
        print(f'ERROR MASS SEND BIG: {e}')
        await state.reset_data()
        await state.reset_state()

        await message.answer(f'ОШИБКА: {e}')


async def stats_command(
        message: types.Message,
        is_admin: bool
    ):
    if not is_admin: 
        return

    users_count = await db.get_count_users()
    await message.answer(f'Пользователей в боте: {users_count}')
    

async def add_channel_step1_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    await message.answer('Введите номер канала')
    await state.set_state(AppStates.STATE_ADD_CHANNEL_ID)


async def add_channel_step2_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return

    if not message.text.isdigit():
        await message.answer('ID канала должно быть число')
        return
    
    _channel_in_db = await db.get_channel_by_id(int(message.text))
    if _channel_in_db:
        await message.answer(f'Канал ID: {message.text} - уже существует!')
        return

    await state.update_data({'channel_id': int(message.text)})
    await message.answer('Введите JSON ID канала')
    await state.set_state(AppStates.STATE_ADD_CHANNEL_TG_ID)


async def add_channel_step3_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
        
    await state.update_data({'tg_id': message.text})


    await state.set_state(AppStates.STATE_ADD_CHANNEL_LINK_NAME)

    await bot.send_message(chat_id=message.from_user.id,
    text='Введите название ссылки(введите 0 чтобы принимать заявки по всем ссылкам):')


async def add_channel_get_link_name(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    
    await state.update_data({'link_name': message.text})

    await state.set_state(AppStates.STATE_ADD_CHANNEL_NAME)

    await bot.send_message(chat_id=message.from_user.id,
    text='Введите название канала:')


async def add_channel_get_name(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    
    await state.update_data({'name': message.text})

    await state.set_state(AppStates.STATE_ADD_CHANNEL_APPROVE)

    await bot.send_message(chat_id=message.from_user.id,
    text='Одобрять заявки на добавление?',
    reply_markup=kb.kb_approve)


async def add_channel_step4_command(
        query: types.CallbackQuery,
        state: FSMContext,
        # is_admin: bool
    ):
    # if not is_admin:
    #     return
    await query.answer()

    if query.data.endswith('yes'):
        approve = True
    else:
        approve = False

    _data = await state.get_data()
    await db.create_channel(
        models.ChannelModel(
            channel_id=_data['channel_id'],
            tg_id=_data['tg_id'],
            link_name=_data['link_name'],
            channel_name=_data['name'],
            approve=approve,
            requests_pending=0,
            requests_accepted=0)
    )
    await query.message.answer('Канал успешно добавлен ✅')
    await state.reset_data()
    await state.reset_state()


async def mass_send_btn_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await message.answer('Введите ID канала!')
    await state.set_state(AppStates.STATE_MASS_SEND_BTN)


async def mass_send_btn_step2_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    _channel_id = message.text
    _channel_in_db = await db.get_channel_by_id(int(_channel_id))
    if not _channel_in_db:
        await message.answer(f'Канал ID: {_channel_id} - не найден!')
        return
    await state.set_state(AppStates.STATE_MASS_SEND_MESSAGE)
    await state.update_data({'channel_id': int(_channel_id)})
    await message.answer('Введите сообщение для рассылки')

async def edit_timeout_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    await message.answer('Введите количество секунд задержки перед отправкой третьего сообщения!')
    await state.set_state(AppStates.STATE_CHANGE_TIMEOUT_BTN)


async def edit_timeout_step2_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    await db.update_timeout(message.text)
    await message.answer('Таймаут обновлен!')
    await state.reset_state()


# Редактирование сообщений

async def edit_messages_menu(query: types.CallbackQuery, state: FSMContext):
    channel_id = query.data.split('_')[-1]
    await query.answer()
    await query.message.edit_text(text='Для кого редактировать сообщения?',
                                  reply_markup=await kb.messages_menu_kb(channel_id))


async def edit_messages_command(
    query: types.CallbackQuery,
):
    await query.answer()
    callback_data = query.data.split('_')
    channel_id = callback_data.pop(-1)
    edit_type = query.data.split('_')[0]
    
    if edit_type == 'bot':
        _kb = kb.kb_edit_message(channel_id)
    else:
        _kb = kb.kb_edit_message_userbot(channel_id)

    await bot.send_message(chat_id=query.from_user.id,text='Выберите сообщение:', reply_markup=_kb)


async def wait_edit_channel_id_callback(
    query: types.CallbackQuery,
    state: FSMContext
):
    await query.answer()
    callback_data = query.data.split('_')
    channel_id = callback_data.pop(-1)
    callback_data = '_'.join(callback_data)
    edit_type = query.data.split('_')[-2]
    msg_type_dict = {
        'edit_msg_priv':'msg_1',
        'edit_msg_vz1':'msg_2',
        'edit_msg_vz2':'msg_3',
        'edit_msg_submit':'msg_4',
        'edit_msg_ozn':'msg_5',
        'edit_msg_info1':'msg_6',
        'edit_msg_info2':'msg_7',
        'edit_msg_mass':'msg_mass_send',
        'edit_msg_priv_u':'msg_u_1',
        'edit_msg_ozn_u':'msg_u_2',
        'edit_msg_info1_u':'msg_u_3',
        'edit_msg_info2_u':'msg_u_4',
    }

    message_type = msg_type_dict[callback_data]

    if edit_type == 'u':
        edit_type = 'userbot'
    else:
        edit_type = 'bot'

    await query.message.answer('Отправьте сообщение!', reply_markup=await kb.clear_message_kb(channel_id, 1, message_type))
    await state.set_state(AppStates.STATE_WAIT_MSG)
    await state.update_data({'callback': callback_data})
    await state.update_data({'return_callback': query.data})
    await state.update_data({'channel_id': int(channel_id)})
    await state.update_data(edit_type=edit_type)


async def clear_message(
    query: types.CallbackQuery,
    state: FSMContext
    ):
    data = await state.get_data()
    callback = data['return_callback']

    await query.answer()
    callback_data = query.data.split('_')[2:]
    channel_id = int(callback_data.pop(0))
    message_type = '_'.join(callback_data)
    channel = await db.get_channel_by_id(channel_id)
    msg = channel.get(message_type)
    if msg:
        msg = msg.get('data').get('text')
    await query.message.edit_text(text=f'Подтвердите удаление сообщения: "{msg}"',
                                  reply_markup=await kb.confirm_message_deletion(channel_id, message_type, callback))


async def clear_message_confirm(query: types.CallbackQuery):

    await query.answer()
    callback_data = query.data.split('_')[3:]
    channel_id = int(callback_data.pop(0))
    message_type = '_'.join(callback_data)
    await db.update_channel_data(channel_id, message_type, None)
    await query.message.edit_text(text='Сообщение очищено!',
                                  reply_markup=await kb.make_back_to_channel_menu_kb(channel_id, 1))


async def wait_get_message_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool,
        album: Optional[List[types.Message]] = None
):
    if not is_admin:
        return
    data = {
        'text': '',
        'photos': [],
        'video_id': None,
        'video_note_id': None,
        'animation_id': None,
        'voice_id': None
    }
    try:
        data['text'] = message.html_text
    except Exception:
        pass
    if album:
        data['photos'] = [p.photo[-1].file_id for p in album if p.photo]
        if len(data['photos']) == 0 and len(album) == 1:
            if album[0].content_type == 'animation':
                data['animation_id'] = album[0].animation.file_id
            elif album[0].content_type == 'video':
                data['video_id'] = album[0].video.file_id
            elif album[0].content_type == 'video_note':
                data['video_note_id'] = album[0].video_note.file_id
            elif album[0].content_type == 'voice':
                data['voice_id'] = album[0].voice.file_id
    elif message.video:
        data['video_id'] = message.video.file_id
    elif message.video_note:
        data['video_note_id'] = message.video_note.file_id
    elif message.animation:
        data['animation'] = message.animation.file_id
    elif message.voice:
        data['voice_id'] = message.voice.file_id
    _state = await state.get_data()
    await state.update_data({'data': data})
    if _state['callback'] == 'edit_msg_mass':
        await state.set_state(AppStates.STATE_WAIT_MSG_MASS_SEND_TIME)
        await message.answer('Введите время по МСК. (В формате hh:mm)')
    else:
        if _state['edit_type'] == 'bot':
            await state.set_state(AppStates.STATE_WAIT_MSG_BUTTON)
            await message.answer('Введите кнопки')
        else:
            message.text = '0'
            await wait_get_buttons_command(message, state, is_admin)


async def wait_get_mass_send_time_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await state.update_data({'time': message.text})
    await state.set_state(AppStates.STATE_WAIT_MSG_BUTTON)
    await message.answer('Введите кнопки')


async def wait_get_buttons_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    buttons = []
    if message.text != '0':
        for s in message.text.split('\n'):
            if len(s.split('-')) < 2: continue
            _text = s.split('-')[0]
            _url = '-'.join(s.split('-')[1:])
            buttons.append({
                "text": _text.strip(),
                "url": _url.strip()
            })
    _state = await state.get_data()

    msg_type_dict = {
        'edit_msg_priv':'msg_1',
        'edit_msg_vz1':'msg_2',
        'edit_msg_vz2':'msg_3',
        'edit_msg_submit':'msg_4',
        'edit_msg_ozn':'msg_5',
        'edit_msg_info1':'msg_6',
        'edit_msg_info2':'msg_7',
        'edit_msg_mass':'msg_mass_send',
        'edit_msg_priv_u':'msg_u_1',
        'edit_msg_ozn_u':'msg_u_2',
        'edit_msg_info1_u':'msg_u_3',
        'edit_msg_info2_u':'msg_u_4',
    }

    msg_type = msg_type_dict[_state['callback']]

    _h, _m = 0, 0

    if msg_type == 'msg_mass_send':
        _h = int(_state['time'].split(':')[0])
        _m = int(_state['time'].split(':')[1])

        _users_for_mass_send = await db.get_id_all_users(_state['channel_id'])

        schedule_data = {
            'message': {
                    "data": _state['data'],
                    "buttons": buttons
                },
            'channel_id': _state['channel_id'],
            'users': _users_for_mass_send,
            'hour': _h,
            'minutes': _m
        }

        scheduler.scheduler.add_job(
            scheduler.send_mass_messages,
            'cron',
            hour=_h,
            minute=_m,
            args=(schedule_data, )
        )

    data = {
        'data': _state['data'],
        'buttons': buttons,
        'hour': _h,
        'minutes': _m
    }

    await db.update_channel_data(_state['channel_id'], msg_type, data)

    await state.reset_data()
    await state.reset_state()

    await message.answer('Сообщение принято! ✅', reply_markup=await kb.make_back_to_channel_menu_kb(_state.get('channel_id'), 1))


async def approve_requersts_btn(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    
    if not is_admin:
        return

    await message.reply(text='Введите ID канала в котором хотите одобрить заявки:',
    reply_markup=kb.kb_cancel)
    await state.set_state(AppStates.STATE_APPROVE_REQUERSTS)


async def approve_requests_get_id(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):

    if not is_admin:
        return
    
    try:
        channel = await db.get_channel_by_id(int(message.text))
        users = await db.get_id_all_users(int(message.text))
    except ValueError:
        await message.reply('ID канала должно быть числом, попробуйте снова',
        reply_markup=kb.kb_cancel)
        return

    if not channel:
        await message.reply('Канала с таким ID не существует, попробуйте снова',
        reply_markup=kb.kb_cancel)
        return

    added = 0
    await db.purge_pending(channel['channel_id'])
    for user_id in users:
        try:
            success = await bot.approve_chat_join_request(chat_id=channel['tg_id'], user_id=user_id)
            if success is True:
                added += 1
                await db.increment_accepted(channel['channel_id'])
        except Exception as e:
            print(f'error while approving request for channel {channel.get("tg_id")} and user {user_id}; {repr(e)}')
        
    await message.reply(text=f'Одобрены {added} заявок! ✅',
                        reply_markup=kb.kb_admin)
    await state.finish()


async def cancel(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await message.reply(text='Возврат в главное меню',
                        reply_markup=kb.kb_admin)
    await state.finish()

async def approvement_settings(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    
    await message.reply(text='Введите ID канала:',
    reply_markup=kb.kb_cancel)
    await state.set_state(AppStates.STATE_APPROVEMENT_SETTINGS)


async def approvement_settings_get_id(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    
    try:
        channel = await db.get_channel_by_id(int(message.text))
    except ValueError:
        await message.reply('ID канала должно быть числом, попробуйте снова',
        reply_markup=kb.kb_cancel)
        return

    if not channel:
        await message.reply('Канала с таким ID не существует, попробуйте снова',
        reply_markup=kb.kb_cancel)
        return
    
    await state.update_data(channel_id=int(message.text))
    
    await message.reply(text=f'Настройка приёма заявок для канала {message.text}. Принимать заявки?',
                        reply_markup=kb.kb_approve)


async def approvement_settings_query(
    query: types.CallbackQuery,
    state: FSMContext,
    # is_admin: bool
):
    # if not is_admin:
    #     return
    
    data = await state.get_data()
    channel_id = data.get('channel_id')
    if not channel_id:
        await query.answer('Используйте актуальные кнопки')
        return
    await query.answer()

    if query.data.endswith('yes'):
        approve=True
    else:
        approve=False

    await db.update_channel_data(channel_id, 'approve', approve)

    if approve is True:
        text = 'БУДЕТ'
    else:
        text = 'НЕ БУДЕТ'
    await query.message.reply(text=f'Теперь канал {channel_id} {text} принимать заявки',
                              reply_markup=kb.kb_admin)
    await state.reset_state()


async def my_channels(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    markup, max_pages = await kb.make_my_channels_kb(1)

    await message.reply(text=f'Список всех каналов стр. 1/{max_pages}:',
                        reply_markup=markup)


async def my_channels_page(
    query: types.CallbackQuery,
    state: FSMContext,
):

    markup, max_pages = await kb.make_my_channels_kb(1)

    try:
        await query.answer()
    except:
        pass
    try:
        await query.message.edit_text(text=f'Список всех каналов стр. 1/{max_pages}:',
                                    reply_markup=markup)
    except MessageNotModified:
        pass


async def channel_menu(query: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.reset_data()
    try:
        await query.answer()
    except Exception as e:
        logging.exception(msg='biba')
    channel = await db.get_channel_by_id(int(query.data.split('_')[-1]))
    page = int(query.data.split('_')[-2])
    text = f"{channel.get('channel_id')} | {channel.get('channel_name')}\n" \
           f"Активных заявок: {channel.get('requests_pending')}\n" \
           f"Одобрено заявок: {channel.get('requests_accepted')}\n" \
           f"Одобрять заявки? - {'Да' if channel.get('approve') else 'Нет'}\n" \
           f"Привязанная ссылка: {'Нет' if channel['link_name'] == '0' else channel['link_name']}"
    try:
        await query.message.edit_text(text=text,
                                  reply_markup=await kb.make_channel_menu_kb(channel['channel_id'], page))
    except MessageNotModified:
        pass

async def approve_requests(query: types.CallbackQuery, state: FSMContext):
    channel_id = int(query.data.split('_')[-1])
    page = int(query.data.split('_')[-2])
    channel = await db.get_channel_by_id(channel_id)
    users = await db.get_id_all_users(channel_id)

    added = 0
    await db.purge_pending(channel['channel_id'])
    for user_id in users:
        try:
            success = await bot.approve_chat_join_request(chat_id=channel['tg_id'], user_id=user_id)
            if success is True:
                added += 1
                await db.increment_accepted(channel['channel_id'])
        except Exception as e:
            print(f'error while approving request for channel {channel.get("tg_id")} and user {user_id}; {repr(e)}')
        
    await query.answer(f'Одобрены {added} заявок! ✅')
    query.data = f'channel_{page}_{channel_id}'
    await channel_menu(query, state)


async def switch_approvement(query: types.CallbackQuery, state: FSMContext):
    channel_id = int(query.data.split('_')[-1])
    page = int(query.data.split('_')[-2])

    await db.switch_approvement_settings(channel_id)
    await query.answer('Настройка изменена')
    
    query.data = f'channel_{page}_{channel_id}'
    await channel_menu(query, state)


async def change_link_name(query: types.CallbackQuery, state: FSMContext):
    page = int(query.data.split('_')[-2])
    channel_id = int(query.data.split('_')[-1])
    # await state.update_data({'page': page, 'channel_id': channel_id})
    await state.update_data(page=page)
    await state.update_data(channel_id=channel_id)
    await query.answer()
    await query.message.edit_text(text='Введите название ссылки (или 0 чтобы принимать заявки по всем ссылкам)',
                                  reply_markup=await kb.make_back_to_channel_menu_kb(channel_id, page))
    await state.set_state(AppStates.STATE_GET_LINK)


async def change_link_name_get(message: types.Message, state: FSMContext):
    data = await state.get_data()
    page = data['page']
    channel_id = data['channel_id']
    markup = await kb.make_back_to_channel_menu_kb(channel_id, page)

    if message.text == '0':
        text = 'Бот будет принимать заявки по всем ссылкам'
    else:
        text = f'Название ссылки по которой будут приниматься заявки изменено на "{message.text}"'

    await db.change_link_name(channel_id, message.text)
    await bot.send_message(chat_id=message.chat.id,
                           text=text,
                           reply_markup=markup)
    await state.reset_state()
    await state.reset_data()


async def set_delay_menu(
    query: types.CallbackQuery,
    state: FSMContext
    ):
    await query.answer()

    callback_data = query.data.split('_')
    page = callback_data[-2]
    channel_id = callback_data[-1]

    markup = await kb.delay_menu(channel_id, page)
    await query.message.edit_text(text='Для кого редактировать задержку?', 
                                  reply_markup=markup)


async def set_delay(
    query: types.CallbackQuery,
    state: FSMContext
    ):
    await query.answer()

    callback_data = query.data.split('_')
    page = callback_data[-2]
    channel_id = callback_data[-1]
    delay_key = callback_data[-3]

    await query.message.edit_text('Введите задержку в секундах:',
                                  reply_markup=await kb.make_back_to_channel_menu_kb(channel_id, page))

    await state.set_state(AppStates.STATE_GET_DELAY)
    await state.update_data(page=page, channel_id=channel_id, delay_key=delay_key)


async def set_delay_get_message(
    message: types.Message,
    state: FSMContext,
    ):
    data = await state.get_data()
    page = data['page']
    channel_id = data['channel_id']
    delay_key = data['delay_key']    

    markup = await kb.make_back_to_channel_menu_kb(channel_id, page)

    try:
        delay = int(message.text)
    except ValueError:
        await message.reply(text='Задержка должна быть числом (в секундах)',
                            reply_markup=markup)
        return

    await db.set_delay(int(channel_id), delay, delay_key)
    await message.answer(text=f'Задержка на {channel_id} канале для {delay_key} теперь {delay} секунд',
                         reply_markup=markup)
    await state.reset_state()
    await state.reset_data()


async def delete_channel(query: types.CallbackQuery):
    await query.answer()
    data = query.data.split('_')
    channel_id = int(data[-1])
    page = int(data[-2])
    channel = await db.get_channel_by_id(channel_id)
    await query.message.edit_text(text=f'Вы уверены в удалении канала \"{channel.get("channel_name")}\". Все данные об этом канале будут безвозвратно ',
                                  reply_markup=await kb.confirm_channel_deletion(channel_id, page))

async def delete_channel_confirm(query: types.CallbackQuery, state: FSMContext):
    await query.answer('Канал удален')
    data = query.data.split('_')
    channel_id = int(data[-1])
    page = int(data[-2])
    await db.delete_channel(channel_id)
    query.data = f'list_channel_page_{page}'
    await my_channels_page(query, state)
