import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
import db.models as models
from states import AppStates
from settings import bot
import keyboards as kb


async def edit_start_message1_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    await state.set_state(AppStates.STATE_MESSAGE1_VIDEO)
    await state.set_data({'message': 1})
    await message.answer('Отправьте видео сообщение!')


async def get_video_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
):
    if not is_admin:
        return
    await state.update_data({'file_id': message.video_note.file_id})
    await state.set_state(AppStates.STATE_MESSAGE_BUTTONS)
    await message.answer('Введите кнопки')


async def edit_start_message2_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    await state.set_state(AppStates.STATE_MESSAGE2_MESSAGE)
    await state.set_data({'message': 2})
    await message.answer('Отправьте сообщение!')


async def edit_start_message3_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    await state.set_state(AppStates.STATE_MESSAGE3_MESSAGE)
    await state.set_data({'message': 3})
    await message.answer('Отправьте сообщение!')


async def get_message_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
):
    if not is_admin:
        return
    data = {
        'text': '',
        'photos': [],
        'video_id': None,
        'video_note_id': None
    }
    try:
        data['text'] = message.html_text
    except Exception:
        pass
    if message.photo:
        data['photos'] = [p.file_id for p in message.photo]
    elif message.video:
        data.video_id = message.video.file_id
    elif message.video_note:
        data.video_note_id = message.video_note.file_id
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
    if num_msg == 1:
        data = {
            'file_id': _state['file_id'],
            'buttons': buttons
        }
        await db.edit_message('start_message_1', data)
    elif num_msg == 2:
        data = {
            'data': _state['data'],
            'buttons': buttons
        }
        await db.edit_message('start_message_2', data)

    else:
        data = {
            'data': _state['data'],
            'buttons': buttons
        }
        await db.edit_message('start_message_3', data)

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
    await state.set_state(AppStates.STATE_MASS_SEND_MESSAGE)
    await message.answer('Введите сообщение для рассылки')


async def mass_send_process_command(
        message: types.Message,
        state: FSMContext,
        is_admin: bool
    ):
    if not is_admin:
        return
    _state = await state.get_state()
    try:
        if _state == AppStates.STATE_MASS_SEND_MESSAGE:
            await state.set_data(
                {
                    "photo_id": message.photo[0].file_id if message.photo else None,
                    "text": message.html_text
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
            
            user_ids = await db.get_id_all_users()
            for _user in user_ids:
                _kb = kb.kb_mass_send(buttons) if buttons else None
                try:
                    if _state_data['photo_id']:
                        await bot.send_photo(
                            _user,
                            _state_data['photo_id'],
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
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"ОШИБКА MASS SEND: {e}")
                
            text = "Рассылка закончена"
            await message.answer(text)


            await state.reset_data()
            await state.reset_state()
    except Exception:
        await state.reset_data()
        await state.reset_state()


async def stats_command(
        message: types.Message,
        is_admin: bool
    ):
    if not is_admin: 
        return

    users_count = await db.get_count_users()
    await message.answer(f'Пользователей в боте: {users_count}')
    