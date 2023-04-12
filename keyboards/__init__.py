from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def kb_mass_send(buttons):
    kb = InlineKeyboardMarkup(row_width=1)
    
    for btn in buttons:
        kb.add(
            InlineKeyboardButton(btn['text'], url=btn['url'])
        )

    return kb


kb_admin = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton('Добавить канал')
        ],
        [
            KeyboardButton('Изменить сообщение')
        ],
        [
            KeyboardButton('Рассылка')
        ],
        [
            KeyboardButton('Изменить таймаут отправки сообщения')
        ]
    ], resize_keyboard=True
)
