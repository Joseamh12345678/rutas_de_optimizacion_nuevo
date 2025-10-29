from fastapi import APIRouter
from backend.src.models.rutas_model import Ruta
from backend.src.services.rutas import registrar_ruta, listar_rutas

router = APIRouter(prefix="/rutas", tags=["Rutas"])

@router.post("/", response_model=Ruta)
def registrar_ruta_endpoint(ruta: Ruta):
    return registrar_ruta(ruta)

@router.get("/", response_model=list[Ruta])
def listar_rutas_endpoint():
    return listar_rutas()