from pydantic import BaseModel, Field
from typing import List


class ExtraccionRequest(BaseModel):
    cantidad: int = Field(
        gt=0,
        description="Cantidad de personajes a extraer desde Rick and Morty API",
    )


class AppInfoResponse(BaseModel):
    app_name: str
    environment: str
    source_api: str


class DatabaseStatusResponse(BaseModel):
    mysql: str
    mongo: str


class SourceMetadataResponse(BaseModel):
    name: str
    base_url: str
    characters_endpoint: str


class ServiceStatusResponse(BaseModel):
    service: str
    status: str


class DataQualityResponse(BaseModel):
    tabla_mysql: str
    coleccion_mongo: str
    mongo_total_documentos: int
    mysql_total_registros: int
    sql_columnas: int
    sql_minimo_8_columnas: bool
    mysql_ids_duplicados: int
    ids_solo_en_mongo_total: int
    ids_solo_en_mysql_total: int
    ids_solo_en_mongo_muestra: List[int]
    ids_solo_en_mysql_muestra: List[int]
    pk_alineada: bool
    estado: str