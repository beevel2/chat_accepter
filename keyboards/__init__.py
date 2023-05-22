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
            ], resize_keyboard=True
        )


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

kb_robot = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton('Я не робот!')
        ]
    ], resize_keyboard=True
)
