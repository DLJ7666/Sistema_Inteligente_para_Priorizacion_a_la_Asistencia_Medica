# Guía de Instalación y Ejecución

Esta guía detalla los pasos necesarios para configurar el entorno de desarrollo, instalar las dependencias e iniciar el servidor de la aplicación.

## 0. Requisitos Previos

Asegúrate de tener instalado en tu sistema:

* **Python** (versión 3.9 o superior recomendada).
* **Pip** (gestor de paquetes de Python).

## 1. Configuración del Entorno Virtual

1. Abre tu terminal y sitúate en la carpeta raíz del proyecto `python`:
```bash
cd python
```

2. Crea un entorno virtual dentro de la carpeta:
```bash
python -m venv venv
```

3. Activa el entorno virtual:
* **En Windows (CMD / PowerShell):**
```bash
venv\Scripts\activate
```

* **En macOS / Linux:**
```bash
source venv/bin/activate
```

## 2. Instalación de Dependencias

Una vez activado el entorno virtual, instala las librerías necesarias ejecutando:

```bash
pip install -r requirements.txt
```

## 3. Configuración de Variables de Entorno

Crea un archivo `.env` en la carpeta raíz del proyecto. Copia el archivo `.env copy` que encontrarás en dicha carpeta, y rellena los datos como se indica abajo

```env
PROJECT_NAME="SIPAM - API REST"
VERSION="1.0.0"
ENTORNO="" # "BASE" para producción/desarrollo, o "TEST" para pruebas
API_V1_STR="/api/v1"

# --- Conexión PostgreSQL / Supabase ---
POSTGRES_SERVER= # Servidor donde se ejecute la base de datos
SUPABASE_URL= # URL del servidor de Supabase
POSTGRES_ANON_KEY= # Clave anónima de Supabase
POSTGRES_PORT= # Puerto de escucha de la base de datos 
POSTGRES_USER= # Usuario de la base de datos
POSTGRES_PASSWORD= # Contraseña del usuario de la base de datos 
POSTGRES_DB= # Nombre de la base de datos

# --- Seguridad JWT ---
SUPABASE_JWT_SECRET= Clave de validación de usuarios JWT de Supabase
ALGORITHM="ES256"
```

## 4. Lanzamiento de la Aplicación

Para iniciar el servidor de desarrollo mediante **Uvicorn**, ejecuta el siguiente comando desde la carpeta raiz del proyecto:

```bash
uvicorn app.main:app
```

## 5. Verificación del Funcionamiento

Una vez iniciado el servidor, podrás comprobar que todo funciona correctamente abriendo tu navegador web e ingresando a las siguientes rutas:

* **Documentación interactiva (Swagger UI):**
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 6. Ejecución de Tests y Pruebas

El proyecto cuenta con una suite de pruebas dividida en pruebas unitarias, de extremo a extremo (E2E) y no funcionales. Para ejecutarlas correctamente, asegúrate de activar primero tu entorno virtual y situarte en la carpeta raíz:

```bash
# Activa tu entorno virtual (si no lo tienes activo)
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
```

### 1. Pruebas Unitarias

* **Ejecución:**

```bash
pytest tests/unit/
```

### 2. Pruebas End-to-End (E2E)

* **Ejecución:**

```bash
python tests/end-to-end/test_postman.py
```

### 3. Pruebas No Funcionales

* **Pruebas de carga y estrés:**

Para ejecutar las simulaciones de tráfico concurrente, láncese el siguiente comando apuntando al archivo de configuración:

```bash
locust -f tests/non-functional/locustfile.py
```

Una vez ejecutado, ábrase el navegador e ingrésese a [http://localhost:8089](http://localhost:8089) para configurar el número de usuarios concurrentes y la tasa de peticiones desde la interfaz gráfica de Locust.

* **Resto de pruebas no funcionales:**

```bash
pytest tests/non-functional/tests_non_functional
```
