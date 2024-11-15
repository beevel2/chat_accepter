import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.default import send_start_message
import db.database as db


scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})

logger = logging.getLogger(__name__)


async def send_mass_messages(data):
    logging.info(f'started send_mass_messages with data: {data}')    
    for user in data['users']:
        try:
            user_record = await db.fetch_channel_user(data['channel_db_id'], user)
            await send_start_message(data['message'], user, user_record)
        except Exception as e:
            print(f'MASS SEND CRON ERROR: {e}')
        await asyncio.sleep(0.5)

async def add_scheduler_tasks(_ = None):
    data = await db.get_all_channels_id_and_user_id_mass_send()
    for d in data:
        scheduler.add_job(send_mass_messages, 'cron', hour=d['hour'], minute=d['minutes'], args=(d, ))
