import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
import jwt
from decouple import config

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = config("JWT_ALGORITHM")
JWT_SECRET_KEY = config("JWT_SECRET_KEY")  # should be kept secret
JWT_REFRESH_SECRET_KEY = config("JWT_REFRESH_SECRET_KEY")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Tokenization:
    def __init__(self, subject: Union[str, Any], expires_delta: int = None):
        self.subject = subject
        self.expires_delta = expires_delta

    # def __init__(self, password: str):
    #     self.password = password

    # def get_hashed_password(self) -> str:
    #     return password_context.hash(self.password)
    #
    # def verify_password(self, hashed_pass: str) -> bool:
    #     return password_context.verify(self.password, hashed_pass)

    def create_access_token(self) -> str:
        if self.expires_delta is not None:
            expires_delta = datetime.utcnow() + timedelta(minutes=self.expires_delta)

        else:
            expires_delta = datetime.utcnow() + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expires_delta, "sub": str(self.subject)}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

        return encoded_jwt

    def create_refresh_token(self) -> str:
        if self.expires_delta is not None:
            expires_delta = datetime.utcnow() + timedelta(minutes=self.expires_delta)
        else:
            expires_delta = datetime.utcnow() + timedelta(
                minutes=REFRESH_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expires_delta, "sub": str(self.subject)}
        encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
        return encoded_jwt
