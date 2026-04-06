# Backend ENSANUT 2018

Backend para la aplicación web de extracción y consulta de datos de la Encuesta Nacional de Salud y Nutrición (ENSANUT) 2018 del INEGI. Desarrollado para el Data Science Lab de la Universidad Anáhuac.

## Stack Tecnológico

- **Framework:** FastAPI
- **Servidor:** Uvicorn
- **Base de Datos:** Oracle (conexión vía `oracledb` en modo Thin)
- **ORM:** SQLAlchemy (para diccionario de datos) + SQL dinámico con `text()` (para tablas de encuesta)
- **Exportación:** Pandas (streaming por chunks)
- **Validación:** Pydantic v2

## Arquitectura del Proyecto

```
app/
├── main.py                  # Punto de entrada, CORS, health check
├── api/
│   └── ensanut_router.py    # 5 endpoints de la API
├── core/
│   └── database.py          # Conexión Oracle (Thin mode), engine, sesiones
├── models/
│   └── ensanut.py           # Modelo ORM DiccionarioDeDatos + whitelist de tablas
├── schemas/
│   └── ensanut.py           # Esquemas Pydantic de request/response
└── services/
    └── data_service.py      # Lógica de negocio: SQL dinámico, paginación, export CSV
docs/
└── DOCUMENTACION_FRONTEND.md  # Guía de integración para el equipo React
```

## Base de Datos

La ENSANUT 2018 está almacenada en **35 tablas de datos** organizadas en dos dominios:

| Prefijo | Dominio | Ejemplos |
|---|---|---|
| `CN_` | Cuestionario de Nutrición | `CN_ANTROPOMETRIA`, `CN_ALIMENTOS_ADU`, `CN_HOGARES` |
| `CS_` | Cuestionario de Salud | `CS_ADULTOS`, `CS_ADOLESCENTES`, `CS_NINO` |

Adicionalmente existe una tabla `DICCIONARIO_DE_DATOS` que contiene las descripciones oficiales de cada columna de cada tabla.

Todas las columnas de las tablas de datos son `VARCHAR2(300)`. La API expone los valores tal cual (como strings).

## Requisitos Previos

- Python 3.11+
- Acceso a la base de datos Oracle del proyecto
- Credenciales de conexión (`DB_USER`, `DB_PASSWORD`, `DB_DSN`)

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Backend-Ensanut-2018-
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_DSN=host:puerto/servicio
```

> El archivo `.env` está en `.gitignore` y nunca debe subirse al repositorio.

## Iniciar el Servidor

```bash
uvicorn app.main:app --reload
```

El servidor quedará disponible en `http://localhost:8000`.

## Documentación de la API

Una vez iniciado el servidor, accede al Swagger UI interactivo:

```
http://localhost:8000/docs
```

Para documentación detallada de integración con React, ver [`docs/DOCUMENTACION_FRONTEND.md`](docs/DOCUMENTACION_FRONTEND.md).

## Endpoints Disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Health check — verifica que la API esté activa |
| `GET` | `/api/tablas` | Lista las 35 tablas con dominio y conteo de registros |
| `GET` | `/api/tablas/{tabla}/columnas` | Columnas de una tabla con descripciones del diccionario |
| `GET` | `/api/tablas/{tabla}/registros` | Registros paginados con filtros dinámicos |
| `GET` | `/api/tablas/{tabla}/exportar` | Exportar datos filtrados a CSV |
| `GET` | `/api/diccionario` | Buscar variables en el diccionario de datos |

### Parámetros de paginación (`/api/tablas/{tabla}/registros`)

| Parámetro | Tipo | Defecto | Descripción |
|---|---|---|---|
| `pagina` | int | 1 | Número de página (inicia en 1) |
| `limite` | int | 15 | Registros por página (máx. 100) |
| `columnas` | string | null | Columnas a devolver, separadas por coma |
| *cualquier otro* | string | — | Filtro de columna (ej. `SEXO=1&ENT=09`) |

### Ejemplos rápidos

```bash
# Listar tablas
curl http://localhost:8000/api/tablas

# Ver columnas de CS_ADULTOS
curl http://localhost:8000/api/tablas/CS_ADULTOS/columnas

# Registros paginados con filtros
curl "http://localhost:8000/api/tablas/CS_ADULTOS/registros?pagina=1&limite=20&SEXO=1&ENT=09"

# Exportar CSV filtrado
curl -O "http://localhost:8000/api/tablas/CS_ADULTOS/exportar?columnas=UPM,EDAD,SEXO&SEXO=2"

# Buscar en el diccionario
curl "http://localhost:8000/api/diccionario?termino=glucosa"
```

## Seguridad

La API implementa 3 capas de protección contra SQL Injection:

1. **Nombres de tabla** — validados contra una whitelist hardcodeada (`TABLAS_PERMITIDAS`)
2. **Nombres de columna** — validados contra los metadatos reales de Oracle (`user_tab_columns`)
3. **Valores de filtro** — siempre como bind parameters de SQLAlchemy (`text()`)

## CORS

Habilitado para los puertos de desarrollo de Vite/React:

- `http://localhost:5173`
- `http://localhost:3000`
- `http://127.0.0.1:5173`
