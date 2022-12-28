import asyncio
from typing import List, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
import db.models as models
from states import AppStates
from settings import bot
import keyboards as kb


# async def edit_start_message1_command(
#         message: types.Message,
#         state: FSMContext,
#         is_admin: bool
#     ):
#     if not is_admin:
#         return
#     _channel_id = message.text.split('_')[-1]
#     _channel_in_db = await db.get_channel_by_id(int(_channel_id))
#     if not _channel_in_db:
#         await message.answer(f'Канал ID: {_channel_id} - не найден!')
#         return
#     await state.set_state(AppStates.STATE_MESSAGE1_VIDEO)
#     await state.set_data({'message': 1, 'channel_id': int(_channel_id)})
#     await message.answer('Отправьте видео сообщение!')


# async def get_video_command(
#         message: types.Message,
#         state: FSMContext,
#         is_admin: bool
# ):
#     if not is_admin:
#         return
#     await state.update_data({'file_id': message.video_note.file_id})
#     await state.set_state(AppStates.STATE_MESSAGE_BUTTONS)
#     await message.answer('Введите кнопки')


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
        await state.set_data({'message': int(_mes_num), 'channel_id': int(_channel_id)})
        await message.answer('Отправьте сообщение!')


# async def edit_start_message3_command(
#         message: types.Message,
#         state: FSMContext,
#         is_admin: bool
#     ):
#     if not is_admin:
#         return
#     _channel_id = message.text.split('_')[-1]
#     _channel_in_db = await db.get_channel_by_id(int(_channel_id))
#     if not _channel_in_db:
#         await message.answer(f'Канал ID: {_channel_id} - не найден!')
#         return
#     await state.set_state(AppStates.STATE_MESSAGE3_MESSAGE)
#     await state.set_data({'message': 3, 'channel_id': int(_channel_id)})
#     await message.answer('Отправьте сообщение!')


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

    # if num_msg == 1:
    #     data = {
    #         'file_id': _state['file_id'],
    #         'buttons': buttons
    #     }
    #     await db.edit_message('start_message_1', data)
    #     await db.update_channel_data(_state['channel_id'], 'message_1', data)
    # elif num_msg == 2:
    #     data = {
    #         'data': _state['data'],
    #         'buttons': buttons
    #     }
    #     await db.edit_message('start_message_2', data)
    #     await db.update_channel_data(_state['channel_id'], 'message_2', data)

    # else:
    #     data = {
    #         'data': _state['data'],
    #         'buttons': buttons
    #     }
    #     await db.edit_message('start_message_3', data)
    #     await db.update_channel_data(_state['channel_id'], 'message_3', data)

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
    await state.set_data({'channel_id': int(_channel_id)})
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
            await state.update_data(
                {
                    "photo_id": message.photo[0].file_id if message.photo else None,
                    "video_id": message.video.file_id if message.video else None,
                    "video_note_id": message.video_note.file_id if message.video_note else None,
                    "animation_id": message.animation.file_id if message.animation else None,
                    "voice_id": message.voice.file_id if message.voice else None,
                    "text": message.html_text if message.text else None
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

    await state.set_data({'channel_id': int(message.text)})
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
    await message.answer('Введите название ссылки')
    await state.set_state(AppStates.STATE_ADD_CHANNEL_LINK_NAME)


async def add_channel_step4_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    
    _data = await state.get_data()
    await db.create_channel(
        models.ChannelModel(
            channel_id=_data['channel_id'],
            tg_id=_data['tg_id'],
            link_name=message.text
        )
    )
    await message.answer('Канал успешно добавлен ✅')
    await state.reset_data()
    await state.reset_state()
