from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def screener():
    return {"message": "Screener endpoint"}