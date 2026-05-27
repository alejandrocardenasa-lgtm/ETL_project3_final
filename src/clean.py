import pandas as pd
import os

def clean_meteostat():
    df = pd.read_csv("data/raw/meteostat_daily_globalv2.csv")

    print("Iniciando limpieza Meteostat")

    # normalizacion de columnas
    df.columns = df.columns.str.strip().str.lower()

    # conversion de fecha
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # limpieza de ciudad
    df["city"] = (
        df["city"]
        .astype(str)
        .str.replace("_", " ", regex=False)
        .str.strip()
        .str.title()
    )

    # conversion de temperaturas
    for col in ["tavg", "tmin", "tmax"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # seleccion de variables
    df = df[["city", "date", "tavg", "tmin", "tmax"]]

    # eliminacion de nulos
    df = df.dropna(subset=["city", "date", "tavg", "tmin", "tmax"])

    # validacion de rangos
    df = df[
        (df["tavg"].between(-50, 60)) &
        (df["tmin"].between(-50, 60)) &
        (df["tmax"].between(-50, 60))
    ]

    # consistencia de temperaturas
    df = df[
        (df["tavg"] >= df["tmin"]) &
        (df["tmax"] >= df["tavg"])
    ]

    # eliminacion de duplicados
    df = df.drop_duplicates(subset=["city", "date"])

    # guardado de datos limpios
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/meteostat_clean.csv", index=False)

    print("Limpieza Meteostat terminada")
    print("Shape:", df.shape)

    return df