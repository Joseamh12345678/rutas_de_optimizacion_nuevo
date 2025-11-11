from geopy.distance import geodesic
from backend.src.services.navigation_sdk import get_route

def distancia_m(a, b):
    return geodesic(a, b).meters

def interpolate_segment(a, b, meters_per_step=20):
    dist_m = distancia_m(a, b)
    if dist_m == 0:
        return [a]
    steps = max(1, int(dist_m / meters_per_step))
    return [(a[0] + (b[0] - a[0]) * i / steps, a[1] + (b[1] - a[1]) * i / steps) for i in range(steps + 1)]

def build_full_geometry(ruta_logica):
    full = []
    for i in range(len(ruta_logica) - 1):
        a, b = ruta_logica[i], ruta_logica[i + 1]
        route_info = get_route(f"{a[0]},{a[1]}", f"{b[0]},{b[1]}")
        if route_info and "polyline" in route_info:
            # Si tienes decodificación de polilínea, úsala aquí
            pass
        else:
            seg = interpolate_segment(a, b)
            full.extend(seg if not full or full[-1] != seg[0] else seg[1:])
    return full