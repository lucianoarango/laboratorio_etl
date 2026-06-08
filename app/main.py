from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.controllers import analitica_controller, etl_controller
from app.database import create_mysql_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_mysql_tables()
        app.state.database_startup_error = None
    except Exception as exc:
        app.state.database_startup_error = str(exc)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Backend ETL con FastAPI, MongoDB, MySQL, Pandas y SQLAlchemy.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(etl_controller.router)
app.include_router(analitica_controller.router)