from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.ensanut import TABLAS_PERMITIDAS
from app.services.data_service import _validar_tabla, _obtener_columnas_validas

# Catálogo de las 32 entidades federativas de México
_ENTIDADES: dict[str, str] = {
    "01": "Aguascalientes", "02": "Baja California", "03": "Baja California Sur",
    "04": "Campeche", "05": "Coahuila", "06": "Colima",
    "07": "Chiapas", "08": "Chihuahua", "09": "Ciudad de México",
    "10": "Durango", "11": "Guanajuato", "12": "Guerrero",
    "13": "Hidalgo", "14": "Jalisco", "15": "Estado de México",
    "16": "Michoacán", "17": "Morelos", "18": "Nayarit",
    "19": "Nuevo León", "20": "Oaxaca", "21": "Puebla",
    "22": "Querétaro", "23": "Quintana Roo", "24": "San Luis Potosí",
    "25": "Sinaloa", "26": "Sonora", "27": "Tabasco",
    "28": "Tamaulipas", "29": "Tlaxcala", "30": "Veracruz",
    "31": "Yucatán", "32": "Zacatecas",
}

# Rangos de edad estándar para análisis poblacional ENSANUT
_RANGOS_EDAD = [
    ("0-4", 0, 4),
    ("5-11", 5, 11),
    ("12-19", 12, 19),
    ("20-59", 20, 59),
    ("60+", 60, 999),
]

# Condiciones de salud consultables desde CS_ADULTOS
# Basado en la estructura estándar del cuestionario ENSANUT 2018:
#   P3_1 = "¿Algún médico le ha dicho que tiene diabetes?"
#   P4_1 = "¿Algún médico le ha dicho que tiene presión alta?"
#   P5_1 = "¿Algún médico le ha dicho que tiene colesterol alto?"
# Valor "1" = Sí en la codificación ENSANUT
_CONDICIONES_SALUD: dict[str, dict[str, str]] = {
    "diabetes": {
        "tabla": "CS_ADULTOS",
        "columna": "P3_1",
        "valor_positivo": "1",
        "etiqueta": "Diabetes diagnosticada",
    },
    "hipertension": {
        "tabla": "CS_ADULTOS",
        "columna": "P4_1",
        "valor_positivo": "1",
        "etiqueta": "Hipertensión diagnosticada",
    },
    "colesterol": {
        "tabla": "CS_ADULTOS",
        "columna": "P5_1",
        "valor_positivo": "1",
        "etiqueta": "Colesterol alto diagnosticado",
    },
}


def obtener_distribucion_entidad(db: Session, tabla: str) -> Dict[str, Any]:
    """
    Calcula la distribución de registros por entidad federativa.
    Retorna conteo por estado ordenado de mayor a menor para visualización en treemap/barras.

    Args:
        db: Sesión activa de SQLAlchemy.
        tabla: Nombre de la tabla a consultar.

    Returns:
        Dict[str, Any]: Distribución con código, nombre del estado y conteo.

    Raises:
        HTTPException: 404 si la tabla no existe, 400 si no tiene columna ENT.
    """
    tabla = _validar_tabla(tabla)
    columnas = _obtener_columnas_validas(db, tabla)

    if "ENT" not in columnas:
        raise HTTPException(
            status_code=400,
            detail=f"La tabla '{tabla}' no contiene la columna ENT (entidad federativa)."
        )

    result = db.execute(text(f"""
        SELECT ENT, COUNT(*) as total
        FROM {tabla}
        WHERE ENT IS NOT NULL
        GROUP BY ENT
        ORDER BY COUNT(*) DESC
    """))

    distribucion = []
    total_general = 0
    for row in result:
        codigo = row[0].strip() if row[0] else None
        conteo = row[1]
        total_general += conteo
        distribucion.append({
            "codigo_entidad": codigo,
            "nombre_entidad": _ENTIDADES.get(codigo, f"Desconocido ({codigo})") if codigo else "Sin dato",
            "total": conteo,
        })

    # Calcular porcentaje
    for item in distribucion:
        item["porcentaje"] = round((item["total"] / total_general * 100), 2) if total_general > 0 else 0

    return {
        "tabla": tabla,
        "total_registros": total_general,
        "entidades": distribucion,
    }


def obtener_demografia(db: Session, tabla: str) -> Dict[str, Any]:
    """
    Calcula la distribución demográfica por sexo y rangos de edad.
    Ideal para pirámides poblacionales e histogramas agrupados.

    Args:
        db: Sesión activa de SQLAlchemy.
        tabla: Nombre de la tabla a consultar.

    Returns:
        Dict[str, Any]: Distribución por sexo y rangos de edad.

    Raises:
        HTTPException: 404/400 si la tabla no existe o no tiene EDAD/SEXO.
    """
    tabla = _validar_tabla(tabla)
    columnas = _obtener_columnas_validas(db, tabla)

    for col_requerida in ["EDAD", "SEXO"]:
        if col_requerida not in columnas:
            raise HTTPException(
                status_code=400,
                detail=f"La tabla '{tabla}' no contiene la columna {col_requerida}."
            )

    # Distribución por sexo
    sexo_result = db.execute(text(f"""
        SELECT SEXO, COUNT(*) as total
        FROM {tabla}
        WHERE SEXO IS NOT NULL
        GROUP BY SEXO
        ORDER BY SEXO
    """))

    distribucion_sexo = []
    for row in sexo_result:
        codigo = row[0].strip() if row[0] else None
        etiqueta = "Hombre" if codigo == "1" else "Mujer" if codigo == "2" else f"Otro ({codigo})"
        distribucion_sexo.append({
            "codigo": codigo,
            "etiqueta": etiqueta,
            "total": row[1],
        })

    # Distribución por rangos de edad cruzados con sexo
    # Usar CASE WHEN para agrupar por rangos en Oracle
    case_edad = "CASE "
    for etiqueta, min_edad, max_edad in _RANGOS_EDAD:
        case_edad += f"WHEN TO_NUMBER(EDAD) BETWEEN {min_edad} AND {max_edad} THEN '{etiqueta}' "
    case_edad += "ELSE 'Sin dato' END"

    rangos_result = db.execute(text(f"""
        SELECT {case_edad} as rango_edad, SEXO, COUNT(*) as total
        FROM {tabla}
        WHERE EDAD IS NOT NULL AND SEXO IS NOT NULL
        GROUP BY {case_edad}, SEXO
        ORDER BY {case_edad}, SEXO
    """))

    rangos_edad = []
    for row in rangos_result:
        codigo_sexo = row[1].strip() if row[1] else None
        rangos_edad.append({
            "rango": row[0],
            "sexo_codigo": codigo_sexo,
            "sexo_etiqueta": "Hombre" if codigo_sexo == "1" else "Mujer" if codigo_sexo == "2" else f"Otro ({codigo_sexo})",
            "total": row[2],
        })

    return {
        "tabla": tabla,
        "distribucion_sexo": distribucion_sexo,
        "rangos_edad": rangos_edad,
    }


def obtener_indicadores_salud(db: Session) -> Dict[str, Any]:
    """
    Calcula indicadores de prevalencia de condiciones de salud clave en adultos.
    Ejecuta conteos rápidos de diabetes, hipertensión y colesterol sobre CS_ADULTOS.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        Dict[str, Any]: Indicadores con total encuestado, total positivo y prevalencia.
    """
    indicadores: List[Dict[str, Any]] = []

    for clave, config in _CONDICIONES_SALUD.items():
        tabla = config["tabla"]
        columna = config["columna"]
        valor_positivo = config["valor_positivo"]

        # Total de encuestados que respondieron la pregunta (no nulos)
        total_result = db.execute(text(
            f"SELECT COUNT(*) FROM {tabla} WHERE {columna} IS NOT NULL"
        ))
        total_encuestados = total_result.scalar()

        # Total de casos positivos
        positivos_result = db.execute(text(
            f"SELECT COUNT(*) FROM {tabla} WHERE {columna} = :val"
        ), {"val": valor_positivo})
        total_positivos = positivos_result.scalar()

        prevalencia = round((total_positivos / total_encuestados * 100), 2) if total_encuestados > 0 else 0

        indicadores.append({
            "condicion": clave,
            "etiqueta": config["etiqueta"],
            "total_encuestados": total_encuestados,
            "total_positivos": total_positivos,
            "prevalencia_porcentaje": prevalencia,
        })

    return {
        "tabla_origen": "CS_ADULTOS",
        "indicadores": indicadores,
    }
