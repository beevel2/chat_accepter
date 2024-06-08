from pathlib import Path
from settings import bot, DOWNLOAD_PATH

import logging

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

async def download_file(file_id: str, voice=False):
    filename = file_id
    if voice:
        filename += ".ogg"
    if file_id.endswith('.jpg'):
        file_id = file_id.split('.jpg')[0]
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    src = Path(DOWNLOAD_PATH, filename)
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())


def replace_in_message(message: str, s_from:str, s_to: str) -> str:
    return message.replace(s_from, str(s_to))


def check_message_has_data(msg, ignore_keys):
    value = 0

    for key in msg:
        if not (key in ignore_keys):
            value += bool(msg[key])

    return value