import os
import time
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import openrouteservice
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os

load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

# -----------------------
# CONFIGURACIÓN
# -----------------------
USE_ORS = bool(ORS_API_KEY)

METERS_PER_STEP = 20
SIM_STEP_SECONDS = 0.6
PORT = 5000

# -----------------------
# Inicializar app
# -----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

ors_client = None
if USE_ORS:
    ors_client = openrouteservice.Client(key=ORS_API_KEY)

geolocator = Nominatim(user_agent="ia_rutas_app")

# -----------------------
# Estado global
# -----------------------
state = {
    "ruta_logica": [],
    "ruta_geom": [],
    "sim_thread": None,
    "sim_running": False,
    "current_index": 0
}

# -----------------------
# UTILIDADES
# -----------------------
def distancia_m(a, b):
    return geodesic(a, b).meters

def geocode_address(addr):
    try:
        loc = geolocator.geocode(addr, timeout=10)
        if loc:
            return (loc.latitude, loc.longitude)
    except Exception as e:
        print("Geocode error:", e)
    return None

def interpolate_segment(a, b, meters_per_step=METERS_PER_STEP):
    dist_m = distancia_m(a, b)
    if dist_m == 0:
        return [a]
    steps = max(1, int(dist_m / meters_per_step))
    points = []
    for i in range(steps + 1):
        frac = i / steps
        lat = a[0] + (b[0] - a[0]) * frac
        lon = a[1] + (b[1] - a[1]) * frac
        points.append((lat, lon))
    return points

def get_route_geom_using_ors(a, b):
    try:
        coords = [(a[1], a[0]), (b[1], b[0])]
        resp = ors_client.directions(coords, profile='driving-car', format='geojson')
        coords_list = resp['features'][0]['geometry']['coordinates']
        return [(lat, lon) for lon, lat in coords_list]
    except Exception as e:
        print("ORS error:", e)
        return None

def build_full_geometry(ruta_logica):
    if USE_ORS and ors_client:
        full = []
        for i in range(len(ruta_logica) - 1):
            a = ruta_logica[i]
            b = ruta_logica[i + 1]
            seg = get_route_geom_using_ors(a, b)
            if seg is None:
                full = None
                break
            if full and full[-1] == seg[0]:
                full.extend(seg[1:])
            else:
                full.extend(seg)
        if full is not None and len(full) > 0:
            return full

    # fallback
    full = []
    for i in range(len(ruta_logica) - 1):
        seg = interpolate_segment(ruta_logica[i], ruta_logica[i + 1])
        if full and full[-1] == seg[0]:
            full.extend(seg[1:])
        else:
            full.extend(seg)
    return full

# -----------------------
# ALGORITMO
# -----------------------
def calcular_ruta_nearest_neighbor(inicio, pendientes):
    pendientes_copy = pendientes.copy()
    ruta = [inicio]
    while pendientes_copy:
        last = ruta[-1]
        siguiente = min(pendientes_copy, key=lambda p: distancia_m(last, p))
        ruta.append(siguiente)
        pendientes_copy.remove(siguiente)
    return ruta

# -----------------------
# SIMULACIÓN
# -----------------------
def sim_thread_func():
    print("[sim] hilo iniciado")
    state['sim_running'] = True
    while state['sim_running']:
        geom = state.get('ruta_geom', [])
        idx = state.get('current_index', 0)
        if not geom or idx >= len(geom):
            state['sim_running'] = False
            break
        pos = geom[idx]
        state['current_index'] = idx + 1
        socketio.emit('position', {'lat': pos[0], 'lng': pos[1]})
        time.sleep(SIM_STEP_SECONDS)
    print("[sim] hilo finalizado")

# -----------------------
# RUTAS HTTP
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_route():
    data = request.get_json(force=True)
    inicio = None
    if "inicio" in data:
        inc = data.get("inicio")
        if isinstance(inc, (list, tuple)) and len(inc) == 2:
            inicio = (float(inc[0]), float(inc[1]))
        elif isinstance(inc, str):
            inicio = geocode_address(inc)
    elif "address" in data:
        inicio = geocode_address(data.get("address"))

    entregas_raw = data.get("entregas", [])
    entregas = []
    for item in entregas_raw:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            entregas.append((float(item[0]), float(item[1])))
        elif isinstance(item, str):
            geo = geocode_address(item)
            if geo:
                entregas.append(geo)

    if not inicio or not entregas:
        return jsonify({"error": "inicio y entregas requeridas (coords o direcciones)"}), 400

    ruta_logica = calcular_ruta_nearest_neighbor(inicio, entregas)
    state['ruta_logica'] = ruta_logica
    ruta_geom = build_full_geometry(ruta_logica)
    state['ruta_geom'] = ruta_geom
    state['current_index'] = 0

    socketio.emit('route', {
        'ruta_logica': [{'lat': p[0], 'lng': p[1]} for p in ruta_logica],
        'ruta_geom': [{'lat': p[0], 'lng': p[1]} for p in ruta_geom]
    })
    if not state['sim_running']:
        t = threading.Thread(target=sim_thread_func, daemon=True)
        state['sim_thread'] = t
        t.start()

    return jsonify({"ok": True})

@app.route("/add_delivery", methods=["POST"])
def add_delivery():
    data = request.get_json(force=True)
    nuevo = None
    if "address" in data:
        nuevo = geocode_address(data.get("address"))
        if not nuevo:
            return jsonify({"error": "no se pudo geocodificar la dirección"}), 400
    else:
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is None or lon is None:
            return jsonify({"error": "proporciona lat y lon o address"}), 400
        nuevo = (float(lat), float(lon))

    ruta = state.get('ruta_logica', [])
    if not ruta:
        return jsonify({"error": "no hay ruta en estado"}), 400

    mejor_pos = 1
    menor_aumento = float('inf')
    for i in range(1, len(ruta)):
        a = ruta[i - 1]
        b = ruta[i]
        aumento = distancia_m(a, nuevo) + distancia_m(nuevo, b) - distancia_m(a, b)
        if aumento < menor_aumento:
            menor_aumento = aumento
            mejor_pos = i
    ruta.insert(mejor_pos, nuevo)
    state['ruta_logica'] = ruta

    ruta_geom = build_full_geometry(ruta)
    state['ruta_geom'] = ruta_geom

    socketio.emit('route_update', {
        'ruta_logica': [{'lat': p[0], 'lng': p[1]} for p in ruta],
        'ruta_geom': [{'lat': p[0], 'lng': p[1]} for p in ruta_geom]
    })
    return jsonify({"ok": True, "position_inserted_at": mejor_pos})

@app.route("/push_gps", methods=["POST"])
def push_gps():
    """Recibe {"lat": ..., "lon": ...} y emite la posición a todos los clientes."""
    data = request.get_json(force=True)
    lat = float(data.get("lat"))
    lon = float(data.get("lon"))
    socketio.emit('position', {'lat': lat, 'lng': lon})
    return jsonify({"ok": True})

# -----------------------
# SOCKET events
# -----------------------
@socketio.on('connect')
def on_connect():
    print("Cliente conectado")
    if state.get('ruta_logica') and state.get('ruta_geom'):
        emit('route', {
            'ruta_logica': [{'lat': p[0], 'lng': p[1]} for p in state['ruta_logica']],
            'ruta_geom': [{'lat': p[0], 'lng': p[1]} for p in state['ruta_geom']]
        })

# -----------------------
# MAIN
# -----------------------
if __name__ == "__main__":
    print("Iniciando servidor Flask + SocketIO en puerto", PORT)
    socketio.run(app, host="0.0.0.0", port=PORT)
