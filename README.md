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
## 3. Lanzamiento de la Aplicación

Para iniciar el servidor de desarrollo mediante **Uvicorn**, ejecuta el siguiente comando desde la carpeta raiz del proyecto:

```bash
uvicorn app.main:app

```
## 4. Verificación del Funcionamiento

Una vez iniciado el servidor, podrás comprobar que todo funciona correctamente abriendo tu navegador web e ingresando a las siguientes rutas:

* **Documentación interactiva (Swagger UI):**
[http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs)
