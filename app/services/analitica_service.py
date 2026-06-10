import pandas as pd

from fastapi import HTTPException

from app.database import engine


def get_analytics_status() -> dict:
    return {
        "service": "analitica",
        "status": "ready",
    }


def analizar_columna(nombre: str):

    query = """
    SELECT *
    FROM personajes_master
    """

    df = pd.read_sql(query, engine)

    columnas_validas = list(df.columns)

    if nombre not in columnas_validas:
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": "La columna no existe",
                "columnas_validas": columnas_validas
            }
        )

    tipo_columna = str(df[nombre].dtype)
    
    # Detectar categoría general del dato
    if tipo_columna in ("str", "object"):
        tipo = "categorica"

    elif tipo_columna in ("int64", "float64"):
        tipo = "numerica"

    else:
        tipo = "desconocido"

    return {
        "columna": nombre,
        "tipo_detectado": tipo_columna,
        "tipo": tipo
    }