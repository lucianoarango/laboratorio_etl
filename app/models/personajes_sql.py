from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class PersonajeSQL(Base):
    __tablename__ = "personajes"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, unique=True, nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    estado = Column(String(50), nullable=True)
    especie = Column(String(80), nullable=True)
    tipo = Column(String(120), nullable=True)
    genero = Column(String(50), nullable=True)
    origen = Column(String(160), nullable=True)
    ubicacion = Column(String(160), nullable=True)
    imagen = Column(String(255), nullable=True)
    numero_episodios = Column(Integer, nullable=False, default=0)
    url = Column(String(255), nullable=True)
    fecha_creacion_api = Column(DateTime, nullable=True)
    fecha_carga = Column(DateTime, nullable=False, server_default=func.now())