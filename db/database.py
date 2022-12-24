

from settings import db_connection, COLLECTION_USER, COLLECTION_MESSAGES, COLLECTION_ADMIN, COLLECTION_CHANNELS
import db.models as models


async def create_user(user: models.UserModel):
    col = db_connection[COLLECTION_USER]
    await col.insert_one(user.dict())


async def get_user_by_tg_id(tg_id: int):
    col = db_connection[COLLECTION_USER]
    return await col.find_one(filter={'tg_id': tg_id})


async def get_admin_by_tg_id(tg_id: int):
    col = db_connection[COLLECTION_ADMIN]
    return await col.find_one(filter={'tg_id': tg_id})


async def get_message(msg_id):
    col = db_connection[COLLECTION_MESSAGES]
    res = await col.find_one(filter={'_id': msg_id})
    return res


async def edit_start_message(text):
    col = db_connection[COLLECTION_MESSAGES]
    await col.find_one_and_update(
        {'_id': 'start_message'}, {'$set': {'text': text}}
    )


async def get_id_all_users(channel_id: int):
    col = db_connection[COLLECTION_USER]
    users = await col.find({'channel_id': channel_id}).to_list(9999)
    return [x['tg_id'] for x in users]


async def get_count_users():
    col = db_connection[COLLECTION_USER]
    users = await col.find({}).distinct('tg_id')
    return len(users)


async def edit_message(msg_id, data):
    col = db_connection[COLLECTION_MESSAGES]
    await col.find_one_and_update(
        {'_id': msg_id}, {'$set': data}, upsert=True
    )


async def create_channel(channel: models.ChannelModel):
    col = db_connection[COLLECTION_CHANNELS]
    await col.insert_one(channel.dict())


async def get_channel_by_id(channel_id: int):
    col = db_connection[COLLECTION_CHANNELS]
    return await col.find_one(filter={'channel_id': channel_id})


async def get_channel_by_link_name(link_name: str):
    col = db_connection[COLLECTION_CHANNELS]
    return await col.find_one(filter={'link_name': link_name})


async def update_channel_data(channel_id, field, data):
    col = db_connection[COLLECTION_CHANNELS]
    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': {field: data}}
    )