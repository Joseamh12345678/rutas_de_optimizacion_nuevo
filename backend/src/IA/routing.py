from .utils import distancia_m

def calcular_ruta_nearest_neighbor(inicio, pendientes):
    pendientes_copy = pendientes.copy()
    ruta = [inicio]
    while pendientes_copy:
        last = ruta[-1]
        siguiente = min(pendientes_copy, key=lambda p: distancia_m(last, p))
        ruta.append(siguiente)
        pendientes_copy.remove(siguiente)
    return ruta