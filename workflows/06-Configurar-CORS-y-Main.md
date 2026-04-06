# Workflow Claude Code: 06 - Configurar CORS y Main

**Objetivo de este paso:**
Actualizar el punto de entrada principal de la aplicación (`app/main.py`) para integrar el enrutador de la ENSANUT y configurar el middleware de CORS, permitiendo la comunicación fluida con el frontend en React.

## Instrucciones de Ejecución:
Por favor, interactúa con el sistema de archivos para realizar las siguientes tareas:

### 1. Actualizar main.py
Abre el archivo `app/main.py` (que actualmente solo tiene el health check) y sobrescríbelo por completo con el siguiente código. Presta atención a las importaciones y a la configuración del `CORSMiddleware`.

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Importar el enrutador de los datos
from app.api.ensanut_router import router as ensanut_router

app = FastAPI(
    title="API de Extracción ENSANUT 2018",
    description="Backend para consulta y extracción de datos del Data Science Lab - Universidad Anáhuac",
    version="1.0.0"
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Se habilitan los puertos estándar de desarrollo frontend (Vite/React)
origenes_permitidos = [
    "http://localhost:5173",  # Puerto por defecto de Vite
    "http://localhost:3000",  # Puerto alternativo clásico
    "[http://127.0.0.1:5173](http://127.0.0.1:5173)",
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

@app.get("/", summary="Health Check", tags=["Sistema"])
def health_check():
    """
    Verifica que el servidor FastAPI esté en ejecución.
    
    Returns:
        JSONResponse: Un mensaje de estado confirmando que la API está activa.
    """
    return JSONResponse(content={"estado": "activo", "mensaje": "API de ENSANUT 2018 operando correctamente."})
2. Confirmación Final
Responde confirmando que el archivo app/main.py ha sido actualizado exitosamente con las políticas de CORS y la inclusión del router.
Informa al usuario que la arquitectura del Back-end está terminada y que puede iniciar el servidor ejecutando el comando: uvicorn app.main:app --reload