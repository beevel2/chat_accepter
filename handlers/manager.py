from datetime import datetime, timezone
from typing import Optional, Tuple

from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram_calendar import SimpleCalendar

from settings import bot, dp
from db import models
from db import database as db
import keyboards
import states
import utils 
from states import AppStates


async def start(message: types.Message, state: FSMContext):
    await state.finish()

    await bot.send_message(chat_id=message.from_user.id,
                           text='Меню менеджера',
                           reply_markup=keyboards.kb_manager)


async def start_query(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.answer()

    await bot.send_message(chat_id=query.from_user.id,
                           text='Меню менеджера',
                           reply_markup=keyboards.kb_manager)


async def add_lead_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await state.set_state(AppStates.STATE_ADD_LEAD)

    await bot.send_message(chat_id=message.from_user.id,
                           text='Отправьте JSON-id пользователя или перешлите сообщение от него',
                           reply_markup=keyboards.kb_cancel_inline)


async def add_lead_froward_handler(message: types.Message, state: FSMContext):
    status, user = await digest_lead_input(message.forward_from.id, message.from_user.id)
    
    match status:
        case 0:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'✅ Лид по пользователю {user["first_name"]} {user["last_name"] if user["last_name"] else ""} успешно добавлен. Отправьте еще один id/пересланное сообщение', reply_markup=keyboards.kb_cancel_inline)
        case 1:
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Пользователь никогда не подписывался на данный канал, поэтому лид не может быть зафиксирован. Отправьте другой id/пересланное сообщение', reply_markup=keyboards.kb_cancel_inline)
        case 2:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'По пользователю {user["first_name"]} {user["last_name"] if user["last_name"] else ""} уже существует лид. Если вы всё равно хотите его зафиксировать - нажмите кнопку ниже. Вы так же можете отправить еще один id/пересланное сообщение',
                                   reply_markup=keyboards.add_lead_again_kb(message.forward_from.id))


async def add_lead_id_handler(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
    except:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Сообщение которое вы отправили не содержит id и не является пересланным. Отправьте другое', reply_markup=keyboards.kb_cancel_inline)
        return

    status, user = await digest_lead_input(int(user_id), message.from_user.id)
    
    match status:
        case 0:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'✅ Лид по пользователю {user["first_name"]} {user["last_name"] if user["last_name"] else ""} успешно добавлен. Отправьте еще один id/пересланное сообщение', reply_markup=keyboards.kb_cancel_inline)
        case 1:
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Пользователь никогда не подписывался на данный канал, поэтому лид не может быть зафиксирован. Отправьте другой id/пересланное сообщение', reply_markup=keyboards.kb_cancel_inline)
        case 2:
            await bot.send_message(chat_id=message.from_user.id,
                                   text='По данному пользователю уже существует лид. Если вы всё равно хотите его зафиксировать - нажмите кнопку ниже. Вы так же можете отправить еще один id/пересланное сообщение',
                                   reply_markup=keyboards.add_lead_again_kb(user_id))


async def digest_lead_input(user_id: int, manager_id: int) -> Tuple[int, Optional[dict]]:
    user = await db.get_user_by_tg_id(int(user_id))
    lead_exists = bool(await db.fetch_lead_by_user_id(int(user_id)))

    if not user:
        return 1, None
    
    if lead_exists:
        return 2, None
    
    await db.add_lead(user_id, manager_id)
    
    return 0, user


async def add_lead_anyway(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    await db.add_lead(user_id=int(query.data.split('_')[-1]), manager_id=query.from_user.id, is_first=False)

    await query.message.edit_text('Лид зафиксирован. Вы можете отправить еще одного пользователя', reply_markup=Noneards.kb_cancel_inline)


async def stats_menu(message: types.Message, state: FSMContext):
    await state.finish()
    
    lead_days, lead_hours = utils.convert_seconds_to_hours_and_days(await db.get_lead_avg_time_diff())
    total_leads = await db.fetch_lead_count()
    unique_leads = await db.fetch_lead_count({'is_first': True})
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Среднее время лида за всё время: {lead_days} дней {lead_hours} часов\n" \
                                f"Всего лидов: {total_leads}\n" \
                                f"Уникальных лидов: {unique_leads}",
                           reply_markup=keyboards.lead_stats_kb)
    

async def stats_calendar_entry(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await state.finish()
    await state.set_state(AppStates.STATE_LEAD_STATS)

    await query.message.edit_text(text='Выберите дату: ', reply_markup=await SimpleCalendar().start_calendar())


async def process_stats_calendar(query: types.CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(query, callback_data)
    if selected:
        start_day, end_day = utils.get_day_boundaries(date)
        lead_days, lead_hours = utils.convert_seconds_to_hours_and_days(await db.get_lead_avg_time_diff(start_day, end_day))
        total_leads = await db.fetch_lead_count({'lead_time': {'$gte': start_day, '$lt': end_day}})
        unique_leads = await db.fetch_lead_count({'is_first': True, 'lead_time': {'$gte': start_day, '$lt': end_day}})
        
        text = f"Среднее время лида за {date.strftime('%d.%m.%Y')}: {lead_days} дней {lead_hours} часов\n" \
               f"Лидов: {total_leads}\n" \
               f"Уникальных лидов: {unique_leads}\n"
               
        await query.message.edit_text(text=text, reply_markup=keyboards.lead_stats_kb)
