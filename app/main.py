from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.ensanut_router import router as ensanut_router
from app.api.metricas_router import router as metricas_router

app = FastAPI(
    title="API de Extracción ENSANUT 2018",
    description="Backend para consulta y extracción de datos del Data Science Lab - Universidad Anáhuac",
    version="1.0.0"
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Se habilitan los puertos estándar de desarrollo frontend (Vite/React)
origenes_permitidos = [
    "http://localhost:5173",    # Puerto por defecto de Vite
    "http://localhost:3000",    # Puerto alternativo clásico
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Integración de Rutas
app.include_router(ensanut_router)
app.include_router(metricas_router)

@app.get("/", summary="Health Check", tags=["Sistema"])
def health_check():
    """
    Verifica que el servidor FastAPI esté en ejecución.

    Returns:
        JSONResponse: Un mensaje de estado confirmando que la API está activa.
    """
    return JSONResponse(content={"estado": "activo", "mensaje": "API de ENSANUT 2018 operando correctamente."})
