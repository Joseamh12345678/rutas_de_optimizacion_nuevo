from fastapi import APIRouter, Query
from backend.src.services.navigation_sdk import get_route

router = APIRouter(prefix="/directions", tags=["Directions"])

@router.get("/")
def directions_endpoint(origin: str = Query(...), destination: str = Query(...)):
    return get_route(origin, destination)