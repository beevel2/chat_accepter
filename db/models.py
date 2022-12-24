from typing import Optional

from datetime import datetime

from pydantic import BaseModel


class UserModel(BaseModel):
    first_name: str
    last_name: str
    username: str
    tg_id: int
    date_registration: datetime = datetime.now()
    channel_id: int


class AdminModel(BaseModel):
    tg_id: int


class ChannelModel(BaseModel):
    channel_id: int
    tg_id: int
    link_name: str
    message_1: Optional[str] = None
    message_2: Optional[str] = None
    message_3: Optional[str] = None

