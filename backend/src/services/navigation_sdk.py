from backend.src.services.utils import get

def get_route(origin: str, destination: str):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving"
    }
    data = get(url, params)
    if data["routes"]:
        leg = data["routes"][0]["legs"][0]
        return {
            "distance_km": leg["distance"]["value"] / 1000,
            "duration_min": leg["duration"]["value"] / 60
        }
    return None