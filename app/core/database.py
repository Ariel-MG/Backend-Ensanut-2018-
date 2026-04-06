import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Configuración de credenciales (vienen de variables de entorno)
DB_USER = os.getenv("DB_USER", "usuario_oracle")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password_oracle")
DB_DSN = os.getenv("DB_DSN", "localhost:1521/XEPDB1")

# Parsear el DSN (host:puerto/servicio) para construir la URL con service_name
_host_port, _service = DB_DSN.rsplit("/", 1)

# URL de conexión SQLAlchemy para oracledb (Modo Thin)
# Se usa ?service_name= para que Oracle no lo interprete como SID
SQLALCHEMY_DATABASE_URL = f"oracle+oracledb://{DB_USER}:{DB_PASSWORD}@{_host_port}/?service_name={_service}"

"""
Motor de la base de datos.
Se configura para manejar el pool de conexiones de manera eficiente.
"""
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    arraysize=1000, # Optimización para extraer grandes volúmenes de datos (ENSANUT)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependencia de FastAPI para obtener la sesión de la base de datos.
    Garantiza que la conexión se cierre correctamente después de cada petición.

    Yields:
        Session: Sesión activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
