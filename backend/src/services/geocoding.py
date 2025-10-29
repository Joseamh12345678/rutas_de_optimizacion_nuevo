from backend.src.services.utils import get

def geocode(address: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address}
    data = get(url, params)
    if data["results"]:
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None