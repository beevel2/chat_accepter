from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from pathlib import Path

from motor.motor_asyncio import (AsyncIOMotorClient, AsyncIOMotorDatabase)
import os

TOKEN=''

MONGO_DB = ''
MONGO_URI = f'mongodb://localhost:27017'

API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
DEVICE_MODEL = 'PC 64bit'
SYSTEM_VERSION = 'Windows 7'
APP_VERSION = '1.9.1'
LANG_CODE = 'en'
SYSTEM_LANG_CODE = 'en-US'
LANG_PACK = 'tdesktop'

PYROGRAM_SESSION_PATH = Path(os.getcwd(), 'sessions')

if not os.path.exists(PYROGRAM_SESSION_PATH):
    os.makedirs(PYROGRAM_SESSION_PATH)

DOWNLOAD_PATH = Path(os.getcwd(), 'files')

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

COLLECTION_ACCOUNTS = 'accounts'
COLLECTION_USER = 'users'
COLLECTION_ADMIN = 'admins'
COLLECTION_MESSAGES = 'messages'
COLLECTION_CHANNELS = 'channels'


def _connect_to_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    return db


db_connection = _connect_to_db()


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())