from fastapi import APIRouter
from backend.src.models.users_model import User
from backend.src.services.user import registrar_usuario, listar_usuarios

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=User)
def registrar_usuario_endpoint(usuario: User):
    return registrar_usuario(usuario)

@router.get("/", response_model=list[User])
def listar_usuarios_endpoint():
    return listar_usuarios()