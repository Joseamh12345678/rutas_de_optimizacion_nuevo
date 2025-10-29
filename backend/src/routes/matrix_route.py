from fastapi import APIRouter, Query
from backend.src.services.matrix import get_distance_matrix

router = APIRouter(prefix="/matrix", tags=["Distance Matrix"])

@router.get("/")
def matrix_endpoint(origins: list[str] = Query(...), destinations: list[str] = Query(...)):
    return get_distance_matrix(origins, destinations)