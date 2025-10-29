from backend.src.services.utils import get

def get_distance_matrix(origins: list, destinations: list):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "mode": "driving"
    }
    data = get(url, params)
    return data["rows"]