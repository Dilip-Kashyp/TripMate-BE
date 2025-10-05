from fastapi import APIRouter
from app.utils.decorators import Response

router = APIRouter()

@router.get("/")
@Response("Srever is Running!!")
def read_root():
    return {"message": "Welcome to the page"}
