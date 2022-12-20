from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

import handlers.default as h
import handlers.admin as h_admin

from states import AppStates


def setup_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(h.start_command)

    dp.register_message_handler(h_admin.edit_start_message1_command, commands=['edit_message_1'])
    dp.register_message_handler(h_admin.edit_start_message2_command, commands=['edit_message_2'])
    dp.register_message_handler(h_admin.edit_start_message3_command, commands=['edit_message_3'])
    dp.register_message_handler(h_admin.get_video_command, content_types=['video_note'], state=[AppStates.STATE_MESSAGE1_VIDEO])
    dp.register_message_handler(h_admin.get_message_command, content_types=['any'], state=[AppStates.STATE_MESSAGE2_MESSAGE, AppStates.STATE_MESSAGE3_MESSAGE])
    dp.register_message_handler(h_admin.get_buttons_command, state=[AppStates.STATE_MESSAGE_BUTTONS])
    
    dp.register_message_handler(h_admin.mass_send_command, commands=['mass_send'])
    dp.register_message_handler(h_admin.mass_send_process_command, content_types=['photo', 'text'], state=[AppStates.STATE_MASS_SEND_BUTTONS, AppStates.STATE_MASS_SEND_MESSAGE])
    dp.register_message_handler(h_admin.stats_command, commands=['stats'])
