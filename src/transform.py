import pandas as pd
import os


def transform_datasets():
    print("Iniciando transformacion e integracion")

    # lectura de fuentes
    df_ideam = pd.read_csv("data/raw/temperature_observations_colombia_transformed.csv")
    df_meteostat = pd.read_csv("data/processed/meteostat_clean.csv")

    # transformacion IDEAM
    df_ideam.columns = df_ideam.columns.str.strip().str.lower()

    df_ideam["fechaobservacion"] = pd.to_datetime(
        df_ideam["fechaobservacion"],
        errors="coerce"
    )

    # conversion de fecha
    df_ideam["date"] = pd.to_datetime(df_ideam["fechaobservacion"].dt.date)

    # limpieza de ciudad
    df_ideam["city"] = (
        df_ideam["municipio"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # conversion de temperatura
    df_ideam["valorobservado"] = pd.to_numeric(
        df_ideam["valorobservado"],
        errors="coerce"
    )

    # eliminacion de nulos
    df_ideam = df_ideam.dropna(subset=["city", "date", "valorobservado"])

    # validacion de rango
    df_ideam = df_ideam[df_ideam["valorobservado"].between(-50, 60)]

    # agregacion diaria
    df_ideam_grouped = df_ideam.groupby(["city", "date"], as_index=False).agg({
        "valorobservado": ["mean", "min", "max"]
    })

    # renombrar medidas
    df_ideam_grouped.columns = [
        "city",
        "date",
        "temperatura_promedio",
        "temperatura_minima",
        "temperatura_maxima"
    ]

    # asignacion de fuente
    df_ideam_grouped["source_id"] = 1

    # transformacion Meteostat
    df_meteostat["date"] = pd.to_datetime(df_meteostat["date"])

    # renombrar medidas
    df_meteostat = df_meteostat.rename(columns={
        "tavg": "temperatura_promedio",
        "tmin": "temperatura_minima",
        "tmax": "temperatura_maxima"
    })

    # seleccion de variables
    df_meteostat = df_meteostat[[
        "city",
        "date",
        "temperatura_promedio",
        "temperatura_minima",
        "temperatura_maxima"
    ]]

    # asignacion de fuente
    df_meteostat["source_id"] = 2

    # integracion de fuentes
    df_integrado = pd.concat(
        [df_ideam_grouped, df_meteostat],
        ignore_index=True
    )

    # eliminacion de duplicados
    df_integrado = df_integrado.drop_duplicates(
        subset=["city", "date", "source_id"]
    )

    # calculo de amplitud termica
    df_integrado["amplitud_termica"] = (
        df_integrado["temperatura_maxima"] -
        df_integrado["temperatura_minima"]
    )

    # identificacion de calor extremo
    df_integrado["evento_calor_extremo"] = df_integrado["temperatura_maxima"].apply(
        lambda x: 1 if x >= 35 else 0
    )

    # dimension ciudad
    dim_city = df_integrado[["city"]].drop_duplicates().reset_index(drop=True)
    dim_city["city_id"] = dim_city.index + 1
    dim_city = dim_city[["city_id", "city"]]

    # dimension fecha
    dim_date = df_integrado[["date"]].drop_duplicates().reset_index(drop=True)
    dim_date["date_id"] = dim_date.index + 1
    dim_date["anio"] = dim_date["date"].dt.year
    dim_date["mes"] = dim_date["date"].dt.month
    dim_date["dia"] = dim_date["date"].dt.day
    dim_date["semana"] = dim_date["date"].dt.isocalendar().week.astype(int)
    dim_date["trimestre"] = dim_date["date"].dt.quarter
    dim_date["es_fin_de_semana"] = dim_date["date"].dt.dayofweek >= 5

    dim_date = dim_date[[
        "date_id",
        "date",
        "anio",
        "mes",
        "dia",
        "semana",
        "trimestre",
        "es_fin_de_semana"
    ]]

    # dimension fuente
    dim_source = pd.DataFrame({
        "source_id": [1, 2],
        "nombre_fuente": ["IDEAM", "Meteostat"],
        "tipo_fuente": ["CSV", "API"]
    })

    # creacion de tabla de hechos
    fact_climate_daily = df_integrado.merge(dim_city, on="city", how="left")
    fact_climate_daily = fact_climate_daily.merge(dim_date, on="date", how="left")

    # seleccion de columnas fact
    fact_climate_daily = fact_climate_daily[[
        "city_id",
        "date_id",
        "source_id",
        "temperatura_promedio",
        "temperatura_minima",
        "temperatura_maxima",
        "amplitud_termica",
        "evento_calor_extremo"
    ]]

    # validacion de grano
    fact_climate_daily = fact_climate_daily.drop_duplicates(
        subset=["city_id", "date_id", "source_id"]
    )

    # guardado de archivos procesados
    os.makedirs("data/processed", exist_ok=True)

    dim_city.to_csv("data/processed/dim_city.csv", index=False)
    dim_date.to_csv("data/processed/dim_date.csv", index=False)
    dim_source.to_csv("data/processed/dim_source.csv", index=False)
    fact_climate_daily.to_csv("data/processed/fact_climate_daily.csv", index=False)

    print("Transformacion e integracion completadas")
    print("dim_city:", dim_city.shape)
    print("dim_date:", dim_date.shape)
    print("dim_source:", dim_source.shape)
    print("fact_climate_daily:", fact_climate_daily.shape)

    return dim_city, dim_date, dim_source, fact_climate_daily