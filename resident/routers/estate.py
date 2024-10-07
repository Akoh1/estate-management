from typing import Annotated
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from estate_management.session import get_db
from estate_management.resident.schema import (
    UserDetails,
    UserCreate,
    CreateEstate,
    Visitor,
)
from estate_management.resident import models
from estate_management.auth_bearer import JWTBearer
from estate_management.resident.decorators import token_required


router = APIRouter(
    prefix="/estate",
    tags=["admin"],
    responses={404: {"description": "Not found"}, 200: {"description": "Successful"}},
)


@router.get("/estates")
@token_required
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
            is_admin=True,
        )
        new_user.set_password(estate.password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    return {"message": "estate created successfully"}


@router.post("/visitor/code")
def generate_visitor_code(
    visitor: Visitor,
    dependencies=Depends(JWTBearer()),
    session: Session = Depends(get_db),
):

    user_visitor = session.query(models.Visitor).filter_by(phone=visitor.phone).first()
    if user_visitor:
        # generate code
        user_visitor.access_code = user_visitor.generate_access_code()
        session.commit()
        session.refresh(user_visitor)
    else:
        try:
            user_visitor = models.Visitor(
                name=visitor.name,
                phone=visitor.phone,
                resident_id=visitor.resident_id,
            )
            user_visitor.access_code = user_visitor.generate_access_code()
            session.add(user_visitor)
            session.commit()
            session.refresh(user_visitor)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {e}")

    return {
        "access_code": user_visitor.access_code,
        "message": "visitor created successfully",
    }
