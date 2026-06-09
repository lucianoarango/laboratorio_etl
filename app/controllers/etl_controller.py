from fastapi import APIRouter
from app.services import etl_service
from pydantic import BaseModel

router = APIRouter()

# Definimos el esquema (View) que exige el PDF para el Body
class ExtraccionRequest(BaseModel):
    cantidad: int

@router.post("/api/v1/etl/extraer", status_code=201)
def extraer_datos_api(request: ExtraccionRequest):
    return etl_service.extraer_datos(request.cantidad)

@router.delete("/api/v1/etl/reset", status_code=200)
def resetear_datos():
    return etl_service.resetear_pipeline()


@router.post("/api/v1/etl/transformar", status_code=200)
def transformar_datos():
    return etl_service.transformar_y_cargar()