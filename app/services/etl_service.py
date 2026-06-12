"""
SERVICIOS (BUSINESS LOGIC LAYER)

Contiene la lógica principal del sistema ETL.

Responsabilidades:
- Extraer datos desde fuentes externas.
- Transformar datos.
- Cargar información en las bases de datos.
- Ejecutar procesos analíticos.

Esta capa es independiente de los endpoints HTTP.
"""

import requests
from fastapi import HTTPException

import pandas as pd
import requests
from fastapi import HTTPException
from pymongo import UpdateOne
from sqlalchemy import text

from app.config import settings
from app.database import engine, get_raw_collection


def extraer_datos(cantidad: int) -> dict:
    """
    Extrae personajes de Rick & Morty y los guarda en MongoDB.
    Garantiza Idempotencia y PK Natural.
    """
    mongo_collection = get_raw_collection()
    url_base = f"{settings.api_base_url}/character"

    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    url_base = "https://rickandmortyapi.com/api/character"
    personajes_extraidos = []
    url_siguiente = url_base

    # 1. Extracción Paginada (Bucle while para traer la cantidad exacta)
    while url_siguiente and len(personajes_extraidos) < cantidad:
        try:
            respuesta = requests.get(url_siguiente, timeout=10)
            respuesta.raise_for_status()
            datos = respuesta.json()
            
            resultados = datos.get("results", [])
            for personaje in resultados:
                if len(personajes_extraidos) < cantidad:
                    personajes_extraidos.append(personaje)
            
            # Tomamos la URL de la siguiente página
            url_siguiente = datos.get("info", {}).get("next")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Error de red al contactar la API: {str(e)}")

    # 2. Carga en MongoDB (Garantizando Idempotencia y PK Natural)
    operaciones_bulk = []
    for p in personajes_extraidos:
        # Forzamos que el _id de Mongo sea el id original de la API
        p["_id"] = p["id"] 
        
        # Preparamos la operación Upsert (Actualizar si existe, Insertar si no)
        # Se utiliza UpdateOne con upsert=True para garantizar la idempotencia exigida en la rúbrica.
        operacion = UpdateOne(
            {"_id": p["_id"]}, # Condición de búsqueda
            {"$set": p},       # Datos a guardar
            upsert=True        # La magia de la idempotencia
        )
        operaciones_bulk.append(operacion)

    # Ejecutamos todas las operaciones de un solo golpe por rendimiento
    if operaciones_bulk:
        try:
            mongo_collection.bulk_write(operaciones_bulk)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error guardando en MongoDB: {str(e)}")
    # Optimización: Creamos un índice en el campo 'name' para acelerar futuras búsquedas analíticas
    mongo_collection.create_index("name")
    return {
        "mensaje": "Datos extraídos exitosamente",
        "registros_guardados": len(personajes_extraidos),
        "fuente": "Rick & Morty API",
        "status": 201
    }
from sqlalchemy import text
# Asegúrate de importar la conexión a MySQL que Luciano dejó configurada.
# Asumiré que se llama 'engine' o 'SessionLocal' en database.py
from app.database import engine 


def resetear_pipeline():
    """
    Limpia la colección de MongoDB y hace TRUNCATE a la tabla de MySQL (si existe).
    """
    mongo_collection = get_raw_collection()

    try:
        # 1. Limpiar MongoDB
        resultado_mongo = mongo_collection.delete_many({})
        docs_eliminados = resultado_mongo.deleted_count

        # 2. Limpiar MySQL (TRUNCATE seguro)
        mysql_status = "Tabla truncada"
        with engine.connect() as conn:
            try:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                conn.execute(text("TRUNCATE TABLE personajes_master;"))
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
                conn.commit()
            except Exception as e:
                # Si la tabla no existe (Error 1146), lo ignoramos pacíficamente
                if "1146" in str(e):
                    mysql_status = "La tabla aún no existe, no se requirió TRUNCATE"
                else:
                    raise e # Si es otro error grave, sí lo lanzamos

        return {
            "mensaje": "Sistema reseteado correctamente",
            "mongo_docs_eliminados": docs_eliminados,
            "mysql_rows_eliminadas": mysql_status,
            "status": 200
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el reset: {str(e)}")



import pandas as pd


def transformar_y_cargar():
    """
    Lee de MongoDB, aplana con Pandas y carga en MySQL.
    Garantiza idempotencia con ON DUPLICATE KEY UPDATE
    y mantiene la PK alineada entre MongoDB y MySQL.
    """
    mongo_collection = get_raw_collection()

    datos_crudos = list(mongo_collection.find())
    if not datos_crudos:
        raise HTTPException(
            status_code=400,
            detail="No hay datos en MongoDB para transformar.",
        )

    df = pd.DataFrame(datos_crudos)

    columnas_requeridas = [
        "_id",
        "name",
        "status",
        "species",
        "gender",
        "origin",
        "location",
        "episode",
    ]

    for columna in columnas_requeridas:
        if columna not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"Falta la columna requerida en MongoDB: {columna}",
            )

    df["origen_nombre"] = df["origin"].apply(
        lambda x: x.get("name") if isinstance(x, dict) else "Desconocido"
    )

    df["ubicacion_nombre"] = df["location"].apply(
        lambda x: x.get("name") if isinstance(x, dict) else "Desconocido"
    )

    df["total_episodios"] = df["episode"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )

    df["esta_vivo"] = df["status"].apply(lambda x: x == "Alive")

    columnas_finales = [
        "_id",
        "name",
        "status",
        "species",
        "gender",
        "origen_nombre",
        "ubicacion_nombre",
        "total_episodios",
        "esta_vivo",
    ]

    df_limpio = df[columnas_finales].copy()
    df_limpio.rename(columns={"_id": "id_personaje"}, inplace=True)

    columnas_texto = [
        "name",
        "status",
        "species",
        "gender",
        "origen_nombre",
        "ubicacion_nombre",
    ]

    df_limpio[columnas_texto] = df_limpio[columnas_texto].fillna("N/A")
    df_limpio["id_personaje"] = df_limpio["id_personaje"].astype(int)
    df_limpio["total_episodios"] = (
        df_limpio["total_episodios"]
        .fillna(0)
        .astype(int)
    )
    df_limpio["esta_vivo"] = (
        df_limpio["esta_vivo"]
        .fillna(False)
        .astype(bool)
    )

    registros_procesados = 0

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS personajes_master (
                id_personaje INT PRIMARY KEY,
                name VARCHAR(100),
                status VARCHAR(50),
                species VARCHAR(50),
                gender VARCHAR(50),
                origen_nombre VARCHAR(100),
                ubicacion_nombre VARCHAR(100),
                total_episodios INT,
                esta_vivo BOOLEAN
            )
        """))

        for _, row in df_limpio.iterrows():
            query = text("""
                INSERT INTO personajes_master
                (
                    id_personaje,
                    name,
                    status,
                    species,
                    gender,
                    origen_nombre,
                    ubicacion_nombre,
                    total_episodios,
                    esta_vivo
                )
                VALUES
                (
                    :id,
                    :name,
                    :status,
                    :species,
                    :gender,
                    :origen,
                    :ubicacion,
                    :episodios,
                    :esta_vivo
                )
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    status = VALUES(status),
                    species = VALUES(species),
                    gender = VALUES(gender),
                    origen_nombre = VALUES(origen_nombre),
                    ubicacion_nombre = VALUES(ubicacion_nombre),
                    total_episodios = VALUES(total_episodios),
                    esta_vivo = VALUES(esta_vivo)
            """)

            conn.execute(query, {
                "id": row["id_personaje"],
                "name": row["name"],
                "status": row["status"],
                "species": row["species"],
                "gender": row["gender"],
                "origen": row["origen_nombre"],
                "ubicacion": row["ubicacion_nombre"],
                "episodios": row["total_episodios"],
                "esta_vivo": row["esta_vivo"],
            })

            registros_procesados += 1

        conn.commit()

    return {
        "mensaje": "Pipeline finalizado",
        "registros_procesados": registros_procesados,
        "tabla_destino": "personajes_master",
        "status": 200,
    }