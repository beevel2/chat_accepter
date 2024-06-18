import settings
from settings import db_connection
import asyncio


async def main():
    col = db_connection[settings.COLLECTION_CHANNELS]
    for channel in (await col.find().to_list(99999999)):
        if channel.get('channel_name') is None:
            await col.update_one({'_id': channel['_id']}, {'$set': {'channel_name': f'К {channel["channel_id"]}'}})

        if channel.get('approve') is None:
            await col.update_one({'_id': channel['_id']}, {'$set': {'approve': True}})

        if channel.get('requests_pending') is None:
            await col.update_one({'_id': channel['_id']}, {'$set': {'requests_pending': 0}})

        if channel.get('requests_accepted') is None:
            await col.update_one({'_id': channel['_id']}, {'$set': {'requests_accepted': 0}})
    print('adapted channel model sucessfuly')

asyncio.run(main())
