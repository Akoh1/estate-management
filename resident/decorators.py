import jwt
from functools import wraps
from estate_management.resident.models import TokenTable
from estate_management.utils import JWT_SECRET_KEY, ALGORITHM


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        payload = jwt.decode(kwargs["dependencies"], JWT_SECRET_KEY, ALGORITHM)
        print(f"wrapper payload: {payload}")
        user_id = payload["sub"]
        data = (
            kwargs["session"]
            .query(TokenTable)
            .filter_by(
                user_id=user_id, access_token=kwargs["dependencies"], status=True
            )
            .first()
        )
        if data:
            return func(kwargs["dependencies"], kwargs["session"])

        else:
            return {"msg": "Token blocked"}

    return wrapper
