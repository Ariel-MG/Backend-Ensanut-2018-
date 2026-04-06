import io
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models.ensanut import TABLAS_PERMITIDAS

# Caché a nivel de módulo para columnas válidas por tabla.
# Se puebla de forma lazy en el primer acceso a cada tabla.
_cache_columnas: dict[str, list[str]] = {}

# Mapeo de prefijo a descripción del dominio
_DOMINIOS: dict[str, str] = {
    "CN": "Cuestionario de Nutrición",
    "CS": "Cuestionario de Salud",
}


def _validar_tabla(tabla: str) -> str:
    """
    Valida que el nombre de tabla esté en la whitelist de tablas permitidas.
    Convierte a mayúsculas para consistencia con Oracle.

    Args:
        tabla: Nombre de la tabla recibido del cliente.

    Returns:
        str: Nombre de tabla en mayúsculas validado.

    Raises:
        HTTPException: 404 si la tabla no existe en la whitelist.
    """
    tabla_upper = tabla.upper()
    if tabla_upper not in TABLAS_PERMITIDAS:
        raise HTTPException(
            status_code=404,
            detail=f"La tabla '{tabla}' no existe. Consulta GET /api/tablas para ver las tablas disponibles."
        )
    return tabla_upper


def _obtener_columnas_validas(db: Session, tabla: str) -> list[str]:
    """
    Obtiene la lista de columnas válidas de una tabla desde los metadatos de Oracle.
    Utiliza caché en memoria para evitar consultas repetidas.

    Args:
        db: Sesión activa de SQLAlchemy.
        tabla: Nombre de la tabla (ya validado y en mayúsculas).

    Returns:
        list[str]: Lista ordenada de nombres de columna.
    """
    if tabla not in _cache_columnas:
        result = db.execute(
            text("SELECT column_name FROM user_tab_columns WHERE table_name = :t ORDER BY column_id"),
            {"t": tabla}
        )
        _cache_columnas[tabla] = [row[0] for row in result]
    return _cache_columnas[tabla]


def _validar_columnas(columnas_solicitadas: list[str], columnas_validas: list[str], tabla: str) -> list[str]:
    """
    Valida que las columnas solicitadas existan en la tabla.

    Args:
        columnas_solicitadas: Columnas que el cliente quiere consultar.
        columnas_validas: Columnas que realmente existen en la tabla.
        tabla: Nombre de la tabla (para el mensaje de error).

    Returns:
        list[str]: Lista de columnas validadas en mayúsculas.

    Raises:
        HTTPException: 400 si alguna columna no existe.
    """
    validas_set = set(columnas_validas)
    columnas_upper = [c.upper() for c in columnas_solicitadas]
    invalidas = [c for c in columnas_upper if c not in validas_set]
    if invalidas:
        raise HTTPException(
            status_code=400,
            detail=f"Columnas inválidas para la tabla '{tabla}': {', '.join(invalidas)}. "
                   f"Consulta GET /api/tablas/{tabla}/columnas para ver las columnas disponibles."
        )
    return columnas_upper


def obtener_tablas(db: Session) -> Dict[str, Any]:
    """
    Obtiene la lista de todas las tablas disponibles con metadatos básicos.
    Utiliza num_rows de user_tables para conteo rápido (aproximado).

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        Dict[str, Any]: Diccionario compatible con ListaTablasResponse.
    """
    placeholders = ", ".join([f":t{i}" for i in range(len(TABLAS_PERMITIDAS))])
    params = {f"t{i}": t for i, t in enumerate(sorted(TABLAS_PERMITIDAS))}

    result = db.execute(
        text(f"SELECT table_name, num_rows FROM user_tables WHERE table_name IN ({placeholders}) ORDER BY table_name"),
        params
    )

    # Obtener conteo de columnas por tabla
    col_result = db.execute(
        text(f"SELECT table_name, COUNT(*) FROM user_tab_columns WHERE table_name IN ({placeholders}) GROUP BY table_name"),
        params
    )
    col_counts = {row[0]: row[1] for row in col_result}

    tablas = []
    for row in result:
        nombre = row[0]
        prefijo = nombre.split("_")[0]
        tablas.append({
            "nombre": nombre,
            "dominio": prefijo,
            "descripcion_dominio": _DOMINIOS.get(prefijo, "Desconocido"),
            "total_registros": row[1] or 0,
            "total_columnas": col_counts.get(nombre, 0),
        })

    return {
        "total_tablas": len(tablas),
        "tablas": tablas,
    }


def obtener_columnas(db: Session, tabla: str) -> Dict[str, Any]:
    """
    Obtiene las columnas de una tabla con sus descripciones del diccionario de datos.
    Realiza un LEFT JOIN entre los metadatos de Oracle y la tabla DICCIONARIO_DE_DATOS.

    Args:
        db: Sesión activa de SQLAlchemy.
        tabla: Nombre de la tabla a consultar.

    Returns:
        Dict[str, Any]: Diccionario compatible con ColumnasResponse.

    Raises:
        HTTPException: 404 si la tabla no está en la whitelist.
    """
    tabla = _validar_tabla(tabla)

    result = db.execute(
        text("""
            SELECT utc.column_name, dd.DESCRIPCION, dd.TIPO_DE_DATO, dd.RANGOS_CLAVES
            FROM user_tab_columns utc
            LEFT JOIN DICCIONARIO_DE_DATOS dd
                ON UPPER(dd.NOMBRE_DE_LA_TABLA) = :tabla
                AND UPPER(dd.NOMBRE_DE_LA_COLUMNA) = utc.column_name
            WHERE utc.table_name = :tabla
            ORDER BY utc.column_id
        """),
        {"tabla": tabla}
    )

    columnas = []
    for row in result:
        columnas.append({
            "nombre": row[0],
            "descripcion": row[1],
            "tipo_de_dato": row[2],
            "rangos_claves": row[3],
        })

    return {
        "tabla": tabla,
        "total_columnas": len(columnas),
        "columnas": columnas,
    }


def obtener_registros(
    db: Session,
    tabla: str,
    pagina: int = 1,
    limite: int = 15,
    columnas_seleccionadas: Optional[List[str]] = None,
    filtros: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Extrae registros paginados de cualquier tabla con filtros dinámicos y selección de columnas.

    Args:
        db: Sesión activa de SQLAlchemy.
        tabla: Nombre de la tabla a consultar.
        pagina: Número de página (inicia en 1).
        limite: Cantidad máxima de registros por página.
        columnas_seleccionadas: Lista de columnas a devolver (None = todas).
        filtros: Diccionario de filtros columna→valor.

    Returns:
        Dict[str, Any]: Diccionario compatible con RespuestaPaginada.

    Raises:
        HTTPException: 404 si la tabla no existe, 400 si columnas/filtros son inválidos.
    """
    tabla = _validar_tabla(tabla)
    columnas_validas = _obtener_columnas_validas(db, tabla)
    filtros = filtros or {}

    # Validar columnas seleccionadas
    if columnas_seleccionadas:
        cols_validadas = _validar_columnas(columnas_seleccionadas, columnas_validas, tabla)
        cols_sql = ", ".join(cols_validadas)
        cols_respuesta = cols_validadas
    else:
        cols_sql = "*"
        cols_respuesta = columnas_validas

    # Validar y construir filtros
    if filtros:
        _validar_columnas(list(filtros.keys()), columnas_validas, tabla)

    where_parts: list[str] = []
    params: dict[str, Any] = {}
    for i, (col, val) in enumerate(filtros.items()):
        param_name = f"f_{i}"
        where_parts.append(f"{col.upper()} = :{param_name}")
        params[param_name] = val

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    # Conteo total con filtros
    count_result = db.execute(text(f"SELECT COUNT(*) FROM {tabla} {where_sql}"), params)
    total = count_result.scalar()

    # Consulta paginada
    offset = (pagina - 1) * limite
    params["offset_val"] = offset
    params["limit_val"] = limite

    data_result = db.execute(
        text(f"SELECT {cols_sql} FROM {tabla} {where_sql} OFFSET :offset_val ROWS FETCH NEXT :limit_val ROWS ONLY"),
        params
    )

    registros = [dict(row._mapping) for row in data_result]

    return {
        "tabla": tabla,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "hay_mas": (offset + limite) < total,
        "columnas": cols_respuesta,
        "registros": registros,
    }


def generar_csv_stream(
    engine: Engine,
    tabla: str,
    columnas_seleccionadas: Optional[List[str]] = None,
    filtros: Optional[Dict[str, str]] = None,
):
    """
    Genera un flujo de bytes CSV para descarga usando chunks de Pandas.
    No carga toda la tabla en memoria, sino que la procesa por bloques de 5000 filas.

    Args:
        engine: Engine de SQLAlchemy para conexión directa.
        tabla: Nombre de la tabla (ya validado).
        columnas_seleccionadas: Columnas a exportar (None = todas).
        filtros: Filtros columna→valor a aplicar.

    Yields:
        str: Fragmentos del CSV como strings.
    """
    filtros = filtros or {}

    # Construir SQL
    cols_sql = ", ".join(columnas_seleccionadas) if columnas_seleccionadas else "*"

    where_parts: list[str] = []
    params: dict[str, Any] = {}
    for i, (col, val) in enumerate(filtros.items()):
        param_name = f"f_{i}"
        where_parts.append(f"{col.upper()} = :{param_name}")
        params[param_name] = val

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    query = text(f"SELECT {cols_sql} FROM {tabla} {where_sql}")

    es_primera = True
    with engine.connect() as conn:
        for chunk in pd.read_sql(query, con=conn, params=params, chunksize=5000):
            buffer = io.StringIO()
            chunk.to_csv(buffer, index=False, header=es_primera)
            es_primera = False
            yield buffer.getvalue()


def buscar_diccionario(
    db: Session,
    termino: Optional[str] = None,
    tabla_filtro: Optional[str] = None,
    pagina: int = 1,
    limite: int = 20,
) -> Dict[str, Any]:
    """
    Busca entradas en el diccionario de datos por palabra clave o por tabla.

    Args:
        db: Sesión activa de SQLAlchemy.
        termino: Palabra clave para buscar en nombre de columna o descripción.
        tabla_filtro: Filtrar resultados por nombre de tabla específica.
        pagina: Número de página.
        limite: Resultados por página.

    Returns:
        Dict[str, Any]: Diccionario compatible con DiccionarioResponse.
    """
    where_parts: list[str] = []
    params: dict[str, Any] = {}

    if termino:
        where_parts.append(
            "(UPPER(NOMBRE_DE_LA_COLUMNA) LIKE UPPER(:termino) OR UPPER(DESCRIPCION) LIKE UPPER(:termino))"
        )
        params["termino"] = f"%{termino}%"

    if tabla_filtro:
        where_parts.append("UPPER(NOMBRE_DE_LA_TABLA) = UPPER(:tabla_filtro)")
        params["tabla_filtro"] = tabla_filtro

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    # Conteo total
    count_result = db.execute(
        text(f"SELECT COUNT(*) FROM DICCIONARIO_DE_DATOS {where_sql}"),
        params
    )
    total = count_result.scalar()

    # Consulta paginada
    offset = (pagina - 1) * limite
    params["offset_val"] = offset
    params["limit_val"] = limite

    result = db.execute(
        text(f"""
            SELECT NOMBRE_DE_LA_DB, NOMBRE_DEL_CONJUNTO, NOMBRE_DE_LA_TABLA,
                   NOMBRE_DE_LA_COLUMNA, DESCRIPCION, TIPO_DE_DATO, RANGOS_CLAVES
            FROM DICCIONARIO_DE_DATOS {where_sql}
            ORDER BY NOMBRE_DE_LA_TABLA, NOMBRE_DE_LA_COLUMNA
            OFFSET :offset_val ROWS FETCH NEXT :limit_val ROWS ONLY
        """),
        params
    )

    resultados = []
    for row in result:
        resultados.append({
            "nombre_de_la_db": row[0],
            "nombre_del_conjunto": row[1],
            "nombre_de_la_tabla": row[2],
            "nombre_de_la_columna": row[3],
            "descripcion": row[4],
            "tipo_de_dato": row[5],
            "rangos_claves": row[6],
        })

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "hay_mas": (offset + limite) < total,
        "resultados": resultados,
    }
