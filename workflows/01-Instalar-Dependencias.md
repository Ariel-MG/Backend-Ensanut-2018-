# Workflow Claude Code: 01 - Instalar Dependencias

**Objetivo de este paso:**
Definir e instalar las dependencias fundamentales del proyecto asegurando la compatibilidad con nuestra arquitectura y las reglas de `CLAUDE.md`.

## Instrucciones de Ejecución:
Por favor, interactúa con el sistema de archivos y la terminal para realizar las siguientes tareas:

### 1. Poblar requirements.txt
Abre o sobrescribe el archivo `requirements.txt` en la raíz del proyecto y agrega exactamente las siguientes librerías:

```text
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
oracledb>=2.0.0
pandas>=2.0.0
pydantic>=2.0.0
2. Instalación de Paquetes
Ejecuta en la terminal el siguiente comando para instalar las dependencias en el entorno virtual activo:
pip install -r requirements.txt

3. Confirmación
Verifica que la instalación haya concluido sin errores y responde confirmando que las dependencias están listas. Indica que el sistema está preparado para avanzar al paso "02-Configurar-Base-de-Datos.md".