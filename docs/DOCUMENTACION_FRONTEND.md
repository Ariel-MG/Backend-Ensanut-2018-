# Documentación de la API - ENSANUT 2018

## Para el equipo de Frontend (React)

Documentación completa de los endpoints disponibles en el backend de extracción de datos de la ENSANUT 2018.

---

## Información General

| Dato | Valor |
|---|---|
| **URL Base (desarrollo)** | `http://localhost:8000` |
| **Documentación interactiva (Swagger)** | `http://localhost:8000/docs` |
| **Formato de respuesta** | JSON |
| **Autenticación** | No requerida (uso interno) |
| **CORS habilitado para** | `localhost:5173`, `localhost:3000`, `127.0.0.1:5173` |

### Notas importantes
- **Todos los valores de los registros son strings** (`VARCHAR2` en Oracle). Si necesitas operar numéricamente sobre `EDAD`, `PESO`, etc., convierte en el frontend con `parseInt()` o `parseFloat()`.
- La paginación es obligatoria. El máximo de registros por página es **100**.
- Los nombres de tablas y columnas son **case-insensitive** (la API convierte a mayúsculas internamente).

---

## Resumen de Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/api/tablas` | Listar todas las tablas disponibles |
| `GET` | `/api/tablas/{tabla}/columnas` | Obtener columnas de una tabla con descripciones |
| `GET` | `/api/tablas/{tabla}/registros` | Obtener registros paginados con filtros |
| `GET` | `/api/tablas/{tabla}/exportar` | Descargar datos en formato CSV |
| `GET` | `/api/diccionario` | Buscar en el diccionario de datos |

---

## Detalle de Endpoints

### 1. `GET /api/tablas`

Devuelve la lista completa de tablas disponibles con metadatos básicos.

**Parámetros:** Ninguno

**Respuesta de ejemplo:**

```json
{
  "total_tablas": 35,
  "tablas": [
    {
      "nombre": "CS_ADULTOS",
      "dominio": "CS",
      "descripcion_dominio": "Cuestionario de Salud",
      "total_registros": 42000,
      "total_columnas": 85
    },
    {
      "nombre": "CN_ANTROPOMETRIA",
      "dominio": "CN",
      "descripcion_dominio": "Cuestionario de Nutrición",
      "total_registros": 50000,
      "total_columnas": 35
    }
  ]
}
```

**Uso típico:** Llenar un selector/dropdown para que el usuario elija qué tabla quiere explorar.

---

### 2. `GET /api/tablas/{tabla}/columnas`

Devuelve los nombres y descripciones de las columnas de una tabla. Las descripciones provienen del diccionario de datos oficial.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `tabla` | string | Nombre de la tabla (ej. `CS_ADULTOS`) |

**Respuesta de ejemplo:**

```json
{
  "tabla": "CS_ADULTOS",
  "total_columnas": 85,
  "columnas": [
    {
      "nombre": "UPM",
      "descripcion": "Unidad primaria de muestreo",
      "tipo_de_dato": "VARCHAR2",
      "rangos_claves": null
    },
    {
      "nombre": "SEXO",
      "descripcion": "Sexo del entrevistado",
      "tipo_de_dato": "VARCHAR2",
      "rangos_claves": "1=Hombre, 2=Mujer"
    },
    {
      "nombre": "EDAD",
      "descripcion": "Edad en años cumplidos",
      "tipo_de_dato": "VARCHAR2",
      "rangos_claves": "20-99"
    }
  ]
}
```

**Uso típico:** Mostrar un panel de selección de columnas (checkboxes) y construir los filtros dinámicamente. El campo `rangos_claves` ayuda a saber qué valores son válidos para cada filtro.

---

### 3. `GET /api/tablas/{tabla}/registros`

Extrae registros paginados con soporte para selección de columnas y filtros dinámicos.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `tabla` | string | Nombre de la tabla |

**Parámetros de query (fijos):**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `pagina` | int | 1 | Número de página (inicia en 1) |
| `limite` | int | 15 | Registros por página (máx. 100) |
| `columnas` | string | null | Columnas separadas por coma |

**Filtros dinámicos:**
Cualquier otro query param se interpreta como un filtro de columna. El nombre del parámetro debe coincidir exactamente con el nombre de la columna.

**Ejemplos de URL:**

```
# Página 1, 15 registros, todas las columnas
GET /api/tablas/CS_ADULTOS/registros

# Página 2, 20 registros
GET /api/tablas/CS_ADULTOS/registros?pagina=2&limite=20

# Solo algunas columnas
GET /api/tablas/CS_ADULTOS/registros?columnas=UPM,EDAD,SEXO,ENT

# Con filtros
GET /api/tablas/CS_ADULTOS/registros?SEXO=1&ENT=09

# Combinando todo
GET /api/tablas/CS_ADULTOS/registros?pagina=1&limite=25&columnas=EDAD,SEXO,ENT&SEXO=2&ENT=15
```

**Respuesta de ejemplo:**

```json
{
  "tabla": "CS_ADULTOS",
  "total": 12500,
  "pagina": 1,
  "limite": 15,
  "hay_mas": true,
  "columnas": ["EDAD", "SEXO", "ENT"],
  "registros": [
    {"EDAD": "35", "SEXO": "1", "ENT": "09"},
    {"EDAD": "42", "SEXO": "2", "ENT": "09"},
    {"EDAD": "28", "SEXO": "1", "ENT": "09"}
  ]
}
```

---

### 4. `GET /api/tablas/{tabla}/exportar`

Descarga un archivo CSV con los datos de la tabla. Acepta los mismos filtros y selección de columnas que el endpoint de registros (excepto paginación).

**Parámetros:** Mismos que `/registros` excepto `pagina` y `limite`.

**Ejemplos de URL:**

```
# Exportar tabla completa
GET /api/tablas/CS_ADULTOS/exportar

# Exportar solo algunas columnas
GET /api/tablas/CS_ADULTOS/exportar?columnas=UPM,EDAD,SEXO,ENT

# Exportar con filtros
GET /api/tablas/CS_ADULTOS/exportar?SEXO=1&ENT=09
```

**Respuesta:** Archivo CSV como descarga directa (no JSON).

---

### 5. `GET /api/diccionario`

Busca variables por palabra clave en el diccionario de datos oficial.

**Parámetros de query:**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `termino` | string | null | Palabra clave (ej. "glucosa", "peso", "diabetes") |
| `tabla` | string | null | Filtrar por tabla específica |
| `pagina` | int | 1 | Número de página |
| `limite` | int | 20 | Resultados por página (máx. 100) |

**Ejemplos de URL:**

```
# Buscar por término
GET /api/diccionario?termino=glucosa

# Buscar dentro de una tabla específica
GET /api/diccionario?termino=peso&tabla=CN_ANTROPOMETRIA

# Ver todo el diccionario de una tabla
GET /api/diccionario?tabla=CS_ADULTOS
```

**Respuesta de ejemplo:**

```json
{
  "total": 3,
  "pagina": 1,
  "limite": 20,
  "hay_mas": false,
  "resultados": [
    {
      "nombre_de_la_db": "ENSANUT2018",
      "nombre_del_conjunto": "Nutrición",
      "nombre_de_la_tabla": "CN_MUESAN_DETBIO_ADU",
      "nombre_de_la_columna": "GLUCOSA",
      "descripcion": "Nivel de glucosa capilar en sangre medida en mg/dL",
      "tipo_de_dato": "VARCHAR2",
      "rangos_claves": "0-500"
    }
  ]
}
```

---

## Códigos de Error

| Código | Significado | Ejemplo |
|---|---|---|
| `400` | Columna o filtro inválido | Se usó un nombre de columna que no existe en la tabla |
| `404` | Tabla no encontrada | Se pidió una tabla que no está en la ENSANUT |
| `500` | Error interno del servidor | Error de conexión a Oracle u otro problema del backend |

**Formato de error:**

```json
{
  "detail": "Columnas inválidas para la tabla 'CS_ADULTOS': COLUMNA_FALSA. Consulta GET /api/tablas/CS_ADULTOS/columnas para ver las columnas disponibles."
}
```

---

## Ejemplos de Integración con React

### Configuración base (axios)

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

export default api;
```

### Obtener lista de tablas

```javascript
const [tablas, setTablas] = useState([]);

useEffect(() => {
  api.get("/tablas").then((res) => {
    setTablas(res.data.tablas);
  });
}, []);
```

### Obtener columnas de una tabla seleccionada

```javascript
const [columnas, setColumnas] = useState([]);

const cargarColumnas = async (nombreTabla) => {
  const res = await api.get(`/tablas/${nombreTabla}/columnas`);
  setColumnas(res.data.columnas);
};
```

### Obtener registros con filtros y paginación

```javascript
const cargarRegistros = async (tabla, pagina, filtros, columnasSeleccionadas) => {
  const params = {
    pagina,
    limite: 15,
    ...filtros, // ej. { SEXO: "1", ENT: "09" }
  };

  // Agregar columnas seleccionadas si hay
  if (columnasSeleccionadas.length > 0) {
    params.columnas = columnasSeleccionadas.join(",");
  }

  const res = await api.get(`/tablas/${tabla}/registros`, { params });
  return res.data; // { tabla, total, pagina, limite, hay_mas, columnas, registros }
};
```

### Descargar CSV

```javascript
const descargarCSV = (tabla, filtros, columnasSeleccionadas) => {
  const params = new URLSearchParams(filtros);

  if (columnasSeleccionadas.length > 0) {
    params.set("columnas", columnasSeleccionadas.join(","));
  }

  // Abrir en nueva pestaña para forzar descarga
  const url = `http://localhost:8000/api/tablas/${tabla}/exportar?${params.toString()}`;
  window.open(url, "_blank");
};
```

### Buscar en el diccionario de datos

```javascript
const buscarVariable = async (termino) => {
  const res = await api.get("/diccionario", {
    params: { termino },
  });
  return res.data.resultados;
};
```

---

## Flujo de Uso Recomendado para el Frontend

1. **Al cargar la aplicación:** Llamar a `GET /api/tablas` para mostrar el selector de tablas.
2. **Al seleccionar una tabla:** Llamar a `GET /api/tablas/{tabla}/columnas` para mostrar las columnas disponibles con sus descripciones y rangos válidos.
3. **Al configurar la vista:** El usuario selecciona columnas (checkboxes) y define filtros (inputs basados en `rangos_claves`).
4. **Al consultar datos:** Llamar a `GET /api/tablas/{tabla}/registros` con los filtros y columnas seleccionadas. Implementar paginación con los campos `pagina`, `total` y `hay_mas`.
5. **Al exportar:** Llamar a `GET /api/tablas/{tabla}/exportar` con los mismos filtros activos para descargar el CSV.
6. **Para descubrir variables:** Usar `GET /api/diccionario` como buscador cuando el analista no sabe en qué tabla está la variable que necesita.
