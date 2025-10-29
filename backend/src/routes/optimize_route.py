from fastapi import APIRouter, Query
from backend.src.services.optimize import optimize_route

router = APIRouter(prefix="/optimize", tags=["Route Optimization"])

@router.get("/")
def optimize_endpoint(locations: list[str] = Query(...)):
    return optimize_route(locations)