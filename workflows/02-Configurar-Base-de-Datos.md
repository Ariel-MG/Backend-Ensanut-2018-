# Workflow Claude Code: 02 - Configurar Base de Datos

**Objetivo de este paso:**
Crear la configuración de SQLAlchemy para conectarse a la base de datos Oracle utilizando el driver `oracledb` en modo Thin, y preparar la dependencia de inyección de sesiones para FastAPI.

## Instrucciones de Ejecución:
Por favor, interactúa con el sistema de archivos para realizar las siguientes tareas:

### 1. Crear el Archivo de Configuración de Base de Datos
Crea un archivo llamado `app/core/database.py` e implementa el siguiente código. Nota que estamos usando la sintaxis de conexión `oracle+oracledb://` que invoca automáticamente el modo Thin.

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuración de credenciales (Idealmente deberían venir de variables de entorno)
# Se colocan valores por defecto para el entorno de desarrollo local / túnel SSH
DB_USER = os.getenv("DB_USER", "usuario_oracle")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password_oracle")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "1521")
DB_SERVICE = os.getenv("DB_SERVICE", "XEPDB1")

# URL de conexión SQLAlchemy para oracledb (Modo Thin)
SQLALCHEMY_DATABASE_URL = f"oracle+oracledb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?service_name={DB_SERVICE}"

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
2. Confirmación
Responde confirmando que el archivo app/core/database.py ha sido creado con la configuración de SQLAlchemy y el driver oracledb. Indica que el sistema está listo para avanzar al paso "03-Definir-Modelos-y-Esquemas.md".
