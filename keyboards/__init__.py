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
        # [
        #     KeyboardButton('Изменить сообщение')
        # ],
        [
            KeyboardButton('Рассылка')
        ],
        [
            KeyboardButton('Изменить таймаут отправки сообщения')
        ],
        # [
        #     KeyboardButton('Редактировать сообщения')
        # ],
        # [
        #     KeyboardButton('Приём заявок')
        # ],
        # [
        #     KeyboardButton('Одобрить заявки')

        # ]
    ], resize_keyboard=True
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
    kb.add(InlineKeyboardButton(text=f'Одобрить заявки ({channel.get("requests_pending")})',
                                      callback_data=f'requests_approve_{page}_{channel_id}'),

                 InlineKeyboardButton(text=f'{"Выключить" if channel.get("approve") else "Включить"} приём заявок',
                                      callback_data=f'switch_requests_approve_{page}_{channel_id}'),

                 InlineKeyboardButton(text='Привязать юзербота',
                                      callback_data=f'tie_account_{page}_{channel_id}'),

                 InlineKeyboardButton(text='Удалить юзербота',
                                      callback_data=f'delete_account_{page}_{channel_id}'),

                 InlineKeyboardButton(text='Задать название ссылки', 
                                      callback_data=f'set_link_name_{page}_{channel_id}'),

                 InlineKeyboardButton(text='Редактировать сообщения', 
                                      callback_data=f'edit_messages_{page}_{channel_id}'),

                 InlineKeyboardButton(text='Задержка',
                                      callback_data=f'set_delay_{page}_{channel_id}'),
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