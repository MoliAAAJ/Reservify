from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import assignments, resources, users, companies


app = FastAPI(
    title="API para la aplicación Reservify",
    description="Una API para manejar usuarios, recursos y reservas usando FastAPI y MongoDB.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir los orígenes definidos
    allow_credentials=True,  # Permitir cookies y encabezados de autenticación
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Incluir las rutas de cada módulo
app.include_router(users.router)
app.include_router(resources.router)
app.include_router(assignments.router)
app.include_router(companies.router)

# Ruta raíz
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Reservas"}

# Para ejecutar con `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
