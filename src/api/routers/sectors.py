from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def sectors():
    return {"message": "Sectors endpoint"}