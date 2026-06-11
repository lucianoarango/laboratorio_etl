# Laboratorio Final 2 - Pipeline ETL con FastAPI, MongoDB y MySQL

Proyecto desarrollado para la asignatura **Bases de Datos para Ciencia de Datos**.

La aplicación implementa un pipeline ETL completo utilizando:

* FastAPI para ostentar la presentación de endpoints.
* API pública de Rick and Morty como fuente de datos.
* MongoDB para almacenamiento RAW.
* MySQL para almacenamiento transformado.
* Pandas que cumple con la transformación de datos.
* SQLAlchemy usada para la conexión y operaciones SQL.

El objetivo del laboratorio es demostrar un flujo completo de extracción, transformación, carga y análisis de datos siguiendo un buen flujo de trabajo relacionado a ingeniería de datos.

---

# API seleccionada

Se utiliza la API pública de Rick and Morty:

* Documentación: https://rickandmortyapi.com/documentation
* Endpoint utilizado: `https://rickandmortyapi.com/api/character`
* Tipo de datos: personajes, especies, estados, géneros, ubicaciones y episodios.

La API no requiere autenticación y permite consulta paginada.

---

# Arquitectura del Pipeline

```text
Rick and Morty API
          |
          v
     Extracción
          |
          v
MongoDB (RAW)
          |
          v
 Transformación
   con Pandas
          |
          v
 MySQL (Curado)
          |
          v
 Analítica SQL
```

---

# Estructura del Proyecto

```text
laboratorio_etl/
│
├── app/
│   ├── controllers/
│   ├── services/
│   ├── models/
│   ├── views/
│   ├── database.py
│   ├── config.py
│   └── main.py
│
├── .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Tecnologías Utilizadas

| Tecnología | Propósito                   |
| ---------- | --------------------------- |
| FastAPI    | API REST                    |
| MongoDB    | Almacenamiento RAW          |
| MySQL      | Almacenamiento transformado |
| Pandas     | Limpieza y transformación   |
| SQLAlchemy | Persistencia SQL            |
| PyMongo    | Persistencia Mongo          |
| Uvicorn    | Servidor ASGI               |

---
---

# Configuración y ejecución para el funcionamiento de la API.

# Configuración del Entorno

Crear entorno virtual:

```powershell
python -m venv .venv
```

Activar entorno:

```powershell
.venv\Scripts\activate
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Crear archivo `.env`:

```powershell
Copy-Item .env.example .env
```

Configurar credenciales de MongoDB y MySQL.

---

# Ejecución

Iniciar servidor:

```powershell
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---


# Pipeline ETL

## 1. Extracción

Endpoint:

```http
POST /api/v1/etl/extraer
```

Body:

```json
{
  "cantidad": 20
}
```

Responsabilidades:

* Consumir la API pública.
* Obtener la cantidad solicitada.
* Realizar paginación automática.
* Guardar documentos RAW en MongoDB.
* Mantener idempotencia mediante Upsert.

---

## 2. Transformación y Carga

Endpoint:

```http
POST /api/v1/etl/transformar
```

Responsabilidades:

* Leer datos desde MongoDB.
* Convertir datos a DataFrame.
* Aplanar estructuras anidadas.
* Crear variables derivadas.
* Seleccionar mínimo 8 columnas.
* Cargar datos en MySQL.

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
```

---

## 3. Reset del Pipeline

Endpoint:

```http
DELETE /api/v1/etl/reset
```

Responsabilidades:

* Eliminar documentos RAW de MongoDB.
* Limpiar la tabla transformada de MySQL.
* Reiniciar el estado del pipeline.

---

# Endpoint Analítico

## Análisis por Columna

Endpoint:

```http
GET /api/v1/analitica/columna/{nombre}
```

Características:

* Validación dinámica de columnas.
* Detección automática de tipos.
* Sin hardcodear nombres específicos.

Tipos soportados:

### Categórica

Ejemplo:

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

### Numérica

Ejemplo:

```json
{
  "columna": "total_episodios",
  "tipo": "numerica",
  "min": 1,
  "max": 51,
  "promedio": 12.1,
  "mediana": 1,
  "desviacion_std": 19.66,
  "nulos": 0
}
```

### Fecha

Soporte implementado para futuras APIs con columnas temporales.

---

# Endpoint Perfil Dual

Endpoint:

```http
GET /api/v1/perfil/{id}
```

Objetivo:

Comparar visualmente el mismo registro entre MongoDB y MySQL.

Ejemplo:

```json
{
  "id": 3,
  "mongo": {...},
  "mysql": {...}
}
```

Casos soportados:

* Registro en ambas bases.
* Registro solo en MongoDB.
* Registro solo en MySQL.
* Registro inexistente.

---

# Principios Aplicados

## Idempotencia

MongoDB:

```python
UpdateOne(..., upsert=True)
```

MySQL:

```sql
ON DUPLICATE KEY UPDATE
```

Evita duplicados al ejecutar múltiples veces el pipeline.

---

## Trazabilidad

MongoDB conserva el JSON original obtenido desde la API.

---

## Bajo Acoplamiento

Separación por capas:

* Controllers
* Services
* Models
* Views

---

## Escalabilidad

El análisis detecta dinámicamente el tipo de columna y puede adaptarse a nuevas APIs sin modificar la lógica principal.


# Estado Verificado

* Conexión MySQL funcional.
* Conexión MongoDB funcional.
* Extracción desde API validada.
* Transformación validada.
* Carga validada.
* Reset validado.
* Analítica validada.
* Perfil dual validado.
* Swagger funcional.
* Postman funcional.

---

# Integrantes

* Luciano Arango
* Iván Cogollo
* Marco Peñate

---

# Repositorio

Repositorio público: https://github.com/lucianoarango/laboratorio_etl
