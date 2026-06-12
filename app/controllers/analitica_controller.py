from fastapi import APIRouter
from app.views.schemas import ServiceStatusResponse
from app.services.analitica_service import (
    get_analytics_status,
    analizar_columna,
    obtener_calidad_datos, 
    obtener_perfil_dual, 
)
from app.views.schemas import DataQualityResponse, ServiceStatusResponse


router = APIRouter(prefix="/analitica", tags=["Analitica"])

perfil_router = APIRouter(tags=["Perfil"])

@router.get("/status", response_model=ServiceStatusResponse)
def get_status():
    return get_analytics_status()


@router.get("/columna/{nombre}")
def obtener_analisis_columna(nombre: str):
    return analizar_columna(nombre)


@router.get("/perfil/{id_personaje}")
def obtener_perfil(id_personaje: int):
    return obtener_perfil_dual(id_personaje)

@perfil_router.get("/perfil/{id_personaje}")
def obtener_perfil_alias(id_personaje: int):
    return obtener_perfil_dual(id_personaje)

@router.get("/calidad-datos", response_model=DataQualityResponse)
def obtener_reporte_calidad():
    return obtener_calidad_datos()