from settings import db_connection, COLLECTION_USER, COLLECTION_MESSAGES, COLLECTION_ADMIN, COLLECTION_CHANNELS, COLLECTION_ACCOUNTS, PYROGRAM_SESSION_PATH
import db.models as models
import os



COLLECTION_SETTINGS = 'settings'


async def create_user(user: models.UserModel):
    col = db_connection[COLLECTION_USER]
    await col.insert_one(user.dict())


async def update_user_not_is_robot(tg_id: int):
    col = db_connection[COLLECTION_USER]
    await col.update_many(
        {'tg_id': tg_id}, {'$set': {'notIsRobot': True}}
    )


async def update_user_banned(tg_id: int, status: bool):
    col = db_connection[COLLECTION_USER]
    await col.update_many(
        {'tg_id': tg_id}, {'$set': {'banned': status}}
    )

async def get_user(tg_id: int, channel_id: int):
    col = db_connection[COLLECTION_USER]
    return await col.find_one(filter={'tg_id': tg_id, 'channel_id': channel_id})


async def create_admin(admin_id):
    col = db_connection[COLLECTION_ADMIN]
    await col.insert_one({"tg_id": admin_id})


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


async def get_channel_stats(channel_id: int):
    col = db_connection[COLLECTION_USER]
    users = await col.find({'channel_id': channel_id}).to_list(99999)

    data = {'total': len(users), 'banned': 0, 'interacted': 0}
 
    for user in users:
        if user.get('banned') is True:
            data['banned'] += 1
        if user.get('notIsRobot') is True:
            data['interacted'] += 1
 
    return data


async def get_all_channels_id_and_user_id_mass_send():
    col_channels = db_connection[COLLECTION_CHANNELS]
    all_channels = await col_channels.find({}).to_list(99999)
    res = []
    for channel in all_channels:
        if channel.get('msg_mass_send', None):
            _users = await get_id_all_users(channel['channel_id'])
            res.append({
                'channel_id': channel['tg_id'],
                'message': channel['msg_mass_send'],
                'hour': channel['hour'],
                'minutes': channel['minutes'],
                'users': _users
            })
    return res


async def get_all_channels():
    col_channels = db_connection[COLLECTION_CHANNELS]
    all_channels = await col_channels.find({}).to_list(99999)
    
    return all_channels


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


async def get_channel_by_tg_id(tg_id: int):
    col = db_connection[COLLECTION_CHANNELS]
    return await col.find_one(filter={'tg_id': tg_id})


async def get_channel_by_link_name(link_name: str):
    col = db_connection[COLLECTION_CHANNELS]
    return await col.find_one(filter={'chat_id': link_name})


async def update_channel_data(channel_id, field, data):
    col = db_connection[COLLECTION_CHANNELS]
    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': {field: data}}
    )


async def delete_channel(channel_id):
    col = db_connection[COLLECTION_CHANNELS]
    await col.delete_one({'channel_id': int(channel_id)})
    await del_account(int(channel_id))
    col = db_connection[COLLECTION_USER]
    await col.delete_many({'channel_id': int(channel_id)})


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

async def get_account_by_phone(phone):
    col = db_connection[COLLECTION_ACCOUNTS]
    return await col.find_one({'phone': phone})


async def create_account(phone: str, tg_id: int, proxy: dict, acc_id:int) -> int:
    col = db_connection[COLLECTION_ACCOUNTS]
    await col.insert_one(
        {
            'account_id': acc_id,
            'tg_id': tg_id,
            'phone': phone,
            'proxy': proxy,
        }
    )
    return acc_id


async def increment_pending(channel_id: int):
    col = db_connection[COLLECTION_CHANNELS]
    channel = await col.find_one(filter={'channel_id': channel_id})

    requests_pending = channel.get('requests_pending')
    if requests_pending is None:
        requests_pending = 1
    else:
        requests_pending += 1
    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': {'requests_pending': requests_pending}}
    )


async def increment_accepted(channel_id: int):
    col = db_connection[COLLECTION_CHANNELS]
    channel = await col.find_one(filter={'channel_id': channel_id})

    requests_accepted = channel.get('requests_accepted')
    if requests_accepted is None:
        requests_accepted = 1
    else:
        requests_accepted += 1
    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': {'requests_accepted': requests_accepted}}
    )


async def purge_pending(channel_id: int):
    col = db_connection[COLLECTION_CHANNELS]
    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': {'requests_pending': 0}}
    )

async def switch_approvement_settings(channel_id: int):
    col = db_connection[COLLECTION_CHANNELS]
    channel = await col.find_one(filter={'channel_id': channel_id})

    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': {'approve': not channel['approve']}}
    )


async def change_link_name(channel_id: int, link_name: str):
    col = db_connection[COLLECTION_CHANNELS]
    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': {'link_name': link_name}}
    )

async def fetch_account_by_id(acc_id: int):
    col = db_connection[COLLECTION_ACCOUNTS]
    account = await col.find_one(filter={'account_id': acc_id})

    return account


async def retie_account(phone: str, acc_id):
    col = db_connection[COLLECTION_ACCOUNTS]
    account = await get_account_by_phone(phone)
    account['account_id'] = acc_id
    await col.insert_one(account)


async def del_account(acc_id: int):
    col = db_connection[COLLECTION_ACCOUNTS]
    account = await col.find_one(filter={'account_id': acc_id})
    await col.delete_one({'account_id': acc_id})
    try:
        os.remove(os.path.join(PYROGRAM_SESSION_PATH, f'client_{account['phone']}.session'))
    except:
        pass
    try:
        os.remove(os.path.join(PYROGRAM_SESSION_PATH, f'client_{account['phone']}.sessionjournal'))
    except:
        pass



async def set_delay(channel_id: int, delay: int, enum: str):
    col = db_connection[COLLECTION_CHANNELS]
    channel = await get_channel_by_id(channel_id)
    message = channel.get(enum)
    message['delay'] = delay
    await col.find_one_and_update({'channel_id': channel_id}, {'$set': {enum: message}})


async def get_messages_bot(channel_id: int):
    channel = await get_channel_by_id(channel_id)
    messages = {}
    for i in range(1, 8):
        if channel.get(f'msg_{i}'):
            messages[f'msg_{i}'] = channel.get(f'msg_{i}')
    return messages


async def get_messages_userbot(channel_id: int):
    channel = await get_channel_by_id(channel_id)
    messages = {}
    for i in range(1, 5):
        if channel.get(f'msg_u_{i}'):
            messages[f'msg_u_{i}'] = channel.get(f'msg_u_{i}')
    return messages
