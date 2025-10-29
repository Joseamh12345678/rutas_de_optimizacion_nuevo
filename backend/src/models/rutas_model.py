from pydantic import BaseModel, Field
from typing import Optional

class Ruta(BaseModel):
    nombre: str
    direccion: str
    latitud: Optional[float] = Field(default=None)
    longitud: Optional[float] = Field(default=None)
    distancia_km: Optional[float] = Field(default=None)
    duracion_min: Optional[float] = Field(default=None)