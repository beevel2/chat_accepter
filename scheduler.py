import asyncio
import datetime
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from handlers.default import send_start_message
from db import models
import db.database as db
import pytz


scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})

logger = logging.getLogger(__name__)


async def send_mass_messages(data):
    logging.info(f'started send_mass_messages with data: {data}')    
    for user in data['users']:
        try:
            user_record = await db.fetch_channel_user(data['channel_db_id'], user)
            await send_start_message(data['message'], user, user_record)
        except Exception as e:
            logger.exception(f'Error at send_mass_messages with data: {data}')
        await asyncio.sleep(0.5)

async def capture_all_stat_snapshots():
    today = datetime.date.today()
    date = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59)
    async for channel in await db.get_all_channels_generator():
        logger.info(f'capturing snapshot for channel {channel["channel_id"]}')
        try:
            stats = await db.get_channel_stats(channel["channel_id"])
            await db.create_stat_snapshot(
                models.StatSnapshotModel(
                    date=date,
                    channel_id=channel["channel_id"],
                    type=models.StatSnapshotTypeEnum.APPROVED_REQUESTS,
                    value=channel["requests_accepted"]
                )
            )
            await db.create_stat_snapshot(
                models.StatSnapshotModel(
                    date=date,
                    channel_id=channel["channel_id"],
                    type=models.StatSnapshotTypeEnum.USERS_NEW,
                    value=stats['total']
                )
            )
            await db.create_stat_snapshot(
                models.StatSnapshotModel(
                    date=date,
                    channel_id=channel["channel_id"],
                    type=models.StatSnapshotTypeEnum.USERS_INTERACTED,
                    value=stats['interacted']
                )
            )
            await db.create_stat_snapshot(
                models.StatSnapshotModel(
                    date=date,
                    channel_id=channel["channel_id"],
                    type=models.StatSnapshotTypeEnum.USERS_BANNED,
                    value=stats['banned']
                )
            )
            logger.info(f'successfully captured snapshot for channel {channel["channel_id"]}')
        except:
            logger.exception(f'error capturing snapshot for channel {channel["channel_id"]}')


async def add_scheduler_tasks(_ = None):
    moscow_tz = pytz.timezone('Europe/Moscow')
    scheduler.add_job(capture_all_stat_snapshots, trigger=CronTrigger(hour=23, minute=59, timezone=moscow_tz))
    
    data = await db.get_all_channels_id_and_user_id_mass_send()
    for d in data:
        scheduler.add_job(send_mass_messages, 'cron', hour=d['hour'], minute=d['minutes'], args=(d, ))
