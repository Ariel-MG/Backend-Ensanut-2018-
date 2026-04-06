# Workflow Claude Code: 05 - Desarrollar Endpoints y Exportación

**Objetivo de este paso:**
Crear el enrutador de FastAPI que expondrá los datos paginados de la ENSANUT e implementará la lógica de exportación masiva utilizando `pandas` y `StreamingResponse`.

## Instrucciones de Ejecución:
Por favor, interactúa con el sistema de archivos para crear los endpoints:

### 1. Crear el Router Principal
Crea un archivo llamado `app/api/ensanut_router.py`. Implementa el siguiente código cumpliendo con las reglas de docstrings nativos, metadatos de Swagger y la generación del CSV en memoria.

```python
import io
import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db, engine
from app.schemas.ensanut import PaginatedResponse
from app.services.data_service import get_paginated_records
from app.models.ensanut import EnsanutRecord

router = APIRouter(prefix="/api", tags=["Extracción de Datos"])

@router.get(
    "/records", 
    response_model=PaginatedResponse, 
    summary="Obtener registros paginados de la ENSANUT",
    description="Extrae una porción específica de los registros de la base de datos Oracle para su visualización segura en el Data Explorer sin comprometer la memoria del servidor."
)
def read_records(
    page: int = Query(1, ge=1, description="Número de página a consultar (Inicia en 1)"), 
    limit: int = Query(15, ge=1, le=100, description="Cantidad máxima de registros por página"), 
    db: Session = Depends(get_db)
):
    """
    Controlador para obtener datos paginados.
    
    Args:
        page (int): Página actual solicitada por el cliente.
        limit (int): Límite de registros a extraer.
        db (Session): Sesión inyectada de SQLAlchemy.
        
    Returns:
        dict: Diccionario estructurado validado por PaginatedResponse.
    """
    return get_paginated_records(db=db, page=page, limit=limit)


@router.get(
    "/export", 
    summary="Exportar datos a archivo CSV",
    description="Genera un archivo CSV al vuelo extrayendo los datos directamente de Oracle mediante Pandas. Retorna un flujo de bytes (stream) forzando la descarga en el navegador del analista."
)
def export_csv():
    """
    Controlador para la generación y descarga masiva de datos en formato CSV.
    Utiliza Pandas para optimizar la extracción y transformación de los datos.
    
    Returns:
        StreamingResponse: Archivo CSV listo para su descarga.
    """
    # Se utiliza Pandas directamente con el engine para máxima eficiencia en lectura SQL
    # Nota: En producción con tablas masivas, se recomienda usar chunksize
    query = f"SELECT * FROM {EnsanutRecord.__tablename__}"
    df = pd.read_sql(query, con=engine)
    
    # Crear un buffer en memoria para no escribir el archivo en el disco del servidor Red Hat
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    # Preparar el stream para la respuesta de FastAPI
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=ensanut_2018_exportacion.csv"
    
    return response
2. Confirmación
Responde confirmando que el archivo app/api/ensanut_router.py ha sido creado exitosamente, incorporando la lógica de Pandas y las descripciones para Swagger UI. Indica que el sistema está listo para avanzar al paso final: "06-Configurar-CORS-y-Main.md".