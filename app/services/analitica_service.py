import pandas as pd

from pandas.api.types import is_datetime64_any_dtype

from fastapi import HTTPException

from app.database import engine

from app.database import mongo_db

from sqlalchemy import text


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

        distribucion = (
            df[nombre]
            .value_counts()
            .to_dict()
        )

        valor_mas_comun = (
            df[nombre]
            .mode()
            .iloc[0]
        )

        return {
            "columna": nombre,
            "tipo": "categorica",
            "valores_unicos": int(df[nombre].nunique()),
            "distribucion": distribucion,
            "valor_mas_comun": valor_mas_comun,
            "nulos": int(df[nombre].isna().sum())
        }

    elif tipo_columna in ("int64", "float64"):

        return {
            "columna": nombre,
            "tipo": "numerica",
            "min": float(df[nombre].min()),
            "max": float(df[nombre].max()),
            "promedio": round(float(df[nombre].mean()), 2),
            "mediana": float(df[nombre].median()),
            "desviacion_std": round(float(df[nombre].std()), 2),
            "nulos": int(df[nombre].isna().sum())
        }
    #Se agregó con la principal funcionalidad de que se pueda trabajar con fechas en cualquier API, aunque
    #para esta en especifico no sea el caso       
    elif is_datetime64_any_dtype(df[nombre]):

        fecha_min = df[nombre].min()
        fecha_max = df[nombre].max()

        return {
            "columna": nombre,
            "tipo": "fecha",
            "min": str(fecha_min),
            "max": str(fecha_max),
            "rango_dias": int((fecha_max - fecha_min).days),
            "nulos": int(df[nombre].isna().sum())
        }        

    else:
        tipo = "desconocido"
    

    return {
        "columna": nombre,
        "tipo_detectado": tipo_columna,
        "tipo": tipo
    }


def obtener_perfil_dual(id_personaje: int):

    documento_mongo = mongo_db["raw_data"].find_one(
        {"_id": id_personaje}
    )

    query = text("""
        SELECT *
        FROM personajes_master
        WHERE id_personaje = :id
    """)

    with engine.connect() as conn:
        resultado_mysql = conn.execute(
            query,
            {"id": id_personaje}
        ).mappings().first()

    return {
        "id": id_personaje,
        "mongo_encontrado": documento_mongo is not None,
        "mysql_encontrado": resultado_mysql is not None
    }