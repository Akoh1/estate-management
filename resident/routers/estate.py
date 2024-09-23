from typing import Annotated
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...session import get_db
from estate_management.resident.schema import User, UserCreate, CreateEstate
from estate_management.resident import models
from estate_management.auth_bearer import JWTBearer


router = APIRouter(
    prefix="/estate",
    tags=["admin"],
    responses={404: {"description": "Not found"}, 200: {"description": "Successful"}},
)


@router.get("/estates")
async def get_estates(
    dependencies=Depends(JWTBearer()), session: Session = Depends(get_db)
):
    user = session.query(models.Estate).all()
    return user


@router.post("/register")
def register_estate(estate: CreateEstate, session: Session = Depends(get_db)):
    existing_estate = session.query(models.Estate).filter_by(name=estate.name).first()
    if existing_estate:
        raise HTTPException(status_code=400, detail="Estate already registered")

    new_estate = models.Estate(name=estate.name)
    new_estate.code = new_estate.generate_code()

    session.add(new_estate)
    session.commit()
    session.refresh(new_estate)

    # Create User and link estate
    if new_estate:
        new_user = models.User(
            first_name=estate.first_name,
            last_name=estate.last_name,
            email=estate.email,
            estate=new_estate,
        )
        new_user.set_password(estate.password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    return {"message": "user created successfully"}
