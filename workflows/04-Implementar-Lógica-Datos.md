# Workflow Claude Code: 04 - Implementar Lógica de Datos

**Objetivo de este paso:**
Crear la capa de servicios que se encargará de ejecutar las consultas a la base de datos a través de SQLAlchemy, implementando estrictamente la paginación para manejar el volumen masivo de datos de la ENSANUT.

## Instrucciones de Ejecución:
Por favor, interactúa con el sistema de archivos para crear la lógica de acceso a datos:

### 1. Crear el Servicio de Datos
Crea un archivo llamado `app/services/data_service.py` e implementa el siguiente código. Presta especial atención a la documentación (docstrings) y al manejo de `limit` y `offset`.

```python
from sqlalchemy.orm import Session
from app.models.ensanut import EnsanutRecord
from typing import Dict, Any

def get_paginated_records(db: Session, page: int = 1, limit: int = 15) -> Dict[str, Any]:
    """
    Extrae los registros de la ENSANUT 2018 de forma paginada para no saturar la memoria.
    
    Args:
        db (Session): Sesión activa de SQLAlchemy conectada a Oracle.
        page (int): Número de la página solicitada (inicia en 1).
        limit (int): Cantidad máxima de registros a devolver por página.
        
    Returns:
        Dict[str, Any]: Un diccionario estructurado que coincide con el esquema PaginatedResponse,
                        incluyendo metadatos de paginación y la lista de registros.
    """
    # Calcular el desplazamiento (offset)
    offset = (page - 1) * limit
    
    # Contar el total de registros en la tabla (para calcular páginas totales en el front-end)
    total_records = db.query(EnsanutRecord).count()
    
    # Extraer solo la fracción de datos solicitada
    records = db.query(EnsanutRecord).offset(offset).limit(limit).all()
    
    # Determinar si existen más páginas disponibles
    has_more = (offset + limit) < total_records
    
    return {
        "total": total_records,
        "page": page,
        "limit": limit,
        "has_more": has_more,
        "records": records
    }
2. Confirmación
Responde confirmando que el archivo app/services/data_service.py ha sido creado con su respectiva lógica de paginación y docstrings en formato Google. Indica que el sistema está listo para avanzar al paso "05-Desarrollar-Endpoints-y-Exportacion.md".