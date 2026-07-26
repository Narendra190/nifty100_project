from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def portfolio():
    return {"message": "Portfolio endpoint"}