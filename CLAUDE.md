# Reglas Globales y Contexto para Claude Code - Backend ENSANUT 2018

## Contexto del Proyecto
Eres el desarrollador Backend Senior de un sistema de "Extracción y Gobierno de Datos" para el Data Science Lab de la Universidad Anáhuac. El objetivo de este backend es exponer los datos unificados de la ENSANUT 2018 para que el frontend (React) los consuma y los analistas puedan exportarlos.

## Stack Tecnológico
* **Framework:** FastAPI (Python)
* **Servidor ASGI:** Uvicorn
* **ORM y Base de Datos:** SQLAlchemy + `oracledb` (Conexión estricta en modo *Thin* hacia Oracle).
* **Validación de Datos:** Pydantic
* **Manejo de Datos/Exportación:** Pandas

## Reglas de Arquitectura y Estructura
* Mantén el código dentro de un directorio principal llamado `app/`.
* Usa una arquitectura estructurada por capas:
    * `app/api/`: Para los routers y endpoints.
    * `app/core/`: Para la configuración (CORS, variables de entorno, conexión a DB).
    * `app/models/`: Para los modelos de SQLAlchemy (tablas físicas).
    * `app/schemas/`: Para los modelos de Pydantic (validación de entrada/salida).
    * `app/services/`: Para la lógica de negocio compleja (como la exportación a CSV).

## Reglas de Documentación Estructurada (CRÍTICO)
1. **Docstrings Nativos:** Utiliza el estándar de docstrings de **Google** para todas las funciones, clases y métodos. Debes detallar claramente el propósito, los argumentos (`Args:`), lo que devuelve (`Returns:`) y las posibles excepciones (`Raises:`).
2. **Metadatos en Endpoints:** Todo decorador de ruta de FastAPI (ej. `@app.get()`) debe incluir los parámetros `summary`, `description`, `response_description` y estar agrupado lógicamente usando `tags`.
3. **Modelos Autodocumentados:** En los esquemas de Pydantic, utiliza obligatoriamente la clase `Field(..., description="...")` para explicar el significado de cada variable. Esto asegurará que el Swagger UI autogenerado sirva como un diccionario de datos técnico para los analistas.

## Reglas Estrictas de Desarrollo
1.  **Conexión a Oracle:** NUNCA intentes instalar ni requerir el *Oracle Instant Client* nativo. Utiliza siempre el paquete `oracledb` de Python en su modo *Thin* (standalone).
2.  **Rendimiento y Paginación:** La ENSANUT contiene millones de registros. Todos los endpoints que devuelvan listas de datos DEBEN estar paginados usando `limit` y `offset` (o `page`). Nunca devuelvas una tabla completa en una sola petición JSON.
3.  **Exportación de Archivos:** Para el botón de "Exportar a CSV" del frontend, el backend debe generar el archivo al vuelo. Utiliza `pandas.DataFrame` para estructurar los datos extraídos por SQLAlchemy y devuelve un `StreamingResponse` o `FileResponse` con el `media_type="text/csv"`.
4.  **Tipado Estricto:** Usa *Type Hints* en todas las variables, funciones y dependencias de FastAPI. Define todos los esquemas de respuesta explícitamente con Pydantic.
5.  **CORS:** Debes habilitar CORS desde el inicio (en el `main.py`) para permitir conexiones desde los puertos locales típicos de Vite/React (como `http://localhost:5173`).
6.  **Idioma:** Todas las descripciones del Swagger, docstrings,