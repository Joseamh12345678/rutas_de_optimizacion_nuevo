from backend.src.services.utils import post
from polyline.codec import decode  # ✅ Agregado para decodificar geometría

def optimize_route(locations: list):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    body = {
        "origin": {"address": {"formattedAddress": locations[0]}},
        "destination": {"address": {"formattedAddress": locations[-1]}},
        "intermediates": [{"address": {"formattedAddress": loc}} for loc in locations[1:-1]],
        "travelMode": "DRIVE"
    }
    data = post(url, body)

    # ✅ Decodificar geometría si está disponible
    if "routes" in data and "polyline" in data["routes"][0]:
        encoded = data["routes"][0]["polyline"]["encodedPolyline"]
        decoded_coords = decode(encoded)  # [(lat, lon), ...]
        return {"decoded_geometry": decoded_coords, "raw": data}

    return data