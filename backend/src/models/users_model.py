from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    nombre: str
    correo: EmailStr
    edad: Optional[int] = None