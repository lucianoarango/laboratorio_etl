# Laboratorio Final 2 - Pipeline ETL con FastAPI, MongoDB y MySQL

Aplicación backend desarrollada para el curso **Bases de Datos para Ciencia de Datos**. El proyecto implementa un pipeline ETL completo usando **FastAPI**, una API pública como fuente de datos, **MongoDB** para almacenar datos crudos, **MySQL** para almacenar datos transformados, **Pandas** para limpieza/transformación y **SQLAlchemy** para la conexión SQL.

La fuente seleccionada es la API pública de **Rick and Morty**:

- Documentación: https://rickandmortyapi.com/documentation
- Endpoint base: `https://rickandmortyapi.com/api`
- Recurso usado: `/character`

## Objetivo

Construir una API backend modular que permita:

- Extraer personajes desde Rick and Morty API.
- Guardar el JSON original en MongoDB como capa RAW.
- Transformar datos anidados usando Pandas.
- Cargar una tabla curada en MySQL.
- Ejecutar análisis dinámicos por columna.
- Consultar un perfil dual entre MongoDB y MySQL.
- Reiniciar el pipeline de forma segura.
- Validar calidad e idempotencia del proceso.

## Arquitectura Del Pipeline

```text
Rick and Morty API
        |
        v
POST /api/v1/etl/extraer
        |
        v
MongoDB - personajes_raw
        |
        v
POST /api/v1/etl/transformar
        |
        v
Pandas - limpieza y aplanamiento
        |
        v
MySQL - personajes_master
        |
        v
Endpoints analíticos
```

## Estructura Del Proyecto

```text
laboratorio_etl/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── app/
    ├── main.py
    ├── config.py
    ├── database.py
    ├── controllers/
    │   ├── etl_controller.py
    │   └── analitica_controller.py
    ├── services/
    │   ├── etl_service.py
    │   └── analitica_service.py
    ├── models/
    │   └── personajes_sql.py
    ├── views/
    │   └── schemas.py
    └── docs/
        └── laboratorio2_etl- Grupo_2.postman_collection.json
```

## Patrón MVC + Services

- `app/main.py`: inicializa FastAPI, crea tablas SQL e incluye routers.
- `app/config.py`: carga variables desde `.env`.
- `app/database.py`: centraliza conexiones MySQL y MongoDB.
- `app/controllers/`: define endpoints HTTP.
- `app/services/`: contiene la lógica ETL y analítica.
- `app/models/`: define modelos SQLAlchemy.
- `app/views/`: define schemas Pydantic para validación.
- `app/docs/`: contiene colección Postman para pruebas.

## Tecnologías

| Tecnología | Uso |
|---|---|
| FastAPI | API REST y Swagger |
| Uvicorn | Servidor ASGI |
| Requests | Consumo de Rick and Morty API |
| MongoDB / PyMongo | Almacenamiento RAW |
| MySQL | Almacenamiento transformado |
| SQLAlchemy | Conexión y ejecución SQL |
| Pandas | Transformación y analítica |
| Pydantic | Validación de datos |

## División De Responsabilidades

### Luciano Arango

Responsable de la infraestructura base del proyecto. Creó la estructura MVC solicitada, configuró `requirements.txt`, `.gitignore`, `.env.example`, `config.py`, `database.py`, conexiones centralizadas a MySQL/MongoDB, modelo SQLAlchemy, schemas iniciales, `main.py` y registro de routers. También realizó los ajustes finales de calidad: alineación del modelo `personajes_master`, centralización de MongoDB, schema de extracción en `views`, endpoint alias de perfil y endpoint de calidad de datos.

### Iván Durango

Responsable del pipeline ETL principal. Implementó la extracción desde Rick and Morty API, paginación, endpoint `POST /api/v1/etl/extraer`, almacenamiento RAW en MongoDB con `_id` igual al ID original de la API, idempotencia con `UpdateOne(..., upsert=True)`, endpoint `POST /api/v1/etl/transformar`, transformación con Pandas, aplanamiento de JSON anidado, carga en MySQL con `ON DUPLICATE KEY UPDATE`, endpoint `DELETE /api/v1/etl/reset`, manejo de errores y optimización con índice en MongoDB.

### Marco Peñate

Responsable de la capa analítica y documentación funcional. Implementó el endpoint `/analitica/columna/{nombre}`, validación dinámica de columnas, detección de tipos categóricos, numéricos, booleanos y fecha, endpoint de perfil dual MongoDB/MySQL, consulta del registro transformado en MySQL, comparación contra documento RAW en MongoDB, colección Postman y mejoras de documentación del uso de la API.

## Variables De Entorno

El archivo `.env` **no se sube al repositorio**. El repositorio incluye `.env.example` como plantilla.

Crear `.env` en Windows:

```powershell
Copy-Item .env.example .env
```

Crear `.env` en macOS/Linux:

```bash
cp .env.example .env
```

Contenido esperado:

```env
APP_NAME=Laboratorio ETL Rick and Morty
APP_ENV=development
API_BASE_URL=https://rickandmortyapi.com/api

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=laboratorio_etl

MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=laboratorio_etl
MONGO_RAW_COLLECTION=personajes_raw
```

## Instalación

Clonar el repositorio:

```powershell
git clone https://github.com/lucianoarango/laboratorio_etl.git
cd laboratorio_etl
git checkout develop
```

Crear entorno virtual:

```powershell
python -m venv .venv
```

Activar entorno virtual en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activar entorno virtual en macOS/Linux:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Crear la base de datos MySQL:

```sql
CREATE DATABASE laboratorio_etl CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Verificar que MongoDB y MySQL estén activos antes de ejecutar la aplicación.

## Ejecución

```powershell
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### Estado Analítica

```http
GET /analitica/status
```

Confirma que el servicio analítico está disponible.

### Extracción

```http
POST /api/v1/etl/extraer
```

Body:

```json
{
  "cantidad": 20
}
```

Extrae personajes desde Rick and Morty API y los guarda en MongoDB usando el ID original como `_id`. Es idempotente porque usa `upsert=True`.

Respuesta esperada:

```json
{
  "mensaje": "Datos extraídos exitosamente",
  "registros_guardados": 20,
  "fuente": "Rick & Morty API",
  "status": 201
}
```

### Transformación Y Carga

```http
POST /api/v1/etl/transformar
```

Lee documentos RAW desde MongoDB, transforma con Pandas, aplana `origin` y `location`, calcula `total_episodios`, crea `esta_vivo` y carga en MySQL.

Tabla destino:

```text
personajes_master
```

Columnas:

```text
id_personaje
name
status
species
gender
origen_nombre
ubicacion_nombre
total_episodios
esta_vivo
```

La PK `id_personaje` queda alineada con `_id` de MongoDB.

Respuesta esperada:

```json
{
  "mensaje": "Pipeline finalizado",
  "registros_procesados": 20,
  "tabla_destino": "personajes_master",
  "status": 200
}
```

### Reset

```http
DELETE /api/v1/etl/reset
```

Limpia MongoDB y MySQL. En MySQL usa `TRUNCATE TABLE personajes_master`, no `DROP`.

Respuesta esperada:

```json
{
  "mensaje": "Sistema reseteado correctamente",
  "mongo_docs_eliminados": 20,
  "mysql_rows_eliminadas": "Tabla truncada",
  "status": 200
}
```

### Analítica Por Columna

```http
GET /analitica/columna/{nombre}
```

Ejemplos:

```http
GET /analitica/columna/species
GET /analitica/columna/total_episodios
GET /analitica/columna/esta_vivo
```

Detecta dinámicamente si la columna es categórica, numérica, booleana o fecha. No depende de nombres hardcodeados.

Ejemplo categórico:

```json
{
  "columna": "species",
  "tipo": "categorica",
  "valores_unicos": 2,
  "distribucion": {
    "Human": 15,
    "Alien": 5
  },
  "valor_mas_comun": "Human",
  "nulos": 0
}
```

Ejemplo numérico:

```json
{
  "columna": "total_episodios",
  "tipo": "numerica",
  "min": 1.0,
  "max": 51.0,
  "promedio": 12.1,
  "mediana": 1.0,
  "desviacion_std": 19.66,
  "nulos": 0
}
```

### Perfil Dual

```http
GET /analitica/perfil/{id_personaje}
GET /perfil/{id_personaje}
```

Compara un personaje entre MongoDB y MySQL.

Casos soportados:

- Registro en ambas bases.
- Registro solo en MongoDB.
- Registro solo en MySQL.
- Registro inexistente.

Ejemplo:

```json
{
  "id": 3,
  "mongo": {
    "id": 3,
    "name": "Summer Smith",
    "status": "Alive",
    "species": "Human",
    "gender": "Female"
  },
  "mysql": {
    "id_personaje": 3,
    "name": "Summer Smith",
    "status": "Alive",
    "species": "Human",
    "gender": "Female",
    "origen_nombre": "Earth (Replacement Dimension)",
    "ubicacion_nombre": "Earth (Replacement Dimension)",
    "total_episodios": 42,
    "esta_vivo": true
  },
  "warning": null
}
```

### Calidad De Datos

```http
GET /analitica/calidad-datos
```

Valida:

- Total de documentos en MongoDB.
- Total de registros en MySQL.
- Cantidad de columnas SQL.
- Mínimo de 8 columnas.
- IDs duplicados.
- IDs presentes solo en MongoDB.
- IDs presentes solo en MySQL.
- Alineación entre `_id` e `id_personaje`.

Ejemplo:

```json
{
  "tabla_mysql": "personajes_master",
  "coleccion_mongo": "personajes_raw",
  "mongo_total_documentos": 20,
  "mysql_total_registros": 20,
  "sql_columnas": 9,
  "sql_minimo_8_columnas": true,
  "mysql_ids_duplicados": 0,
  "ids_solo_en_mongo_total": 0,
  "ids_solo_en_mysql_total": 0,
  "ids_solo_en_mongo_muestra": [],
  "ids_solo_en_mysql_muestra": [],
  "pk_alineada": true,
  "estado": "ok"
}
```

## Idempotencia

MongoDB usa `UpdateOne` con `upsert=True`:

```python
UpdateOne({"_id": p["_id"]}, {"$set": p}, upsert=True)
```

MySQL usa `ON DUPLICATE KEY UPDATE`:

```sql
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    status = VALUES(status),
    species = VALUES(species),
    gender = VALUES(gender),
    origen_nombre = VALUES(origen_nombre),
    ubicacion_nombre = VALUES(ubicacion_nombre),
    total_episodios = VALUES(total_episodios),
    esta_vivo = VALUES(esta_vivo)
```

Esto permite ejecutar extracción y transformación varias veces sin duplicar registros.

## Transformación De Datos

El proceso de transformación realiza:

- Lectura de documentos RAW desde MongoDB.
- Conversión a `DataFrame`.
- Validación de columnas requeridas.
- Aplanamiento de `origin.name` en `origen_nombre`.
- Aplanamiento de `location.name` en `ubicacion_nombre`.
- Cálculo de `total_episodios`.
- Creación de variable booleana `esta_vivo`.
- Limpieza de nulos.
- Conversión de tipos.
- Carga idempotente en MySQL.

## Consultas De Validación En MySQL

```sql
SELECT COUNT(*) AS total_mysql
FROM personajes_master;

SELECT COUNT(DISTINCT id_personaje) AS ids_unicos_mysql
FROM personajes_master;

SELECT id_personaje, COUNT(*) AS repeticiones
FROM personajes_master
GROUP BY id_personaje
HAVING COUNT(*) > 1;

DESCRIBE personajes_master;

SELECT *
FROM personajes_master
LIMIT 20;
```

## Consultas De Validación En MongoDB

```javascript
db.personajes_raw.countDocuments()

db.personajes_raw.findOne()

db.personajes_raw.aggregate([
  { $group: { _id: "$_id", total: { $sum: 1 } } },
  { $match: { total: { $gt: 1 } } }
])
```


## Checklist De Calidad

Se verifica que se cumpla con el checklist de calidad propuesto para el Laboratorio 2 y con la Rúbrica de Evaluación. 

- Repositorio público.
- README con división de responsabilidades.
- Estructura MVC + Services.
- `.env` excluido mediante `.gitignore`.
- `.env.example` incluido como plantilla.
- Extracción idempotente en MongoDB.
- Transformación idempotente en MySQL.
- PK alineada entre MongoDB y MySQL.
- Reset con `TRUNCATE`, no `DROP`.
- Analítica dinámica por columna.
- Perfil dual con manejo de casos.
- Tabla SQL con mínimo 8 columnas.
- Mínimo 10 commits por integrante.

## Evidencia De Trabajo En Git

En la rama `develop` se evidencia el trabajo colaborativo mediante commits individuales y Pull Requests:

- Luciano Arango: infraestructura, configuración, conexiones, modelos, routers y ajustes finales de calidad.
- Iván Durango: endpoints ETL, extracción, transformación, carga, reset e idempotencia.
- Marco Peñate: endpoints analíticos, perfil dual, documentación y colección Postman.

Cada integrante cuenta con mínimo 10 commits en el repositorio.

## Repositorio

https://github.com/lucianoarango/laboratorio_etl

