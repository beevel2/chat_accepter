import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.default import send_start_message
import db.database as db


scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})


async def send_mass_messages(data):
    for user in data['users']:
        try:
            await send_start_message(data['message'], user, 'USERNAME')
        except Exception as e:
            print(f'MASS SEND CRON ERROR: {e}')
        await asyncio.sleep(0.5)

async def add_scheduler_tasks(_ = None):
    data = await db.get_all_channels_id_and_user_id_mass_send()
    for d in data:
        scheduler.add_job(send_mass_messages, 'cron', hour=d['hour'], minute=d['minutes'], args=(d, ))
