from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from db import database as db

import math


def kb_mass_send(buttons):
    isInline = True

    for btn in buttons:
        if btn['url'].lower() == 'кнопка':
            isInline = False
            break

    if isInline:

        kb = InlineKeyboardMarkup(row_width=1)
        
        for btn in buttons:
            kb.add(
                InlineKeyboardButton(btn['text'], url=btn['url'])
            )

        return kb

    else:
        kb = ReplyKeyboardMarkup(
            [
                [ KeyboardButton(buttons[0]['text']) ]
            ]
        )

        return kb


kb_admin = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton('Мои каналы')
        ],
        [
            KeyboardButton('Добавить канал')
        ],
        [
            KeyboardButton('Статистика')
        ],
        [
            KeyboardButton('Рассылка')
        ],
        [
            KeyboardButton('Записать лид')
        ],
    ], resize_keyboard=True
)

kb_manager = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton('Записать лид')
        ],
        [
            KeyboardButton('Статистика')
        ]
    ],
    resize_keyboard=True
)

kb_robot = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton('Я не робот!')
        ]
    ], resize_keyboard=True
)

def kb_edit_message(channel_id: int):
    _kb = InlineKeyboardMarkup(row_width=1)
    _kb.add(InlineKeyboardButton('Приветственное', callback_data=f'edit_msg_priv_{channel_id}'))
    _kb.add(InlineKeyboardButton('Взаимодействие 1', callback_data=f'edit_msg_vz1_{channel_id}'))
    _kb.add(InlineKeyboardButton('Взаимодействие 2', callback_data=f'edit_msg_vz2_{channel_id}'))
    _kb.add(InlineKeyboardButton('Подтверждение', callback_data=f'edit_msg_submit_{channel_id}'))
    _kb.add(InlineKeyboardButton('Ознакомление', callback_data=f'edit_msg_ozn_{channel_id}'))
    _kb.add(InlineKeyboardButton('Информация 1', callback_data=f'edit_msg_info1_{channel_id}'))
    _kb.add(InlineKeyboardButton('Информация 2', callback_data=f'edit_msg_info2_{channel_id}'))
    _kb.add(InlineKeyboardButton('Рассылка', callback_data=f'edit_msg_mass_{channel_id}'))
    return _kb


def kb_edit_message_userbot(channel_id: int):
    _kb = InlineKeyboardMarkup(row_width=1)
    _kb.add(InlineKeyboardButton('Приветственное', callback_data=f'edit_msg_priv_u_{channel_id}'))
    _kb.add(InlineKeyboardButton('Ознакомление', callback_data=f'edit_msg_ozn_u_{channel_id}'))
    _kb.add(InlineKeyboardButton('Информация 1', callback_data=f'edit_msg_info1_u_{channel_id}'))
    _kb.add(InlineKeyboardButton('Информация 2', callback_data=f'edit_msg_info2_u_{channel_id}'))
    return _kb


kb_approve = InlineKeyboardMarkup()
kb_approve.row(InlineKeyboardButton(text='Да', callback_data='approve_yes'),
               InlineKeyboardButton(text='Нет', callback_data='approve_no'))


kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel.add(KeyboardButton('Отмена'))


async def make_my_channels_kb(page: int):
    channel_list = await db.get_all_channels()

    max_pages = math.ceil(len(channel_list) / 10)

    if page * 10 >= len(channel_list):
        next_page = 1
    else:
        next_page = page + 1

    if page == 1:
        prew_page = math.ceil(len(channel_list) / 10)
    else:
        prew_page = page - 1


    kb = InlineKeyboardMarkup()
    for channel in channel_list[(page-1)*10:page*10+1]:
        channel_name = str(channel.get('channel_name'))[:50]
        kb.row(InlineKeyboardButton(text=channel['channel_id'], callback_data=f'channel_{page}_{channel["channel_id"]}'),
               InlineKeyboardButton(text=channel_name, callback_data=f'channel_{page}_{channel["channel_id"]}'))
    kb.row(InlineKeyboardButton(text='⬅️', callback_data=f'list_channel_page_{prew_page}'),
           InlineKeyboardButton(text='➡️', callback_data=f'list_channel_page_{next_page}'))
    return kb, max_pages


async def make_channel_menu_kb(channel_id: int, page: int):
    channel = await db.get_channel_by_id(channel_id)
    kb = InlineKeyboardMarkup(row_width=1)
    
    tie_btn = InlineKeyboardButton(text='Привязать юзербота',
                                   callback_data=f'tie_account_{page}_{channel_id}')
    account = await db.fetch_account_by_id(channel_id)
    if account:
        tie_btn = InlineKeyboardButton(text='Удалить юзербота',
                                       callback_data=f'delete_account_{page}_{channel_id}')

    kb.add(InlineKeyboardButton(text=f'Одобрить заявки ({channel.get("requests_pending")})',
                                      callback_data=f'requests_approve_{page}_{channel_id}'),

                 InlineKeyboardButton(text=f'{"Выключить" if channel.get("approve") else "Включить"} приём заявок',
                                      callback_data=f'switch_requests_approve_{page}_{channel_id}'),
                 # tie_btn,

                 InlineKeyboardButton(text='Задать название ссылки', 
                                      callback_data=f'set_link_name_{page}_{channel_id}'),

                 InlineKeyboardButton(text='Редактировать сообщения', 
                                      callback_data=f'edit_messages_{page}_{channel_id}'),

                 InlineKeyboardButton(text='Задержка',
                                      callback_data=f'set_delay_{page}_{channel_id}'),
                 InlineKeyboardButton(text='Отписка',
                                      callback_data=f'unsub_settings_{channel_id}'),
                 InlineKeyboardButton(text='Удалить канал',
                                      callback_data=f'delete_channel_{page}_{channel_id}'),
                 InlineKeyboardButton(text='🔙 Назад',
                                      callback_data=f'list_channel_page_{page}'))
    return kb


async def make_back_to_channel_menu_kb(channel_id: int, page: int):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data=f'channel_{page}_{channel_id}'))

    return kb 


async def messages_menu_kb(channel_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='Для бота', callback_data=f'bot_edit_messages_{channel_id}'),
           InlineKeyboardButton(text='Для юзер-бота', callback_data=f'userbot_edit_messages_{channel_id}'))
    return kb

retie_kb = InlineKeyboardMarkup(row_width=2)
retie_kb.add(InlineKeyboardButton(text='Да', callback_data='retie_acc_yes'),
             InlineKeyboardButton(text='Нет', callback_data='retie_acc_no'))


async def delay_menu(channel_id: int, page: int):
    delay_menu_kb = InlineKeyboardMarkup(row_width=1)
    delay_menu_kb.add(InlineKeyboardButton(text='Для бота', callback_data=f'delay_bot_{page}_{channel_id}'),
           InlineKeyboardButton(text='Для юзер-бота', callback_data=f'delay_userbot_{page}_{channel_id}'))
    return delay_menu_kb


async def clear_message_kb(channel_id: int, page: int, message_type: str):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data=f'channel_{page}_{channel_id}'),
           InlineKeyboardButton(text='🗑 Очистить', callback_data=f'clear_message_{channel_id}_{message_type}'))
    return kb


async def confirm_message_deletion(channel_id, message_type, callback):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='Удалить', callback_data=f'comfirm_message_del_{channel_id}_{message_type}'),
       InlineKeyboardButton(text='Отмена', callback_data=callback))
    return kb


async def confirm_channel_deletion(channel_id, page):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='Удалить', callback_data=f'comfirm_channel_del_{page}_{channel_id}'),
       InlineKeyboardButton(text='Отмена', callback_data=f'channel_{page}_{channel_id}'))
    return kb


async def message_delay_kb(channel_id: int, page: int, enum: str):
    kb = InlineKeyboardMarkup(row_width=2)
    msg_name_dict = {
        'msg_1': 'Приветственное',
        'msg_2': 'Взаимодействие 1',
        'msg_3': 'Взаимодействие 2',
        'msg_4': 'Подтверждение',
        'msg_5': 'Ознакомление',
        'msg_6': 'Информация 1',
        'msg_7': 'Информация 2',
        'msg_u_1': 'Приветственное',
        'msg_u_2': 'Ознакомление',
        'msg_u_3': 'Информация 1',
        'msg_u_4': 'Информация 2'
    }
    if enum == 'userbot':
        messages = await db.get_messages_userbot(channel_id)
    else:
        messages = await db.get_messages_bot(channel_id)

    for key, value in messages.items():
        kb.add(InlineKeyboardButton(text=msg_name_dict[key],
                                    callback_data=f'edit-delay-{key}-{page}-{channel_id}'),
               InlineKeyboardButton(text=str(value['delay']),
                                    callback_data=f'edit-delay-{key}-{page}-{channel_id}'))
    kb.row(InlineKeyboardButton(text='🔙 Назад', callback_data=f'channel_{page}_{channel_id}'))
    return kb


async def make_pushes_kb(channel_id: int):
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(InlineKeyboardButton(text='Добавить', callback_data=f'add_push_{channel_id}'))

    for i, _ in enumerate(await db.fetch_channel_pushes(channel_id)):
        kb.add(InlineKeyboardButton(text=f'Сообщение {i+1}', callback_data=f'view_push_{channel_id}_{i}'),
               InlineKeyboardButton(text='❌', callback_data=f'delete_push_{channel_id}_{i}'))

    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data=f'channel_1_{channel_id}'))
                 
    return kb


async def delete_push_confirm_kb(channel_id, push_id):
    kb = InlineKeyboardMarkup(row_width=2)

    kb.row(InlineKeyboardButton(text='Удалить', callback_data=f'confirm_push_deletion_{channel_id}_{push_id}'),
           InlineKeyboardButton(text='Отмена', callback_data=f'unsub_settings_{channel_id}'))

    return kb


async def back_to_pushes_kb(channel_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text='К меню отписки', callback_data=f'unsub_settings_{channel_id}'))

    return kb


async def user_push_kb(button_text, channel_id, push_index):
    kb = InlineKeyboardMarkup(row_width=1)
    for button in button_text:
        if not button['url']:
            kb.add(InlineKeyboardButton(text=button['text'], callback_data=f'next_push_{channel_id}_{push_index + 1}'))
        else:
            kb.add(InlineKeyboardButton(text=button['text'], url=button['url']))

    return kb    


def add_lead_again_kb(user_id):
    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton(text='Зафиксировать', callback_data=f'add_lead_{user_id}'))
    kb.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    return kb


lead_stats_kb = InlineKeyboardMarkup()
lead_stats_kb.add(InlineKeyboardButton(text='Выбрать дату', callback_data='lead_stats_to_calendar'))


kb_cancel_inline = InlineKeyboardMarkup(row_width=1)
kb_cancel_inline.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))