from fastapi import APIRouter
from app.views.schemas import ServiceStatusResponse
from app.services.analitica_service import (
    get_analytics_status,
    analizar_columna
)


router = APIRouter(prefix="/analitica", tags=["Analitica"])


@router.get("/status", response_model=ServiceStatusResponse)
def get_status():
    return get_analytics_status()


@router.get("/columna/{nombre}")
def obtener_analisis_columna(nombre: str):
    return analizar_columna(nombre)