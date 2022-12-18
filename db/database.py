

from settings import db_connection, COLLECTION_USER, COLLECTION_MESSAGES, COLLECTION_ADMIN
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


async def get_start_message():
    col = db_connection[COLLECTION_MESSAGES]
    res = await col.find_one(filter={'_id': 'start_message'})
    return res['text']


async def edit_start_message(text):
    col = db_connection[COLLECTION_MESSAGES]
    await col.find_one_and_update(
        {'_id': 'start_message'}, {'$set': {'text': text}}
    )


async def get_id_all_users():
    col = db_connection[COLLECTION_USER]
    users = await col.find({}).to_list(9999)
    return [x['tg_id'] for x in users]
