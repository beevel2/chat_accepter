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
    notIsRobot: bool = False
    banned: bool = False


class AdminModel(BaseModel):
    tg_id: int


class ChannelModel(BaseModel):
    channel_id: int
    tg_id: int
    channel_name: str
    link_name: str
    approve: bool
    requests_pending: int
    requests_accepted: int
    msg_1: Optional[str] = None
    msg_2: Optional[str] = None
    msg_3: Optional[str] = None
    msg_4: Optional[str] = None
    msg_5: Optional[str] = None
    msg_6: Optional[str] = None
    msg_7: Optional[str] = None
    msg_mass_send: Optional[str] = None
    msg_u_1: Optional[str] = None
    msg_u_2: Optional[str] = None
    msg_u_3: Optional[str] = None
    msg_u_4: Optional[str] = None



