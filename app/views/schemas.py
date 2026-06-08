from pydantic import BaseModel


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