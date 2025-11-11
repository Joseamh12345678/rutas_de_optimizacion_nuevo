from fastapi import WebSocket, WebSocketDisconnect
from .estado import state

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state["websockets"].add(websocket)
    try:
        if state["ruta_logica"] and state["ruta_geom"]:
            await websocket.send_json({
                "type": "route",
                "ruta_logica": [{"lat": p[0], "lng": p[1]} for p in state["ruta_logica"]],
                "ruta_geom": [{"lat": p[0], "lng": p[1]} for p in state["ruta_geom"]]
            })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        state["websockets"].remove(websocket)