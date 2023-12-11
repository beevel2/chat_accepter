from aiogram.utils.helper import Helper, HelperMode, Item


class AppStates(Helper):
    mode = HelperMode.snake_case

    STATE_MASS_SEND_MESSAGE = Item()
    STATE_MASS_SEND_BUTTONS = Item()

    STATE_MESSAGE1_VIDEO = Item()
    STATE_MESSAGE2_MESSAGE = Item()
    STATE_MESSAGE3_MESSAGE = Item()
    STATE_MESSAGE_BUTTONS = Item()
    
    STATE_ADD_CHANNEL_ID = Item()
    STATE_ADD_CHANNEL_TG_ID = Item()
    STATE_ADD_CHANNEL_NAME = Item()
    STATE_ADD_CHANNEL_APPROVE = Item()
    STATE_ADD_CHANNEL_LINK_NAME = Item()

    STATE_MASS_SEND_BTN = Item()
    STATE_EDIT_MESSAGE_BTN = Item()
    STATE_ADD_CHANNEL_BTN = Item()
    STATE_CHANGE_TIMEOUT_BTN = Item()

    STATE_WAIT_CHANNEL_ID = Item()
    STATE_WAIT_MSG = Item()
    STATE_WAIT_MSG_BUTTON = Item()
    STATE_WAIT_MSG_MASS_SEND_TIME = Item()

    STATE_APPROVE_REQUERSTS = Item()

    STATE_APPROVEMENT_SETTINGS = Item()

    STATE_WAIT_PROXY = Item()
    STATE_WAIT_PHONE = Item()
    STATE_WAIT_AUTH_CODE = Item()
    STATE_WAIT_2FA = Item()
    
    STATE_GET_LINK = Item()
    
    STATE_GET_DELAY = Item()
