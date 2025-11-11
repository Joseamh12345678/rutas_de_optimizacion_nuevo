from fastapi import APIRouter, Query
from backend.src.services.optimize import optimize_route

router = APIRouter(prefix="/optimize", tags=["Route Optimization"])

@router.get("/")
def optimize_endpoint(locations: list[str] = Query(...)):
    result = optimize_route(locations)

    #Si se decodificó la geometría, la incluimos en la respuesta
    if isinstance(result, dict) and "decoded_geometry" in result:
        return {
            "geometry": [{"lat": lat, "lng": lng} for lat, lng in result["decoded_geometry"]],
            "raw": result["raw"]
        }

    #Si no hay geometría decodificada, devolvemos la respuesta original
    return result