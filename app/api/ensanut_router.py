from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import engine, get_db
from app.schemas.ensanut import (
    ColumnasResponse,
    DiccionarioResponse,
    ListaTablasResponse,
    RespuestaPaginada,
)
from app.services.data_service import (
    buscar_diccionario,
    generar_csv_stream,
    obtener_columnas,
    obtener_registros,
    obtener_tablas,
    _validar_tabla,
    _obtener_columnas_validas,
    _validar_columnas,
)

router = APIRouter(prefix="/api", tags=["Extracción de Datos"])

# Parámetros reservados que no deben tratarse como filtros de columna
_PARAMS_RESERVADOS = {"pagina", "limite", "columnas"}


def _extraer_filtros(request: Request) -> dict[str, str]:
    """
    Extrae los filtros dinámicos de los query params.
    Todo parámetro que no sea pagina, limite o columnas se considera un filtro de columna.

    Args:
        request: Objeto Request de FastAPI.

    Returns:
        dict[str, str]: Diccionario de filtros columna→valor.
    """
    return {
        k: v for k, v in request.query_params.items()
        if k not in _PARAMS_RESERVADOS
    }


def _parsear_columnas(columnas: Optional[str]) -> Optional[list[str]]:
    """
    Convierte el string de columnas separadas por coma en una lista.

    Args:
        columnas: String con nombres de columna separados por coma, o None.

    Returns:
        Optional[list[str]]: Lista de nombres de columna, o None si no se especificaron.
    """
    if not columnas:
        return None
    return [c.strip() for c in columnas.split(",") if c.strip()]


# ──────────────────────────────────────────────
# Endpoint 1: Listar tablas
# ──────────────────────────────────────────────
@router.get(
    "/tablas",
    response_model=ListaTablasResponse,
    summary="Listar tablas disponibles de la ENSANUT",
    description="Devuelve la lista completa de las 35 tablas de datos de la ENSANUT 2018 "
                "con su dominio (Nutrición o Salud), conteo aproximado de registros y número de columnas.",
    response_description="Lista de tablas con metadatos básicos.",
    tags=["Tablas"],
)
def listar_tablas(db: Session = Depends(get_db)) -> ListaTablasResponse:
    """
    Controlador para obtener el catálogo de tablas disponibles.

    Args:
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        ListaTablasResponse: Catálogo de tablas con metadatos.
    """
    return obtener_tablas(db=db)


# ──────────────────────────────────────────────
# Endpoint 2: Obtener columnas de una tabla
# ──────────────────────────────────────────────
@router.get(
    "/tablas/{tabla}/columnas",
    response_model=ColumnasResponse,
    summary="Obtener columnas de una tabla",
    description="Devuelve los nombres y descripciones de todas las columnas de la tabla especificada. "
                "Las descripciones provienen del diccionario de datos oficial de la ENSANUT.",
    response_description="Lista de columnas con descripción, tipo de dato y rangos válidos.",
    tags=["Tablas"],
)
def obtener_columnas_tabla(
    tabla: str = Path(..., description="Nombre de la tabla (ej. CS_ADULTOS, CN_ANTROPOMETRIA)."),
    db: Session = Depends(get_db),
) -> ColumnasResponse:
    """
    Controlador para obtener las columnas y sus descripciones de una tabla.

    Args:
        tabla: Nombre de la tabla a consultar.
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        ColumnasResponse: Columnas de la tabla con metadatos del diccionario.
    """
    return obtener_columnas(db=db, tabla=tabla)


# ──────────────────────────────────────────────
# Endpoint 3: Obtener registros paginados
# ──────────────────────────────────────────────
@router.get(
    "/tablas/{tabla}/registros",
    response_model=RespuestaPaginada,
    summary="Obtener registros paginados con filtros",
    description="Extrae registros de cualquier tabla de la ENSANUT con paginación, "
                "selección de columnas y filtros dinámicos. Los filtros se pasan como query params "
                "usando el nombre exacto de la columna (ej. ?SEXO=1&ENT=09).",
    response_description="Registros paginados con metadatos de la consulta.",
    tags=["Datos"],
)
def obtener_registros_tabla(
    request: Request,
    tabla: str = Path(..., description="Nombre de la tabla a consultar."),
    pagina: int = Query(1, ge=1, description="Número de página (inicia en 1)."),
    limite: int = Query(15, ge=1, le=100, description="Registros por página (máximo 100)."),
    columnas: Optional[str] = Query(None, description="Columnas a incluir, separadas por coma (ej. UPM,EDAD,SEXO). Si se omite, devuelve todas."),
    db: Session = Depends(get_db),
) -> RespuestaPaginada:
    """
    Controlador para obtener datos paginados con filtros dinámicos.

    Args:
        request: Objeto Request para extraer filtros de query params.
        tabla: Nombre de la tabla a consultar.
        pagina: Página actual solicitada por el cliente.
        limite: Límite de registros a extraer.
        columnas: Columnas seleccionadas separadas por coma.
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        RespuestaPaginada: Registros paginados con metadatos.
    """
    return obtener_registros(
        db=db,
        tabla=tabla,
        pagina=pagina,
        limite=limite,
        columnas_seleccionadas=_parsear_columnas(columnas),
        filtros=_extraer_filtros(request),
    )


# ──────────────────────────────────────────────
# Endpoint 4: Exportar tabla a CSV
# ──────────────────────────────────────────────
@router.get(
    "/tablas/{tabla}/exportar",
    summary="Exportar tabla a archivo CSV",
    description="Genera un archivo CSV al vuelo con los datos de la tabla. "
                "Acepta los mismos filtros y selección de columnas que el endpoint de registros. "
                "El archivo se transmite por streaming sin cargarlo completo en memoria.",
    response_description="Archivo CSV descargable como flujo de bytes.",
    tags=["Exportación"],
)
def exportar_tabla_csv(
    request: Request,
    tabla: str = Path(..., description="Nombre de la tabla a exportar."),
    columnas: Optional[str] = Query(None, description="Columnas a incluir, separadas por coma."),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Controlador para exportar datos filtrados en formato CSV.

    Args:
        request: Objeto Request para extraer filtros de query params.
        tabla: Nombre de la tabla a exportar.
        columnas: Columnas seleccionadas separadas por coma.
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        StreamingResponse: Flujo CSV listo para descarga.
    """
    tabla_validada = _validar_tabla(tabla)
    columnas_validas = _obtener_columnas_validas(db, tabla_validada)
    filtros = _extraer_filtros(request)
    cols_parseadas = _parsear_columnas(columnas)

    # Validar columnas y filtros antes de iniciar el stream
    if cols_parseadas:
        cols_parseadas = _validar_columnas(cols_parseadas, columnas_validas, tabla_validada)
    if filtros:
        _validar_columnas(list(filtros.keys()), columnas_validas, tabla_validada)

    stream = generar_csv_stream(
        engine=engine,
        tabla=tabla_validada,
        columnas_seleccionadas=cols_parseadas,
        filtros=filtros,
    )

    response = StreamingResponse(stream, media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={tabla_validada}_ensanut_2018.csv"
    return response


# ──────────────────────────────────────────────
# Endpoint 5: Buscar en el diccionario de datos
# ──────────────────────────────────────────────
@router.get(
    "/diccionario",
    response_model=DiccionarioResponse,
    summary="Buscar en el diccionario de datos",
    description="Busca variables por palabra clave en el nombre o descripción de las columnas "
                "del diccionario de datos oficial de la ENSANUT 2018. "
                "Opcionalmente filtra por tabla específica.",
    response_description="Resultados paginados de la búsqueda en el diccionario.",
    tags=["Diccionario"],
)
def buscar_en_diccionario(
    termino: Optional[str] = Query(None, description="Palabra clave a buscar en nombre o descripción de columna (ej. glucosa, peso, diabetes)."),
    tabla: Optional[str] = Query(None, description="Filtrar por nombre de tabla específica (ej. CS_ADULTOS)."),
    pagina: int = Query(1, ge=1, description="Número de página."),
    limite: int = Query(20, ge=1, le=100, description="Resultados por página (máximo 100)."),
    db: Session = Depends(get_db),
) -> DiccionarioResponse:
    """
    Controlador para búsqueda en el diccionario de datos.

    Args:
        termino: Palabra clave para buscar.
        tabla: Nombre de tabla para filtrar resultados.
        pagina: Página actual.
        limite: Resultados por página.
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        DiccionarioResponse: Resultados paginados del diccionario.
    """
    return buscar_diccionario(
        db=db,
        termino=termino,
        tabla_filtro=tabla,
        pagina=pagina,
        limite=limite,
    )
