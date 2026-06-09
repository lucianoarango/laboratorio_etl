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