from fastapi import FastAPI
from app.routes import users, resources, assignments
import uvicorn

app = FastAPI(
    title="API para la aplicación Reservify",
    description="Una API para manejar usuarios, recursos y reservas usando FastAPI y MongoDB.",
    version="1.0.0"
)

# Incluir las rutas de cada módulo
app.include_router(users.router)
app.include_router(resources.router)
app.include_router(assignments.router)

# Ruta raíz
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Reservas"}

# Para ejecutar con `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
