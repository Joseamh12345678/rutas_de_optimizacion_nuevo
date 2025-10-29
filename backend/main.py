from fastapi import FastAPI
from backend.src.routes.rutas_route import router as rutas_router
from backend.src.routes.geocode_route import router as geocode_router
from backend.src.routes.directions_route import router as directions_router
from backend.src.routes.matrix_route import router as matrix_router
from backend.src.routes.optimize_route import router as optimize_router
from backend.src.routes.users_route import router as users_router


app = FastAPI()

app.include_router(rutas_router)
app.include_router(geocode_router)
app.include_router(directions_router)
app.include_router(matrix_router)
app.include_router(optimize_router)
app.include_router(users_router)