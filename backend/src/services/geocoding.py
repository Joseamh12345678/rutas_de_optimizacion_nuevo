from backend.src.services.utils import get

def geocode(address: str, region: str = None):  # ✅ Se agrega parámetro opcional
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address}
    if region:
        params["region"] = region  # ✅ Se incluye en la petición si se proporciona

    data = get(url, params)
    if data["results"]:
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None