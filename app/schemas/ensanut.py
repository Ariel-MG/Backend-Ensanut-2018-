from pydantic import BaseModel, Field
from typing import Optional


class TablaInfo(BaseModel):
    """Información resumida de una tabla de la ENSANUT 2018."""
    nombre: str = Field(..., description="Nombre de la tabla en la base de datos.")
    dominio: str = Field(..., description="Dominio: 'CN' (Nutrición) o 'CS' (Salud).")
    descripcion_dominio: str = Field(..., description="Nombre completo del cuestionario.")
    total_registros: int = Field(..., description="Cantidad total de registros en la tabla.")
    total_columnas: int = Field(..., description="Cantidad de columnas en la tabla.")


class ListaTablasResponse(BaseModel):
    """Respuesta con la lista completa de tablas disponibles."""
    total_tablas: int = Field(..., description="Número total de tablas disponibles.")
    tablas: list[TablaInfo] = Field(..., description="Lista de tablas con sus metadatos.")


class ColumnaInfo(BaseModel):
    """Información de una columna incluyendo su descripción del diccionario de datos."""
    nombre: str = Field(..., description="Nombre de la columna en la tabla.")
    descripcion: Optional[str] = Field(None, description="Descripción según el diccionario de datos.")
    tipo_de_dato: Optional[str] = Field(None, description="Tipo de dato documentado en el diccionario.")
    rangos_claves: Optional[str] = Field(None, description="Rangos o claves válidos para esta columna.")


class ColumnasResponse(BaseModel):
    """Respuesta con las columnas de una tabla específica."""
    tabla: str = Field(..., description="Nombre de la tabla consultada.")
    total_columnas: int = Field(..., description="Número total de columnas.")
    columnas: list[ColumnaInfo] = Field(..., description="Lista de columnas con metadatos.")


class RespuestaPaginada(BaseModel):
    """Respuesta genérica paginada para registros dinámicos de cualquier tabla."""
    tabla: str = Field(..., description="Nombre de la tabla consultada.")
    total: int = Field(..., description="Total de registros que coinciden con los filtros.")
    pagina: int = Field(..., description="Número de la página actual.")
    limite: int = Field(..., description="Registros por página.")
    hay_mas: bool = Field(..., description="Indica si hay más páginas disponibles.")
    columnas: list[str] = Field(..., description="Lista de nombres de columnas devueltas.")
    registros: list[dict[str, Optional[str]]] = Field(
        ..., description="Lista de registros. Cada registro es un diccionario columna→valor (todos los valores son strings o null)."
    )


class DiccionarioEntrada(BaseModel):
    """Una entrada del diccionario de datos de la ENSANUT."""
    nombre_de_la_db: Optional[str] = Field(None, description="Base de datos de origen.")
    nombre_del_conjunto: Optional[str] = Field(None, description="Conjunto de datos.")
    nombre_de_la_tabla: str = Field(..., description="Tabla a la que pertenece la columna.")
    nombre_de_la_columna: str = Field(..., description="Nombre de la columna.")
    descripcion: Optional[str] = Field(None, description="Descripción de la variable.")
    tipo_de_dato: Optional[str] = Field(None, description="Tipo de dato.")
    rangos_claves: Optional[str] = Field(None, description="Valores válidos o rangos.")


class DiccionarioResponse(BaseModel):
    """Respuesta paginada de búsqueda en el diccionario de datos."""
    total: int = Field(..., description="Total de entradas que coinciden con la búsqueda.")
    pagina: int = Field(..., description="Página actual.")
    limite: int = Field(..., description="Resultados por página.")
    hay_mas: bool = Field(..., description="Si hay más páginas.")
    resultados: list[DiccionarioEntrada] = Field(..., description="Entradas del diccionario.")
