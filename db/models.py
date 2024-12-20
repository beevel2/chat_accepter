from typing import Optional, List

from datetime import datetime, timezone

from pydantic import BaseModel, Field


def get_utc_time():
    return datetime.now(tz=timezone.utc)


class UserModel(BaseModel):
    first_name: str
    last_name: str
    username: str
    tg_id: int
    date_registration: datetime = Field(default_factory=get_utc_time)
    channel_id: int
    notIsRobot: bool = False
    banned: bool = False


class LeadModel(BaseModel):
    user_id: int
    manager_id: int

    is_first: bool = True
    
    date_registration: datetime
    lead_time: datetime = Field(default_factory=get_utc_time)
    time_diff_seconds: int


class AdminModel(BaseModel):
    tg_id: int


class ManagerModel(BaseModel):
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



class MessageModel(BaseModel):
    text: str = ''
    photos: Optional[list] = []
    video_id: Optional[str] = None
    video_note_id: Optional[str] = None
    animation_id: Optional[str] = None
    voice_id: Optional[str] = None
    button_text: List[dict] = []

class PushModel(BaseModel):
    data: MessageModel = MessageModel()
    channel_id: int
    