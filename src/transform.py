import pandas as pd
import os

def transform_datasets():
    print("Iniciando transformacion e integracion")

    # 1. Leer datasets
    df_ideam = pd.read_csv("data/raw/temperature_observations_colombia_transformed.csv")
    df_meteostat = pd.read_csv("data/processed/meteostat_clean.csv")

   
    # 2. Transformar Ideam
    df_ideam.columns = df_ideam.columns.str.strip().str.lower()

    # convertir fecha
    df_ideam["fechaobservacion"] = pd.to_datetime(df_ideam["fechaobservacion"])
    df_ideam["date"] = df_ideam["fechaobservacion"].dt.date
    df_ideam["date"] = pd.to_datetime(df_ideam["date"])

    # municipio como city
    df_ideam["city"] = df_ideam["municipio"].astype(str).str.strip().str.title()

    # valorobservado a numerico
    df_ideam["valorobservado"] = pd.to_numeric(df_ideam["valorobservado"], errors="coerce")

    # agrupar a nivel ciudad + fecha
    df_ideam_grouped = df_ideam.groupby(["city", "date"], as_index=False).agg({
        "valorobservado": ["mean", "min", "max"]
    })

    df_ideam_grouped.columns = [
        "city",
        "date",
        "temperatura_promedio",
        "temperatura_minima",
        "temperatura_maxima"
    ]

    # columnas que IDEAM no trae en este dataset
    df_ideam_grouped["precipitacion"] = pd.NA
    df_ideam_grouped["nieve"] = pd.NA
    df_ideam_grouped["velocidad_viento"] = pd.NA
    df_ideam_grouped["rafaga_viento"] = pd.NA
    df_ideam_grouped["presion"] = pd.NA
    df_ideam_grouped["minutos_sol"] = pd.NA

    # source_id IDEAM
    df_ideam_grouped["source_id"] = 1

    
    # 3. Tranformar meteostat
    df_meteostat["date"] = pd.to_datetime(df_meteostat["date"])
    df_meteostat["city"] = df_meteostat["city"].str.replace("_", " ", regex=False)

    df_meteostat = df_meteostat.rename(columns={
        "tavg": "temperatura_promedio",
        "tmin": "temperatura_minima",
        "tmax": "temperatura_maxima",
        "prcp": "precipitacion",
        "snow": "nieve",
        "wspd": "velocidad_viento",
        "wpgt": "rafaga_viento",
        "pres": "presion",
        "tsun": "minutos_sol"
    })

    columnas_comunes = [
        "city",
        "date",
        "temperatura_promedio",
        "temperatura_minima",
        "temperatura_maxima",
        "precipitacion",
        "nieve",
        "velocidad_viento",
        "rafaga_viento",
        "presion",
        "minutos_sol"
    ]

    for col in columnas_comunes:
        if col not in df_meteostat.columns:
            df_meteostat[col] = pd.NA

    df_meteostat = df_meteostat[columnas_comunes]

    # source_id Meteostat
    df_meteostat["source_id"] = 2

    # 4. Integrar fuentes 
    df_integrado = pd.concat([df_ideam_grouped, df_meteostat], ignore_index=True)

    # 5. CREAR DIMENSIONES
    # dim_city
    dim_city = df_integrado[["city"]].drop_duplicates().reset_index(drop=True)
    dim_city["city_id"] = dim_city.index + 1
    dim_city = dim_city[["city_id", "city"]]

    # dim_date
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

    # dim_source
    dim_source = pd.DataFrame({
        "source_id": [1, 2],
        "nombre_fuente": ["IDEAM", "Meteostat"],
        "tipo_fuente": ["CSV", "API"]
    })

    # 6. FACT TABLE
    fact_climate_daily = df_integrado.merge(dim_city, on="city", how="left")
    fact_climate_daily = fact_climate_daily.merge(dim_date, on="date", how="left")

    fact_climate_daily = fact_climate_daily[[
        "city_id",
        "date_id",
        "source_id",
        "temperatura_promedio",
        "temperatura_minima",
        "temperatura_maxima",
        "precipitacion",
        "nieve",
        "velocidad_viento",
        "rafaga_viento",
        "presion",
        "minutos_sol"
    ]]

    print("Transformacion e integracion completadas")
    print("dim_city:", dim_city.shape)
    print("dim_date:", dim_date.shape)
    print("dim_source:", dim_source.shape)
    print("fact_climate_daily:", fact_climate_daily.shape)

    # eliminar filas con inconsistencias logicas en temperatura
    fact_climate_daily = fact_climate_daily[
        (fact_climate_daily["temperatura_promedio"] >= fact_climate_daily["temperatura_minima"]) &
        (fact_climate_daily["temperatura_maxima"] >= fact_climate_daily["temperatura_promedio"])
    ]
    # guardar fact para validacion
    os.makedirs("data/processed", exist_ok=True)
    fact_climate_daily.to_csv("data/processed/fact_climate_daily.csv", index=False)

    return dim_city, dim_date, dim_source, fact_climate_daily