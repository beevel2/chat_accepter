from aiogram.utils.helper import Helper, HelperMode, Item


class AppStates(Helper):
    mode = HelperMode.snake_case

    STATE_EDIT_MESSAGE = Item()
    STATE_MASS_SEND_MESSAGE = Item()
    STATE_MASS_SEND_BUTTONS = Item()
