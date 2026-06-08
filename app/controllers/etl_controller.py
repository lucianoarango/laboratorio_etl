from fastapi import APIRouter

from app.config import settings
from app.database import check_mongo_connection, check_mysql_connection
from app.services.etl_service import get_source_metadata
from app.views.schemas import (
    AppInfoResponse,
    DatabaseStatusResponse,
    SourceMetadataResponse,
)


router = APIRouter()


@router.get("/", response_model=AppInfoResponse, tags=["Sistema"])
def get_app_info():
    return {
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "source_api": settings.api_base_url,
    }


@router.get("/health", response_model=DatabaseStatusResponse, tags=["Sistema"])
def health_check():
    return {
        "mysql": "ok" if check_mysql_connection() else "error",
        "mongo": "ok" if check_mongo_connection() else "error",
    }


@router.get("/etl/source", response_model=SourceMetadataResponse, tags=["ETL"])
def get_etl_source():
    return get_source_metadata()