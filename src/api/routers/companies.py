from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def companies():
    return {"message": "Companies endpoint"}