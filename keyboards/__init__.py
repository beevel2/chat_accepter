from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


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
        [
            KeyboardButton('Редактировать сообщения')
        ]
    ], resize_keyboard=True
)

kb_robot = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton('Я не робот!')
        ]
    ], resize_keyboard=True
)

def kb_edit_message():
    _kb = InlineKeyboardMarkup(row_width=1)
    _kb.add(InlineKeyboardButton('Приветственное', callback_data='edit_msg_priv'))
    _kb.add(InlineKeyboardButton('Взаимодействие 1', callback_data='edit_msg_vz1'))
    _kb.add(InlineKeyboardButton('Взаимодействие 2', callback_data='edit_msg_vz2'))
    _kb.add(InlineKeyboardButton('Подтверждение', callback_data='edit_msg_submit'))
    _kb.add(InlineKeyboardButton('Ознакомление', callback_data='edit_msg_ozn'))
    _kb.add(InlineKeyboardButton('Информация 1', callback_data='edit_msg_info1'))
    _kb.add(InlineKeyboardButton('Информация 2', callback_data='edit_msg_info2'))
    _kb.add(InlineKeyboardButton('Рассылка', callback_data='edit_msg_mass'))
    return _kb
