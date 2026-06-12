"""
CONFIGURACIÓN DE BASE DE DATOS

Este módulo centraliza las conexiones a las bases de datos utilizadas
por el proyecto.

Bases utilizadas:
- MongoDB (almacenamiento temporal/raw data)
- MySQL (almacenamiento estructurado)

Permite reutilizar las conexiones en toda la aplicación.
"""

from pymongo import MongoClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


engine = create_engine(settings.mysql_url, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

mongo_client = MongoClient(settings.mongo_uri)
mongo_db = mongo_client[settings.mongo_database]
raw_collection = mongo_db[settings.mongo_raw_collection]


def get_mysql_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo_database():
    return mongo_db


def get_raw_collection():
    return raw_collection


def check_mysql_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_mongo_connection() -> bool:
    try:
        mongo_client.admin.command("ping")
        return True
    except Exception:
        return False
    

def create_mysql_tables() -> None:
    import app.models.personajes_sql

    Base.metadata.create_all(bind=engine)