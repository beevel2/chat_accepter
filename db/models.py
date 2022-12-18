from datetime import datetime

from pydantic import BaseModel


class UserModel(BaseModel):
    first_name: str
    last_name: str
    username: str
    tg_id: int
    date_registration: datetime = datetime.now()


class AdminModel(BaseModel):
    tg_id: int
