

from settings import db_connection, COLLECTION_USER, COLLECTION_MESSAGES, COLLECTION_ADMIN, COLLECTION_CHANNELS
import db.models as models


COLLECTION_SETTINGS = 'settings'


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
    users = await col.find({'channel_id': channel_id}).to_list(99999)
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

async def update_timeout(timeout: int):
    col = db_connection[COLLECTION_SETTINGS]
    res = await col.find_one(filter={'settings': 'timeout'})
    if res:
        await col.find_one_and_update(
            {'settings': timeout}, {'$set': {'value': int(timeout)}}
        )
    else:
        await col.insert_one(
            {
                'setting': 'timeout',
                'value': int(timeout)
            }
        )


async def get_timeout():
    col = db_connection[COLLECTION_SETTINGS]
    res = await col.find_one(filter={'settings': 'timeout'})
    if res:
        return res['value']
    else:
        return 2


async def get_btn_robot_text():
    col = db_connection[COLLECTION_SETTINGS]
    res = await col.find_one(filter={'settings': 'btn_robot_text'})
    if res:
        return res['value']
    else:
        await col.insert_one(
            {
                'setting': 'btn_robot_text',
                'value': 'Я не робот!'
            }
        )
        return 'Я не робот!'
