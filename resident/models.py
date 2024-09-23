import bcrypt
from typing import List
from typing import Optional
import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from ..database import Base


class Estate(Base):
    __tablename__ = "estate"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    users = relationship("User", back_populates="estate")
    created_date = Column(DateTime, default=datetime.datetime.now)
    active = Column(Boolean, default=False)

    def generate_code(self):
        middle_name = len(self.name) // 2
        code = (
            self.name[:2].upper()
            + str(middle_name)
            + self.name[middle_name : middle_name + 2].upper()
        )
        return code


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_security = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_resident = Column(Boolean, default=True)
    estate_id = Column(Integer, ForeignKey("estate.id"))
    estate = relationship("Estate", back_populates="users")
    created_date = Column(DateTime, default=datetime.datetime.now)
    active = Column(Boolean, default=False)

    def set_password(self, password):

        hash_password = password_context.hash(password)
        self.password = hash_password

    def check_password(self, password):
        return password_context.verify(password, self.password)


class TokenTable(Base):
    __tablename__ = "token"

    user_id = Column(Integer)
    access_token = Column(String(450), primary_key=True)
    refresh_token = Column(String(450), nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)
