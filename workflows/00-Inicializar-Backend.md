# Workflow Claude Code: 00 - Inicializar Backend

**Objetivo de este paso:**
Crear la estructura base de directorios del proyecto, inicializar los módulos de Python y preparar el punto de entrada principal (`main.py`) siguiendo la arquitectura de capas definida en las reglas globales.

## Instrucciones de Ejecución:
Por favor, interactúa con el sistema de archivos para realizar las siguientes tareas secuencialmente:

### 1. Estructura de Directorios
Crea la siguiente estructura de carpetas en el directorio actual:
- `app/`
- `app/api/`
- `app/core/`
- `app/models/`
- `app/schemas/`
- `app/services/`

### 2. Inicialización de Módulos
Crea un archivo `__init__.py` vacío dentro de cada una de las carpetas recién creadas (incluyendo `app/`) para que Python las reconozca como paquetes/módulos válidos.

### 3. Archivos de Configuración Base
- Crea un archivo `.gitignore` estándar para Python (asegúrate de ignorar `__pycache__/`, entornos virtuales como `venv/`, `.env` y archivos `.csv` generados).
- Crea un archivo vacío llamado `requirements.txt` en la raíz del proyecto.

### 4. Creación del Punto de Entrada (main.py)
Crea el archivo `app/main.py` con una estructura muy básica de FastAPI que incluya un endpoint de "health check". Usa este código:

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="API de Extracción ENSANUT 2018",
    description="Backend para consulta y extracción de datos del Data Science Lab - Universidad Anáhuac",
    version="1.0.0"
)

@app.get("/", summary="Health Check", tags=["Sistema"])
def health_check():
    """
    Verifica que el servidor FastAPI esté en ejecución.
    
    Returns:
        JSONResponse: Un mensaje de estado confirmando que la API está activa.
    """
    return JSONResponse(content={"estado": "activo", "mensaje": "API de ENSANUT 2018 operando correctamente."})
5. Confirmación
Responde confirmando que la estructura de carpetas y el main.py fueron creados exitosamente. No instales dependencias todavía.


***

**Nota rápida para ti (como desarrollador humano):** Dado que estás en tu computadora local, no olvides crear tu entorno virtual **antes** de correr el paso 01 para que las librerías no se te instalen de forma global. 
Si estás en Windows o Mac/Linux, solo corre esto en tu terminal:
`python -m venv venv` 
Y actívalo (en Windows: `venv\Scripts\activate` | en Mac/Linux: `source venv/bin/activate`).