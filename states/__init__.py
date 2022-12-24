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
    STATE_ADD_CHANNEL_LINK_NAME = Item()
