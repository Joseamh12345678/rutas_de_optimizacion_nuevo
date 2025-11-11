import asyncio
from .estado import state

async def simular_movimiento():
    state["sim_running"] = True
    while state["sim_running"]:
        geom = state["ruta_geom"]
        idx = state["current_index"]
        if not geom or idx >= len(geom):
            state["sim_running"] = False
            break
        pos = geom[idx]
        state["current_index"] += 1
        for ws in state["websockets"]:
            await ws.send_json({"type": "position", "lat": pos[0], "lng": pos[1]})
        await asyncio.sleep(0.6)