from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def peers():
    return {"message": "Peers endpoint"}