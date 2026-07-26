from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def documents():
    return {"message": "Documents endpoint"}