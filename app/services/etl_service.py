import requests
from pymongo import MongoClient, UpdateOne
from fastapi import HTTPException
import os

# Conexión a MongoDB usando la variable de entorno
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["etl_db"]
mongo_collection = mongo_db["raw_data"]

def extraer_datos(cantidad: int):
    """
    Extrae personajes de Rick & Morty y los guarda en MongoDB.
    Garantiza Idempotencia y PK Natural.
    """
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    url_base = "https://rickandmortyapi.com/api/character"
    personajes_extraidos = []
    url_siguiente = url_base

    # 1. Extracción Paginada (Bucle while para traer la cantidad exacta)
    while url_siguiente and len(personajes_extraidos) < cantidad:
        try:
            respuesta = requests.get(url_siguiente)
            respuesta.raise_for_status()
            datos = respuesta.json()
            
            resultados = datos.get("results", [])
            for personaje in resultados:
                if len(personajes_extraidos) < cantidad:
                    personajes_extraidos.append(personaje)
            
            # Tomamos la URL de la siguiente página
            url_siguiente = datos.get("info", {}).get("next")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error consultando la API: {str(e)}")

    # 2. Carga en MongoDB (Garantizando Idempotencia y PK Natural)
    operaciones_bulk = []
    for p in personajes_extraidos:
        # Forzamos que el _id de Mongo sea el id original de la API
        p["_id"] = p["id"] 
        
        # Preparamos la operación Upsert (Actualizar si existe, Insertar si no)
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
    Garantiza Idempotencia (ON DUPLICATE KEY UPDATE) y PK Alineada.
    """
    # 1. EXTRACT (Desde MongoDB)
    datos_crudos = list(mongo_collection.find())
    if not datos_crudos:
        raise HTTPException(status_code=400, detail="No hay datos en MongoDB para transformar.")

    # 2. TRANSFORM (Con Pandas)
    df = pd.DataFrame(datos_crudos)

    # Aplanamiento: La API de Rick & Morty trae 'origin' y 'location' como diccionarios.
    # Extraemos solo el nombre y creamos columnas planas.
    df['origen_nombre'] = df['origin'].apply(lambda x: x.get('name') if isinstance(x, dict) else 'Desconocido')
    df['ubicacion_nombre'] = df['location'].apply(lambda x: x.get('name') if isinstance(x, dict) else 'Desconocido')
    
    # Derivada: Contamos cuántos episodios tiene el personaje
    df['total_episodios'] = df['episode'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    
    
    # Variable derivada booleana
    df['esta_vivo'] = df['status'].apply(
        lambda x: True if x == "Alive" else False
    )

    # Seleccionamos al menos 8 columnas exigidas por la rúbrica
    columnas_finales = ['_id', 'name', 'status', 'species', 'gender', 'origen_nombre', 'ubicacion_nombre', 'total_episodios', 'esta_vivo']
    df_limpio = df[columnas_finales].copy()

    # Renombramos '_id' a 'id_personaje' para MySQL (PK Alineada)
    df_limpio.rename(columns={'_id': 'id_personaje'}, inplace=True)

    # Manejo de nulos
    df_limpio.fillna('N/A', inplace=True)

    # 3. LOAD (Hacia MySQL)
    registros_procesados = 0
    with engine.connect() as conn:
        # Resiliencia: Creamos la tabla si no existe
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

        # Inserción con Idempotencia (Upsert en MySQL)
        for _, row in df_limpio.iterrows():
            query = text("""
                INSERT INTO personajes_master 
                (id_personaje, name, status, species, gender, origen_nombre, ubicacion_nombre, total_episodios, esta_vivo)
                VALUES (:id, :name, :status, :species, :gender, :origen, :ubicacion, :episodios, :esta_vivo)
                ON DUPLICATE KEY UPDATE
                name=VALUES(name), status=VALUES(status), species=VALUES(species), 
                gender=VALUES(gender), origen_nombre=VALUES(origen_nombre), 
                ubicacion_nombre=VALUES(ubicacion_nombre), total_episodios=VALUES(total_episodios)
            """)
            conn.execute(query, {
                "id": row['id_personaje'], "name": row['name'], "status": row['status'],
                "species": row['species'], "gender": row['gender'], "origen": row['origen_nombre'],
                "ubicacion": row['ubicacion_nombre'], "episodios": row['total_episodios'], "esta_vivo": row["esta_vivo"]
            })
            registros_procesados += 1
        
        conn.commit()

    return {
        "mensaje": "Pipeline finalizado",
        "registros_procesados": registros_procesados,
        "tabla_destino": "personajes_master",
        "status": 200
    }