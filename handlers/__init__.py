from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

import handlers.default as h
import handlers.admin as h_admin

from states import AppStates


def setup_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(h.start_command)

    # dp.register_message_handler(h_admin.edit_start_message1_command, Text(startswith='/edit_message_1_'))
    # dp.register_message_handler(h_admin.edit_start_message2_command, Text(startswith='/edit_message_2_'))
    # dp.register_message_handler(h_admin.edit_start_message3_command, Text(startswith='/edit_message_3_'))
    dp.register_message_handler(h_admin.edit_start_message_command, Text(startswith='/edit_message_'), content_types=['any'])
    # dp.register_message_handler(h_admin.get_video_command, content_types=['video_note'], state=[AppStates.STATE_MESSAGE1_VIDEO])
    dp.register_message_handler(h_admin.get_message_command, content_types=['any'], state=[AppStates.STATE_MESSAGE2_MESSAGE, AppStates.STATE_MESSAGE3_MESSAGE])
    dp.register_message_handler(h_admin.get_buttons_command, state=[AppStates.STATE_MESSAGE_BUTTONS])
    
    dp.register_message_handler(h_admin.mass_send_command, Text(startswith='/mass_send_'))
    dp.register_message_handler(h_admin.mass_send_process_command, content_types=['any'], state=[AppStates.STATE_MASS_SEND_BUTTONS, AppStates.STATE_MASS_SEND_MESSAGE])
    dp.register_message_handler(h_admin.stats_command, commands=['stats'])
    
    dp.register_message_handler(h_admin.add_channel_step1_command, commands=['add_channel'])
    dp.register_message_handler(h_admin.add_channel_step2_command, state=[AppStates.STATE_ADD_CHANNEL_ID])
    dp.register_message_handler(h_admin.add_channel_step3_command, state=[AppStates.STATE_ADD_CHANNEL_TG_ID])
    dp.register_message_handler(h_admin.add_channel_step4_command, state=[AppStates.STATE_ADD_CHANNEL_LINK_NAME])
