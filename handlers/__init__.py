from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

import handlers.default as h
import handlers.admin as h_admin

from states import AppStates

import re


def setup_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(h.start_command)

    dp.register_message_handler(h_admin.start_command, commands=['start'], state='*')

    dp.register_message_handler(h_admin.cancel, Text('Отмена'))

    dp.register_callback_query_handler(h_admin.add_account_step1_command,
                                lambda c: c.data.startswith('tie_account_'))
    dp.register_message_handler(h_admin.add_account_step2_command, state=[AppStates.STATE_WAIT_PROXY], regexp=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+:[^:]+:[^:]+")
    dp.register_message_handler(h_admin.add_account_step3_command, state=[AppStates.STATE_WAIT_PHONE], regexp=r"\d+")
    dp.register_callback_query_handler(h_admin.retie_account, 
                                       lambda c: c.data.startswith('retie_acc_'),
                                       state=[AppStates.STATE_WAIT_PHONE])
    dp.register_message_handler(h_admin.add_account_step4_command, state=[AppStates.STATE_WAIT_AUTH_CODE])
    dp.register_message_handler(h_admin.add_account_step5_command, state=[AppStates.STATE_WAIT_2FA])

    # dp.register_message_handler(h_admin.edit_start_message_btn_command, Text('Изменить сообщение'))
    dp.register_message_handler(h_admin.edit_start_message_btn_step2_command, state=[AppStates.STATE_EDIT_MESSAGE_BTN], regexp=r"\d+\s\d")

    # dp.register_message_handler(h_admin.edit_start_message_command, Text(startswith='/edit_message_'), content_types=['any'])


    # dp.register_message_handler(h_admin.approvement_settings, Text('Приём заявок'))
    dp.register_message_handler(h_admin.approvement_settings_get_id, content_types='text', state=[AppStates.STATE_APPROVEMENT_SETTINGS])
    dp.register_callback_query_handler(h_admin.approvement_settings_query, lambda c: c.data.startswith('approve'), state=[AppStates.STATE_APPROVEMENT_SETTINGS])

    # dp.register_message_handler(h_admin.approve_requersts_btn, Text('Одобрить заявки'))
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
    dp.register_message_handler(h_admin.add_channel_get_link_name, state=[AppStates.STATE_ADD_CHANNEL_LINK_NAME])
    dp.register_message_handler(h_admin.add_channel_get_name, state=[AppStates.STATE_ADD_CHANNEL_NAME])
    dp.register_callback_query_handler(h_admin.add_channel_step4_command, lambda c: c.data.startswith('approve_'), state=[AppStates.STATE_ADD_CHANNEL_APPROVE])

    dp.register_message_handler(h_admin.edit_timeout_command, Text('Изменить таймаут отправки сообщения'))
    dp.register_message_handler(h_admin.edit_timeout_step2_command, state=[AppStates.STATE_CHANGE_TIMEOUT_BTN], regexp=r"\d+")


    dp.register_callback_query_handler(h_admin.edit_messages_menu,
                                       lambda c: c.data.startswith('edit_messages_'))

    dp.register_callback_query_handler(h_admin.edit_messages_command,
                                       lambda c: c.data.startswith('bot_edit_messages_'),
                                       state='*')

    dp.register_message_handler(h_admin.my_channels, Text('Мои каналы'), state='*')

    dp.register_callback_query_handler(
        h_admin.change_link_name, 
        lambda call: call.data.startswith('set_link_name_')
    )
    dp.register_message_handler(h_admin.change_link_name_get, content_types='text', state=[AppStates.STATE_GET_LINK])

    dp.register_callback_query_handler(
        h_admin.switch_approvement, 
        lambda call: call.data.startswith('switch_requests_approve_')
    )

    dp.register_callback_query_handler(
        h_admin.approve_requests, 
        lambda call: call.data.startswith('requests_approve_')
    )

    dp.register_callback_query_handler(
        h_admin.channel_menu, 
        lambda call: call.data.startswith('channel_'),
        state='*'
    )

    dp.register_callback_query_handler(
        h_admin.my_channels_page, 
        lambda call: 'list_channel_page_' in call.data
    )


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
