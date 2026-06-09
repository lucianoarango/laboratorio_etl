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