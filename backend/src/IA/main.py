from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.src.services.geocoding import geocode
from backend.src.services.optimize import optimize_route
from .estado import state
from .utils import distancia_m, build_full_geometry
from .routing import calcular_ruta_nearest_neighbor
from .simulacion import simular_movimiento
from .websocket import websocket_endpoint

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/start")
async def start_route(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    inicio = geocode(data.get("inicio")) if isinstance(data.get("inicio"), str) else tuple(data.get("inicio"))
    entregas = [geocode(e) if isinstance(e, str) else tuple(e) for e in data.get("entregas", [])]
    entregas = [e for e in entregas if e]

    if not inicio or not entregas:
        return {"error": "inicio y entregas requeridos"}

    try:
        locations = [f"{inicio[0]},{inicio[1]}"] + [f"{e[0]},{e[1]}" for e in entregas]
        optimized = optimize_route(locations)
        ruta_logica = [(float(p["location"]["latLng"]["latitude"]), float(p["location"]["latLng"]["longitude"])) for p in optimized["routes"][0]["legs"]]
    except Exception:
        ruta_logica = calcular_ruta_nearest_neighbor(inicio, entregas)

    state["ruta_logica"] = ruta_logica
    state["ruta_geom"] = build_full_geometry(ruta_logica)
    state["current_index"] = 0

    for ws in state["websockets"]:
        await ws.send_json({
            "type": "route",
            "ruta_logica": [{"lat": p[0], "lng": p[1]} for p in ruta_logica],
            "ruta_geom": [{"lat": p[0], "lng": p[1]} for p in state["ruta_geom"]]
        })

    if not state["sim_running"]:
        background_tasks.add_task(simular_movimiento)

    return {"ok": True}

@app.post("/add_delivery")
async def add_delivery(request: Request):
    data = await request.json()
    nuevo = geocode(data.get("address")) if "address" in data else (float(data.get("lat")), float(data.get("lon")))
    ruta = state["ruta_logica"]
    if not ruta or not nuevo:
        return {"error": "ruta o entrega inválida"}

    mejor_pos = min(range(1, len(ruta)), key=lambda i: distancia_m(ruta[i - 1], nuevo) + distancia_m(nuevo, ruta[i]) - distancia_m(ruta[i - 1], ruta[i]))
    ruta.insert(mejor_pos, nuevo)
    state["ruta_logica"] = ruta
    state["ruta_geom"] = build_full_geometry(ruta)

    for ws in state["websockets"]:
        await ws.send_json({
            "type": "route_update",
            "ruta_logica": [{"lat": p[0], "lng": p[1]} for p in ruta],
            "ruta_geom": [{"lat": p[0], "lng": p[1]} for p in state["ruta_geom"]]
        })

    return {"ok": True, "position_inserted_at": mejor_pos}

@app.post("/push_gps")
async def push_gps(request: Request):
    data = await request.json()
    lat, lon = float(data["lat"]), float(data["lon"])
    for ws in state["websockets"]:
        await ws.send_json({"type": "position", "lat": lat, "lng": lon})
    return {"ok": True}

app.websocket("/ws")(websocket_endpoint)