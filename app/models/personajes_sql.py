from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class PersonajeSQL(Base):
    __tablename__ = "personajes_master"

    id_personaje = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=True)
    species = Column(String(50), nullable=True)
    gender = Column(String(50), nullable=True)
    origen_nombre = Column(String(100), nullable=True)
    ubicacion_nombre = Column(String(100), nullable=True)
    total_episodios = Column(Integer, nullable=False, default=0)
    esta_vivo = Column(Boolean, nullable=False, default=False)