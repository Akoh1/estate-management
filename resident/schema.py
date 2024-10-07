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


class ResidentOrSecurityCreate(UserCreate):
    is_security: bool = False
    is_resident: bool
    estate_id: int

    class Config:
        orm_mode = True


class UserDetails(UserBase):
    id: int
    is_security: bool
    is_admin: bool
    is_resident: bool
    estate_id: int
    created_date: datetime.datetime

    class Config:
        orm_mode = True


# class SecurityUserCreate(UserBase):
#     id: int
#     is_security: bool
#     estate_id: int
#     created_date: datetime.datetime
#
#     class Config:
#         orm_mode = True


class CreateEstate(UserCreate):
    name: str


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime


class Visitor(BaseModel):
    name: str
    phone: str
    resident_id: int


class VisitorDetails(Visitor):
    id: int
    access_code: str
    access_granted: bool
    created_date: datetime.datetime
    write_date: datetime.datetime
