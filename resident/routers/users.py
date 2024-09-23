from estate_management.resident.schema import User, LoginDetails
from estate_management.resident.models import User, TokenTable
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from ...session import get_db

from ...utils import Tokenization

router = APIRouter(
    prefix="/users",
    tags=["admin"],
    responses={404: {"description": "Not found"}, 200: {"description": "Successful"}},
)


@router.post("/login")
def login(login: LoginDetails, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email"
        )

    if not user.check_password(login.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    token = Tokenization(user.id, 60)
    access = token.create_access_token()
    refresh = token.create_refresh_token()

    token_db = TokenTable(
        user_id=user.id, access_token=access, refresh_token=refresh, status=True
    )
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }
