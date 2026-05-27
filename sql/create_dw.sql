CREATE DATABASE climate_dw;

USE climate_dw;

DROP TABLE IF EXISTS fact_climate_daily;
DROP TABLE IF EXISTS dim_city;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_source;

CREATE TABLE dim_city (
    city_id INT PRIMARY KEY,
    city VARCHAR(150) NOT NULL
);

CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date DATE NOT NULL,
    anio INT,
    mes INT,
    dia INT,
    semana INT,
    trimestre INT,
    es_fin_de_semana BOOLEAN
);

CREATE TABLE dim_source (
    source_id INT PRIMARY KEY,
    nombre_fuente VARCHAR(100) NOT NULL,
    tipo_fuente VARCHAR(50) NOT NULL
);

CREATE TABLE fact_climate_daily (
    city_id INT NOT NULL,
    date_id INT NOT NULL,
    source_id INT NOT NULL,

    temperatura_promedio FLOAT NOT NULL,
    temperatura_minima FLOAT NOT NULL,
    temperatura_maxima FLOAT NOT NULL,

    amplitud_termica FLOAT NOT NULL,
    evento_calor_extremo INT NOT NULL,

    PRIMARY KEY (city_id, date_id, source_id),

    FOREIGN KEY (city_id) REFERENCES dim_city(city_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);