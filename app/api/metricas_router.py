from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ensanut import (
    DemografiaResponse,
    DistribucionEntidadResponse,
    IndicadoresSaludResponse,
)
from app.services.metricas_service import (
    obtener_distribucion_entidad,
    obtener_demografia,
    obtener_indicadores_salud,
)

router = APIRouter(prefix="/api/metricas", tags=["Métricas y Agrupaciones"])


@router.get(
    "/distribucion-entidad",
    response_model=DistribucionEntidadResponse,
    summary="Distribución de registros por entidad federativa",
    description="Agrupa los registros de la tabla indicada por entidad federativa (ENT). "
                "Retorna el conteo y porcentaje por estado, ordenado de mayor a menor. "
                "Ideal para treemaps, mapas de calor y barras horizontales.",
    response_description="Distribución geográfica con código INEGI, nombre del estado y porcentaje.",
    tags=["Métricas y Agrupaciones"],
)
def distribucion_por_entidad(
    tabla: str = Query(..., description="Nombre de la tabla a consultar (ej. CS_ADULTOS, CN_ANTROPOMETRIA)."),
    db: Session = Depends(get_db),
) -> DistribucionEntidadResponse:
    """
    Controlador para obtener la distribución geográfica de una tabla.

    Args:
        tabla: Tabla de la ENSANUT a agrupar por entidad.
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        DistribucionEntidadResponse: Distribución por estado con porcentajes.
    """
    return obtener_distribucion_entidad(db=db, tabla=tabla)


@router.get(
    "/demografia",
    response_model=DemografiaResponse,
    summary="Distribución demográfica por sexo y edad",
    description="Calcula la distribución por sexo (para Pie Chart) y por rangos de edad "
                "cruzados con sexo (para pirámide poblacional / histograma). "
                "Rangos: 0-4, 5-11, 12-19, 20-59, 60+.",
    response_description="Distribución por sexo y tabla cruzada edad×sexo.",
    tags=["Métricas y Agrupaciones"],
)
def demografia(
    tabla: str = Query(..., description="Nombre de la tabla a consultar (ej. CS_ADULTOS, CN_ANTROPOMETRIA)."),
    db: Session = Depends(get_db),
) -> DemografiaResponse:
    """
    Controlador para obtener la distribución demográfica.

    Args:
        tabla: Tabla de la ENSANUT a analizar demográficamente.
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        DemografiaResponse: Distribución por sexo y rangos de edad.
    """
    return obtener_demografia(db=db, tabla=tabla)


@router.get(
    "/salud",
    response_model=IndicadoresSaludResponse,
    summary="Indicadores de prevalencia de condiciones de salud",
    description="Calcula la prevalencia de diabetes, hipertensión y colesterol alto "
                "entre los adultos encuestados en CS_ADULTOS. Retorna total de encuestados, "
                "total de casos positivos y prevalencia como porcentaje. "
                "Ideal para tarjetas KPI y sparklines.",
    response_description="Indicadores de salud con prevalencias porcentuales.",
    tags=["Métricas y Agrupaciones"],
)
def indicadores_salud(
    db: Session = Depends(get_db),
) -> IndicadoresSaludResponse:
    """
    Controlador para obtener indicadores de salud clave.

    Args:
        db: Sesión inyectada de SQLAlchemy.

    Returns:
        IndicadoresSaludResponse: Prevalencias de diabetes, hipertensión y colesterol.
    """
    return obtener_indicadores_salud(db=db)
