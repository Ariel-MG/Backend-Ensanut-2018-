from sqlalchemy import Column, String
from app.core.database import Base

class DiccionarioDeDatos(Base):
    """
    Modelo ORM para la tabla DICCIONARIO_DE_DATOS de la ENSANUT 2018.
    Contiene las descripciones humanas de cada columna de cada tabla,
    permitiendo que la API autodocumente los datos para los analistas.

    Attributes:
        nombre_de_la_db: Base de datos de origen.
        nombre_del_conjunto: Conjunto de datos al que pertenece.
        nombre_de_la_tabla: Nombre de la tabla física en Oracle.
        nombre_de_la_columna: Nombre de la columna dentro de la tabla.
        descripcion: Descripción legible de la variable.
        tipo_de_dato: Tipo de dato documentado.
        rangos_claves: Valores válidos o rangos permitidos.
    """
    __tablename__ = "DICCIONARIO_DE_DATOS"

    nombre_de_la_db = Column("NOMBRE_DE_LA_DB", String(100))
    nombre_del_conjunto = Column("NOMBRE_DEL_CONJUNTO", String(100))
    nombre_de_la_tabla = Column("NOMBRE_DE_LA_TABLA", String(200), primary_key=True)
    nombre_de_la_columna = Column("NOMBRE_DE_LA_COLUMNA", String(200), primary_key=True)
    descripcion = Column("DESCRIPCION", String(1000))
    tipo_de_dato = Column("TIPO_DE_DATO", String(100))
    rangos_claves = Column("RANGOS_CLAVES", String(500))


# Whitelist de tablas permitidas para prevención de SQL Injection.
# Solo estas tablas pueden ser consultadas dinámicamente por la API.
TABLAS_PERMITIDAS: set[str] = {
    "CN_ALIMENTOS_ADU",
    "CN_ALIMENTOS_COM",
    "CN_ALIMENTOS_ESC",
    "CN_ALIMENTOS_PREES",
    "CN_ANTROPOMETRIA",
    "CN_CAT_ALIMENTOS",
    "CN_DES_INF",
    "CN_DES_INF_P7",
    "CN_FCA_ADOLESCENTES",
    "CN_FCA_ADU",
    "CN_FCA_ESC",
    "CN_FCA_PREES",
    "CN_HOGARES",
    "CN_LAC_MAT",
    "CN_MUESAN_DETBIO_ADU",
    "CN_MUESAN_DETBIO_ESC",
    "CN_MUESAN_DETBIO_PREES",
    "CN_MUESAN_HEMOGLOBINA",
    "CN_MUESAN_HEPA_ADU",
    "CN_MUESAN_PLOMO",
    "CN_PLOMO",
    "CN_RESIDENTES",
    "CN_VIVIENDAS",
    "CS_ACT_FIS_ADO",
    "CS_ACT_FIS_NINO",
    "CS_ADOLESCENTES",
    "CS_ADULTOS",
    "CS_AYUDA_ALIMENTARIA",
    "CS_ETIQUETADO_FRONTAL",
    "CS_HOGARES",
    "CS_NINO",
    "CS_RESIDENTES",
    "CS_SEGURIDAD_ALIMENTARIA",
    "CS_SERV_SALUD",
    "CS_VIVIENDAS",
}
