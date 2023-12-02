from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

import handlers.default as h
import handlers.admin as h_admin

from states import AppStates


def setup_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(h.start_command)

    dp.register_message_handler(h_admin.start_command, commands=['start'], state='*')

    dp.register_message_handler(h_admin.cancel, Text('Отмена'))

    dp.register_message_handler(h_admin.edit_start_message_btn_command, Text('Изменить сообщение'))
    dp.register_message_handler(h_admin.edit_start_message_btn_step2_command, state=[AppStates.STATE_EDIT_MESSAGE_BTN], regexp=r"\d+\s\d")

    dp.register_message_handler(h_admin.edit_start_message_command, Text(startswith='/edit_message_'), content_types=['any'])


    dp.register_message_handler(h_admin.approvement_settings, Text('Приём заявок'))
    dp.register_message_handler(h_admin.approvement_settings_get_id, content_types='text', state=[AppStates.STATE_APPROVEMENT_SETTINGS])
    dp.register_callback_query_handler(h_admin.approvement_settings_query, lambda c: c.data.startswith('approve'), state=[AppStates.STATE_APPROVEMENT_SETTINGS])

    dp.register_message_handler(h_admin.approve_requersts_btn, Text('Одобрить заявки'))
    dp.register_message_handler(h_admin.approve_requests_get_id, content_types='text', state=[AppStates.STATE_APPROVE_REQUERSTS])


    # dp.register_message_handler(h_admin.get_message_command, content_types=['any'], state=[AppStates.STATE_MESSAGE2_MESSAGE, AppStates.STATE_MESSAGE3_MESSAGE])
    # dp.register_message_handler(h_admin.get_buttons_command, state=[AppStates.STATE_MESSAGE_BUTTONS])
    
    dp.register_message_handler(h_admin.mass_send_btn_command, Text('Рассылка'))
    dp.register_message_handler(h_admin.mass_send_btn_step2_command, state=[AppStates.STATE_MASS_SEND_BTN], regexp=r"\d+")

    dp.register_message_handler(h_admin.mass_send_command, Text(startswith='/mass_send_'))
    dp.register_message_handler(h_admin.mass_send_process_command, content_types=['any'], state=[AppStates.STATE_MASS_SEND_BUTTONS, AppStates.STATE_MASS_SEND_MESSAGE])
    dp.register_message_handler(h_admin.stats_command, commands=['stats'])
    
    dp.register_message_handler(h_admin.add_channel_step1_command, Text('Добавить канал'))

    dp.register_message_handler(h_admin.add_channel_step1_command, commands=['add_channel'])
    dp.register_message_handler(h_admin.add_channel_step2_command, state=[AppStates.STATE_ADD_CHANNEL_ID])
    dp.register_message_handler(h_admin.add_channel_step3_command, state=[AppStates.STATE_ADD_CHANNEL_TG_ID])
    dp.register_callback_query_handler(h_admin.add_channel_step4_command, lambda c: c.data.startswith('approve_'), state=[AppStates.STATE_ADD_CHANNEL_APPROVE])

    dp.register_message_handler(h_admin.edit_timeout_command, Text('Изменить таймаут отправки сообщения'))
    dp.register_message_handler(h_admin.edit_timeout_step2_command, state=[AppStates.STATE_CHANGE_TIMEOUT_BTN], regexp=r"\d+")

    dp.register_message_handler(h_admin.edit_messages_command, Text('Редактировать сообщения'))

    dp.register_callback_query_handler(
        h_admin.wait_edit_channel_id_callback, 
        lambda call: 'edit_msg_' in call.data
    )

    dp.register_message_handler(
        h_admin.wait_channel_id_command,
        regexp=r"\d+",
        state=[AppStates.STATE_WAIT_CHANNEL_ID]
    )

    dp.register_message_handler(
        h_admin.wait_get_message_command,
        content_types=['any'],
        state=[AppStates.STATE_WAIT_MSG]
    )

    dp.register_message_handler(
        h_admin.wait_get_buttons_command,
        state=[AppStates.STATE_WAIT_MSG_BUTTON]
    )

    dp.register_message_handler(
        h_admin.wait_get_mass_send_time_command,
        state=[AppStates.STATE_WAIT_MSG_MASS_SEND_TIME],
        regexp=r"\d{1,2}:\d{1,2}"
    )

    dp.register_message_handler(h.user_send_message_command)
