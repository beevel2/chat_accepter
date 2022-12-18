from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

import handlers.default as h
import handlers.admin as h_admin

from states import AppStates


def setup_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(h.start_command)

    dp.register_message_handler(h_admin.edit_start_message_command, commands=['edit_message'])
    dp.register_message_handler(h_admin.edit_start_message_confirm_command, state=[AppStates.STATE_EDIT_MESSAGE])
    dp.register_message_handler(h_admin.mass_send_command, commands=['mass_send'])
    dp.register_message_handler(h_admin.mass_send_process_command, content_types=['photo', 'text'], state=[AppStates.STATE_MASS_SEND_BUTTONS, AppStates.STATE_MASS_SEND_MESSAGE])
