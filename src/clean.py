import pandas as pd
import os

def clean_meteostat():

    df = pd.read_csv("data/raw/meteostat_daily_globalv2.csv")

    print("Iniciando limpieza")

    # convertir fecha
    df["date"] = pd.to_datetime(df["date"])

    # arreglar ciudad
    df["city"] = df["city"].str.replace("_", " ", regex=False)

    # eliminar columna 100% nula
    df = df.drop(columns=["wdir"], errors="ignore")

    # eliminar filas sin temperatura 
    df = df.dropna(subset=["tavg", "tmin", "tmax"])

    # eliminar duplicados (por seguridad)
    df = df.drop_duplicates()

    # guardar en processed
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/meteostat_clean.csv", index=False)

    print("Limpieza terminada")
    print("Shape:", df.shape)

    return df