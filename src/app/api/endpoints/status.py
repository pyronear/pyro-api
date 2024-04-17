from fastapi import APIRouter

router = APIRouter()

@router.get("/get-status")
async def get_api_status():
    """
    Returns the status of the API
    """
    # TODO : implement a more complexe behavior to check if everything is initialized for ex
    return {"status": "API is running smoothly"}