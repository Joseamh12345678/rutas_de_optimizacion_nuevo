from backend.src.services.utils import post

def optimize_route(locations: list):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    body = {
        "origin": {"address": {"formattedAddress": locations[0]}},
        "destination": {"address": {"formattedAddress": locations[-1]}},
        "intermediates": [{"address": {"formattedAddress": loc}} for loc in locations[1:-1]],
        "travelMode": "DRIVE"
    }
    return post(url, body)