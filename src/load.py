import pandas as pd
from sqlalchemy import create_engine, text


def load_to_warehouse(dim_city, dim_date, dim_source, fact_climate_daily):

    print("Iniciando carga al Data Warehouse...")

    db_url = "mysql+pymysql://root:root@localhost:3306/climate_dw"

    try:
        engine = create_engine(db_url)

        # limpiar datos sin borrar las tablas
        with engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.execute(text("TRUNCATE TABLE fact_climate_daily"))
            conn.execute(text("TRUNCATE TABLE dim_city"))
            conn.execute(text("TRUNCATE TABLE dim_date"))
            conn.execute(text("TRUNCATE TABLE dim_source"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        dim_date["date"] = pd.to_datetime(dim_date["date"]).dt.date

        print("Cargando tabla: dim_city...")
        dim_city.to_sql("dim_city", con=engine, if_exists="append", index=False)

        print("Cargando tabla: dim_date...")
        dim_date.to_sql("dim_date", con=engine, if_exists="append", index=False)

        print("Cargando tabla: dim_source...")
        dim_source.to_sql("dim_source", con=engine, if_exists="append", index=False)

        print("Cargando tabla: fact_climate_daily...")
        fact_climate_daily.to_sql("fact_climate_daily", con=engine, if_exists="append", index=False)

        print("Carga completada con éxito.")

    except Exception as e:
        print(f"Error durante la carga: {e}")
        raise