import datetime
from pydantic import BaseModel


class LoginDetails(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_security: bool
    is_admin: bool
    is_resident: bool
    estate_id: int
    created_date: datetime.datetime

    class Config:
        orm_mode = True


class CreateEstate(UserCreate):
    name: str


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime
