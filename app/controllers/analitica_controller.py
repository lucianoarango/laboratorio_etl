from fastapi import APIRouter

from app.services.analitica_service import get_analytics_status
from app.views.schemas import ServiceStatusResponse


router = APIRouter(prefix="/analitica", tags=["Analitica"])


@router.get("/status", response_model=ServiceStatusResponse)
def get_status():
    return get_analytics_status()