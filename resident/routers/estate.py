from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/estate",
    tags=["admin"],
    responses={404: {"description": "Not found"}, 200: {"description": "Successful"}},
)


@router.get("/")
async def read_items():
    test = {"estates": "Estate"}
    return test
