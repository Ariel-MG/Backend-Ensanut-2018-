# Workflow Claude Code: 03 - Definir Modelos y Esquemas

**Objetivo de este paso:**
Crear los modelos ORM de SQLAlchemy para interactuar con las tablas de Oracle y los esquemas de Pydantic para validar los datos, estructurar las respuestas paginadas y autogenerar la documentación interactiva (Swagger UI).

## Instrucciones de Ejecución:
Por favor, interactúa con el sistema de archivos para crear los siguientes componentes:

### 1. Crear el Modelo ORM (SQLAlchemy)
Crea un archivo llamado `app/models/ensanut.py` e implementa una tabla representativa de la muestra poblacional (como base para las 34 tablas de la ENSANUT):

```python
from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class EnsanutRecord(Base):
    """
    Modelo ORM que representa una vista unificada o tabla específica 
    de la muestra poblacional de la ENSANUT 2018.
    """
    __tablename__ = "ensanut_muestra"

    id = Column(Integer, primary_key=True, index=True)
    folio_int = Column(String(50), index=True)
    edad = Column(Integer)
    sexo = Column(String(15))
    peso_kg = Column(Float)
    glucosa_mg_dl = Column(Float)
2. Crear los Esquemas de Validación (Pydantic)
Crea un archivo llamado app/schemas/ensanut.py. CRÍTICO: Asegúrate de usar Field con el parámetro description en todos los atributos para cumplir con las reglas de documentación del CLAUDE.md.

Python
from pydantic import BaseModel, Field
from typing import List

class EnsanutRecordBase(BaseModel):
    """Esquema base con los datos de interés de la ENSANUT 2018."""
    folio_int: str = Field(..., description="Identificador único de la vivienda y el hogar encuestado.")
    edad: int = Field(..., description="Edad en años cumplidos del participante al momento de la entrevista.")
    sexo: str = Field(..., description="Sexo del integrante del hogar (ej. Masculino, Femenino).")
    peso_kg: float = Field(..., description="Peso en kilogramos medido por el personal de salud.")
    glucosa_mg_dl: float = Field(..., description="Nivel de glucosa capilar en sangre medida en mg/dL.")

class EnsanutRecordResponse(EnsanutRecordBase):
    """Esquema de respuesta que incluye el identificador interno."""
    id: int = Field(..., description="Identificador primario interno de la base de datos.")

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    """Esquema genérico para estandarizar la paginación de datos masivos."""
    total: int = Field(..., description="Total de registros disponibles que coinciden con los filtros aplicados.")
    page: int = Field(..., description="Número de la página actual de resultados.")
    limit: int = Field(..., description="Cantidad de registros devueltos en la presente página.")
    has_more: bool = Field(..., description="Indica si existen más páginas de datos disponibles para consultar.")
    records: List[EnsanutRecordResponse] = Field(..., description="Lista estructurada de los registros de la ENSANUT.")
3. Confirmación
Responde confirmando que los archivos app/models/ensanut.py y app/schemas/ensanut.py han sido creados correctamente y que cumplen con las descripciones para el Swagger UI. Indica que el sistema está listo para avanzar al paso "04-Implementar-Logica-Datos.md".