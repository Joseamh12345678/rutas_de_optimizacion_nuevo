import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def get(url, params):
    params["key"] = API_KEY
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.HTTPError as e:
        print("GET error:", e.response.text)  # ✅ Mensaje de error detallado
        raise
    return response.json()

def post(url, body, headers=None):
    headers = headers or {}
    headers["X-Goog-Api-Key"] = API_KEY
    headers["Content-Type"] = "application/json"
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as e:
        print("POST error:", e.response.text)  # ✅ Mensaje de error detallado
        raise
    return response.json()