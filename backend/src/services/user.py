from backend.src.models.users_model import User

usuarios_db: list[User] = []
id_counter = 1

def registrar_usuario(usuario: User) -> User:
    global id_counter
    usuario.id = id_counter
    id_counter += 1
    usuarios_db.append(usuario)
    return usuario

def listar_usuarios() -> list[User]:
    return usuarios_db