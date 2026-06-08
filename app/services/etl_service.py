from app.config import settings


def get_source_metadata() -> dict:
    return {
        "name": "Rick and Morty API",
        "base_url": settings.api_base_url,
        "characters_endpoint": f"{settings.api_base_url}/character",
    }