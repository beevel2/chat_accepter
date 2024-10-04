from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram_calendar import simple_cal_callback


import handlers.default as h
import handlers.admin as h_admin
import handlers.manager as h_manager

import filters

from states import AppStates

import re



def setup_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(h.start_command, state='*')
    dp.register_chat_member_handler(h.unsub_handler)
    dp.register_callback_query_handler(h.next_push_handler, lambda c: c.data.startswith('next_push_'), state='*')


    dp.register_my_chat_member_handler(h.banned_handler, chat_type='private')

    dp.register_message_handler(h_admin.start_command, filters.is_admin_filter, commands=['start'], state='*')

    dp.register_message_handler(h_manager.start, filters.is_manager_filter, commands='start', state='*')

    dp.register_message_handler(h_admin.cancel, Text('Отмена'))


    # Lead reg
    dp.register_message_handler(h_manager.add_lead_menu, filters.is_manager_filter, text='Записать лид', state='*')
    dp.register_message_handler(h_manager.add_lead_froward_handler, filters.is_manager_filter, lambda m: bool(m.forward_from), state=AppStates.STATE_ADD_LEAD)
    dp.register_message_handler(h_manager.add_lead_id_handler, filters.is_manager_filter, content_types='text', state=AppStates.STATE_ADD_LEAD)
    dp.register_callback_query_handler(h_manager.add_lead_anyway, filters.is_manager_filter, lambda c: c.data.startswith('add_lead_'), state='*')

    # Lead stats
    dp.register_message_handler(h_manager.stats_menu, text='Статистика', state='*')
    dp.register_callback_query_handler(h_manager.stats_calendar_entry, lambda c: c.data == 'lead_stats_to_calendar', state='*')
    dp.register_callback_query_handler(h_manager.process_stats_calendar, simple_cal_callback.filter(), state=AppStates.STATE_LEAD_STATS)


    dp.register_callback_query_handler(h_admin.add_account_step1_command,
                                lambda c: c.data.startswith('tie_account_'))
    dp.register_message_handler(h_admin.add_account_step2_command, state=[AppStates.STATE_WAIT_PROXY], regexp=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+:[^:]+:[^:]+")
    dp.register_message_handler(h_admin.add_account_step3_command, state=[AppStates.STATE_WAIT_PHONE], regexp=r"\d+")
    dp.register_callback_query_handler(h_admin.retie_account, 
                                       lambda c: c.data.startswith('retie_acc_'),
                                       state=[AppStates.STATE_WAIT_PHONE])
    dp.register_message_handler(h_admin.add_account_step4_command, state=[AppStates.STATE_WAIT_AUTH_CODE])
    dp.register_message_handler(h_admin.add_account_step5_command, state=[AppStates.STATE_WAIT_2FA])

    dp.register_message_handler(h_admin.approvement_settings_get_id, content_types='text', state=[AppStates.STATE_APPROVEMENT_SETTINGS])
    dp.register_callback_query_handler(h_admin.approvement_settings_query, lambda c: c.data.startswith('approve'), state=[AppStates.STATE_APPROVEMENT_SETTINGS])

    # dp.register_message_handler(h_admin.approve_requersts_btn, Text('Одобрить заявки'))
    dp.register_message_handler(h_admin.approve_requests_get_id, content_types='text', state=[AppStates.STATE_APPROVE_REQUERSTS])


    # Меню отписки
    dp.register_callback_query_handler(h_admin.push_menu, lambda c: c.data.startswith('unsub_settings'), state='*')
    dp.register_callback_query_handler(h_admin.append_push, lambda c: c.data.startswith('add_push_'), state='*')
    dp.register_callback_query_handler(h_admin.delete_push, lambda c: c.data.startswith('delete_push_'), state='*')
    dp.register_callback_query_handler(h_admin.delete_push_confirm, lambda c: c.data.startswith('confirm_push_deletion_'), state='*')
    dp.register_callback_query_handler(h_admin.edit_push, lambda c: c.data.startswith('view_push_'), state='*')
    dp.register_message_handler(h_admin.edit_push_get_data, content_types='any', state=[AppStates.STATE_GET_PUSH_DATA])
    dp.register_message_handler(h_admin.edit_push_get_button, content_types='text', state=[AppStates.STATE_GET_PUSH_BUTTON])


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

    # Изменение сообщений
    # comment to enable userbot
    dp.register_callback_query_handler(h_admin.edit_messages_command,
                                       lambda c: c.data.startswith('edit_messages_'))

    # uncomment to enable userbot
    # dp.register_callback_query_handler(h_admin.edit_messages_menu,
    #                                    lambda c: c.data.startswith('edit_messages_'))

    dp.register_callback_query_handler(h_admin.edit_messages_command,
                                       lambda c: c.data.startswith('bot_edit_messages_') or c.data.startswith('userbot_edit_messages_'),
                                       state='*')
    dp.register_callback_query_handler(
        h_admin.wait_edit_channel_id_callback, 
        lambda call: 'edit_msg_' in call.data,
        state='*'
    )

    # Очистить сообщение
    dp.register_callback_query_handler(
        h_admin.clear_message, 
        lambda call: call.data.startswith('clear_message_'),
        state=[AppStates.STATE_WAIT_MSG]

    )
    dp.register_callback_query_handler(
        h_admin.clear_message_confirm, 
        lambda call: call.data.startswith('comfirm_message_del_'),
        state=[AppStates.STATE_WAIT_MSG]

    )


    # Получить текст сообщения
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

    dp.register_callback_query_handler(h_admin.set_delay_menu,
                                       lambda c: c.data.startswith('set_delay_'))
    dp.register_callback_query_handler(h_admin.set_delay_pick_message,
                                       lambda c: c.data.startswith('delay_'))
    dp.register_callback_query_handler(h_admin.set_delay,
                                       lambda c: c.data.startswith('edit-delay'))
    dp.register_message_handler(h_admin.set_delay_get_message,
                                state=[AppStates.STATE_GET_DELAY])

    dp.register_message_handler(h_admin.my_channels, Text('Мои каналы'), state='*')

    dp.register_callback_query_handler(h_admin.del_account,
                                       lambda c: c.data.startswith('delete_account_'))

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

    dp.register_callback_query_handler(
        h_admin.delete_channel, 
        lambda call: call.data.startswith('delete_channel_')
    )
    dp.register_callback_query_handler(
        h_admin.delete_channel_confirm, 
        lambda call: call.data.startswith('comfirm_channel_del_')
    )

    dp.register_message_handler(h.user_send_message_command)
