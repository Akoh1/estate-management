import logging
import jwt
from datetime import datetime
from estate_management.resident.schema import ResidentOrSecurityCreate, LoginDetails
from estate_management.resident.models import User, TokenTable
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from estate_management.session import get_db
from estate_management.auth_bearer import JWTBearer
from estate_management.utils import JWT_SECRET_KEY, ALGORITHM

from estate_management.utils import Tokenization


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["admin"],
    responses={404: {"description": "Not found"}, 200: {"description": "Successful"}},
)


@router.post("/register")
def register_user(user: ResidentOrSecurityCreate, session: Session = Depends(get_db)):
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        is_security=user.is_security,
        is_resident=user.is_resident,
        estate_id=user.estate_id,
    )
    new_user.set_password(user.password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "user created successfully"}


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


@router.post("/logout")
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    token = dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    logger.info(f"payload: {payload}")
    user_id = payload["sub"]
    token_record = db.query(TokenTable).all()
    info = []
    for record in token_record:
        if (datetime.utcnow() - record.created_date).days > 1:
            info.append(record.user_id)
    if info:
        db.query(TokenTable).where(TokenTable.user_id.in_(info)).delete()
        db.commit()

    existing_token = (
        db.query(TokenTable)
        .filter(TokenTable.user_id == user_id, TokenTable.access_token == token)
        .first()
    )
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message": "Logout Successfully"}
