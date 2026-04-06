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


# ── Schemas de Métricas ──

class EntidadDistribucion(BaseModel):
    """Distribución de registros para una entidad federativa."""
    codigo_entidad: Optional[str] = Field(None, description="Código INEGI de la entidad (01-32).")
    nombre_entidad: str = Field(..., description="Nombre del estado.")
    total: int = Field(..., description="Cantidad de registros en esta entidad.")
    porcentaje: float = Field(..., description="Porcentaje respecto al total nacional.")


class DistribucionEntidadResponse(BaseModel):
    """Distribución geográfica de registros por entidad federativa."""
    tabla: str = Field(..., description="Tabla de origen consultada.")
    total_registros: int = Field(..., description="Total de registros con entidad válida.")
    entidades: list[EntidadDistribucion] = Field(..., description="Distribución por estado, ordenada de mayor a menor.")


class SexoDistribucion(BaseModel):
    """Distribución por sexo."""
    codigo: Optional[str] = Field(None, description="Código del sexo (1=Hombre, 2=Mujer).")
    etiqueta: str = Field(..., description="Etiqueta legible del sexo.")
    total: int = Field(..., description="Cantidad de registros.")


class RangoEdadSexo(BaseModel):
    """Conteo por rango de edad y sexo para pirámide poblacional."""
    rango: str = Field(..., description="Rango de edad (ej. 0-4, 5-11, 12-19, 20-59, 60+).")
    sexo_codigo: Optional[str] = Field(None, description="Código del sexo.")
    sexo_etiqueta: str = Field(..., description="Etiqueta legible del sexo.")
    total: int = Field(..., description="Cantidad de registros en este grupo.")


class DemografiaResponse(BaseModel):
    """Distribución demográfica por sexo y rangos de edad."""
    tabla: str = Field(..., description="Tabla de origen consultada.")
    distribucion_sexo: list[SexoDistribucion] = Field(..., description="Distribución por sexo (para Pie Chart).")
    rangos_edad: list[RangoEdadSexo] = Field(..., description="Distribución por rango de edad y sexo (para histograma/pirámide).")


class IndicadorSalud(BaseModel):
    """Indicador de prevalencia de una condición de salud."""
    condicion: str = Field(..., description="Clave de la condición (diabetes, hipertension, colesterol).")
    etiqueta: str = Field(..., description="Nombre legible de la condición.")
    total_encuestados: int = Field(..., description="Total de personas que respondieron la pregunta.")
    total_positivos: int = Field(..., description="Total de personas con diagnóstico positivo.")
    prevalencia_porcentaje: float = Field(..., description="Prevalencia como porcentaje del total encuestado.")


class IndicadoresSaludResponse(BaseModel):
    """Indicadores de prevalencia de condiciones de salud clave en adultos."""
    tabla_origen: str = Field(..., description="Tabla de donde se extraen los indicadores.")
    indicadores: list[IndicadorSalud] = Field(..., description="Lista de indicadores de salud con prevalencias.")
